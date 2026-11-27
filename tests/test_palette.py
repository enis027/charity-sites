import unittest

from tests.helpers import ROOT  # noqa: F401  (sets sys.path)
import palette

BRANDS = [
    ["#22274F", "#1D9AD7", "#DB372C"],   # navy / blue / red
    ["#F7C948", "#2BB673", "#00A3E0"],   # light yellow / green / cyan
    ["#E30613"],                          # single bright red
    ["#7A1FA2", "#FFB300"],               # purple / amber
    ["#000000", "#FFFFFF"],               # black and white
    ["#0B6E4F", "#F15A24"],               # green / orange
    ["#FFD1DC", "#B5EAD7"],               # pastels only
    [],                                   # nothing extracted
]


class PaletteTest(unittest.TestCase):
    def test_contrast_ratio_known_values(self):
        self.assertAlmostEqual(palette.contrast("#000000", "#FFFFFF"), 21.0, places=1)
        self.assertAlmostEqual(palette.contrast("#FFFFFF", "#FFFFFF"), 1.0, places=2)

    def test_every_brand_passes_every_required_pair(self):
        for colors in BRANDS:
            with self.subTest(colors=colors):
                p = palette.build_palette({"colors": colors})
                failures = [r for r in palette.audit(p) if not r["ok"]]
                self.assertEqual(failures, [], f"{colors}: {failures}")

    def test_donate_is_distinct_from_primary(self):
        for colors in BRANDS:
            with self.subTest(colors=colors):
                p = palette.build_palette({"colors": colors})
                self.assertNotEqual(p["brand-donate"], p["brand-primary"])

    def test_explicit_roles_are_respected_but_made_accessible(self):
        p = palette.build_palette({"colors": ["#123456"], "donate": "#FF8800"})
        self.assertGreaterEqual(palette.contrast("#FFFFFF", p["brand-donate"]), 4.5)

    def test_darken_until_keeps_already_dark_colours(self):
        self.assertEqual(palette.darken_until("#22274F", "#FFFFFF", 7.0), "#22274F")


if __name__ == "__main__":
    unittest.main()
