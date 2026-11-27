import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tests.helpers import ROOT
import build
import check

FIXTURES = ["fixture-en", "fixture-ar"]


class BuildTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def build(self, name, mutate=None, preview=None):
        src = ROOT / "examples" / name
        work = self.tmp / name
        shutil.copytree(src, work)
        site_path = work / "site.json"
        site = json.loads(site_path.read_text(encoding="utf-8"))
        if preview is not None:
            site["preview"] = preview
        if mutate:
            mutate(site)
        site_path.write_text(json.dumps(site, ensure_ascii=False), encoding="utf-8")
        out = work / "dist"
        build.build(site_path, out)
        return out, site

    def test_fixtures_build_and_pass_all_checks(self):
        for name in FIXTURES:
            with self.subTest(fixture=name):
                out, site = self.build(name)
                errors, warns = check.check_dist(out, site)
                self.assertEqual(errors, [])
                self.assertEqual(warns, [])

    def test_rtl_fixture_sets_direction_and_arabic_fonts(self):
        out, _ = self.build("fixture-ar")
        html = (out / "index.html").read_text(encoding="utf-8")
        self.assertIn('dir="rtl"', html)
        self.assertIn("Noto+Naskh+Arabic", html)

    def test_preview_marks_noindex_and_banner(self):
        out, _ = self.build("fixture-en")
        html = (out / "index.html").read_text(encoding="utf-8")
        self.assertIn('content="noindex, nofollow"', html)
        self.assertIn("preview-banner", html)
        self.assertTrue((out / "robots.txt").exists())

    def test_production_without_form_service_or_payment_hides_demo_forms(self):
        out, site = self.build("fixture-en", preview=False)
        donate = (out / "donate.html").read_text(encoding="utf-8")
        contact = (out / "contact.html").read_text(encoding="utf-8")
        self.assertNotIn('id="donation-form"', donate)   # no payment link → no card giving
        self.assertIn("bank-block", donate)               # bank transfer still offered
        self.assertNotIn('id="contact-form"', contact)
        errors, _ = check.check_dist(out, site)
        self.assertEqual(errors, [])

    def test_production_with_payment_link_renders_handoff(self):
        def connect(site):
            site["payment"]["url"] = "https://donate.stripe.com/test_123"
        out, site = self.build("fixture-en", mutate=connect, preview=False)
        donate = (out / "donate.html").read_text(encoding="utf-8")
        self.assertIn('data-url="https://donate.stripe.com/test_123"', donate)
        self.assertIn('data-amount-param="prefilled_amount"', donate)
        self.assertNotIn('data-demo="true"', donate.split('id="donation-form"')[1].split(">")[0])

    def test_fixed_amount_links_replace_presets_and_custom_field(self):
        def links(site):
            site["payment"] = {"provider": "paytr-link", "provider_name": "PayTR", "links_by_amount": {"100": "https://example.com/a", "250": "https://example.com/b"}}
        out, _ = self.build("fixture-en", mutate=links, preview=False)
        donate = (out / "donate.html").read_text(encoding="utf-8")
        self.assertIn('value="250"', donate)
        self.assertNotIn('id="custom-amount"', donate)

    def test_missing_source_fails_check(self):
        def drop_src(site):
            del site["pages"][0]["sections"][1]["src"]
        out, site = self.build("fixture-en", mutate=drop_src)
        errors, _ = check.check_dist(out, site)
        self.assertTrue(any("missing 'src'" in e for e in errors))

    def test_unknown_language_without_strings_is_refused(self):
        def swahili(site):
            site["lang"] = "sw"
        with self.assertRaises(SystemExit) as ctx:
            self.build("fixture-en", mutate=swahili)
        self.assertIn("Translate", str(ctx.exception))


class CheckNegativeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def page(self, body, head='<meta name="viewport" content="width=device-width"><meta name="description" content="x">'):
        (self.tmp / "index.html").write_text(f'<!DOCTYPE html><html lang="en"><head>{head}</head><body>{body}</body></html>', encoding="utf-8")
        return check.check_dist(self.tmp, None)

    def test_card_fields_are_rejected(self):
        errors, _ = self.page('<h1>Donate</h1><form action="https://x"><label for="c">Card</label><input id="c" name="card_number" autocomplete="cc-number"></form>')
        self.assertTrue(any("PCI" in e for e in errors))

    def test_missing_alt_and_label_and_h1(self):
        errors, _ = self.page('<img src="https://x/y.jpg"><input name="q">')
        joined = "\n".join(errors)
        self.assertIn("no alt", joined)
        self.assertIn("no label", joined)
        self.assertIn("exactly one <h1>", joined)

    def test_placeholder_and_broken_link(self):
        errors, warns = self.page('<h1>Hi</h1><p>Lorem ipsum dolor</p><p>site.bagis.title</p><a href="missing.html">x</a>')
        joined = "\n".join(errors + warns)
        self.assertIn("Lorem ipsum", joined)
        self.assertIn("site.bagis.title", joined)
        self.assertIn("broken internal link", joined)

    def test_empty_button_has_no_accessible_name(self):
        errors, _ = self.page('<h1>Hi</h1><button type="button"><svg aria-hidden="true"></svg></button>')
        self.assertTrue(any("no accessible name" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
