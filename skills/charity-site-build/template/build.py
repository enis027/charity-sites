#!/usr/bin/env python3
"""Build a static charity website from site.json.

Usage:
  python3 build.py path/to/site.json [--out dist] [--allow-contrast-fail]

Standard library only. Output is plain HTML/CSS/JS that runs on any static host
or straight from the file system.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from urllib.parse import quote_plus

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import palette  # noqa: E402
import render  # noqa: E402

LATIN = ("Source Serif 4", "Source Sans 3")
FONT_PRESETS = {
    # language prefix -> (heading family, body family). All support the script natively.
    "ar": ("Noto Naskh Arabic", "Noto Sans Arabic"), "fa": ("Noto Naskh Arabic", "Noto Sans Arabic"),
    "ur": ("Noto Nastaliq Urdu", "Noto Sans Arabic"), "he": ("Noto Serif Hebrew", "Noto Sans Hebrew"),
    "hi": ("Noto Serif Devanagari", "Noto Sans Devanagari"), "mr": ("Noto Serif Devanagari", "Noto Sans Devanagari"),
    "ne": ("Noto Serif Devanagari", "Noto Sans Devanagari"), "bn": ("Noto Serif Bengali", "Noto Sans Bengali"),
    "ta": ("Noto Serif Tamil", "Noto Sans Tamil"), "te": ("Noto Serif Telugu", "Noto Sans Telugu"),
    "th": ("Noto Serif Thai", "Noto Sans Thai"), "ja": ("Noto Serif JP", "Noto Sans JP"),
    "zh": ("Noto Serif SC", "Noto Sans SC"), "ko": ("Noto Serif KR", "Noto Sans KR"),
    "ka": ("Noto Serif Georgian", "Noto Sans Georgian"), "hy": ("Noto Serif Armenian", "Noto Sans Armenian"),
    "am": ("Noto Serif Ethiopic", "Noto Sans Ethiopic"), "km": ("Noto Serif Khmer", "Noto Sans Khmer"),
}
RTL = {"ar", "fa", "ur", "he", "ps", "sd", "yi", "dv", "ug", "ckb"}
REQUIRED = ["lang", "org", "brand", "nav", "pages", "donate_href"]


def fonts_for(site: dict) -> dict:
    lang = site["lang"].split("-")[0].lower()
    f = dict(site.get("fonts") or {})
    heading, body = FONT_PRESETS.get(lang, LATIN)
    heading = f.get("heading", heading)
    body = f.get("body", body)
    serif_fallback = "Georgia, 'Times New Roman', serif"
    sans_fallback = "system-ui, -apple-system, 'Segoe UI', Roboto, Arial, sans-serif"
    out = {
        "heading": heading, "body": body,
        "heading_stack": f"'{heading}', {serif_fallback if 'Serif' in heading or 'Naskh' in heading else sans_fallback}",
        "body_stack": f"'{body}', {sans_fallback}",
    }
    if f.get("self_hosted"):
        out["google_css"] = ""
        out["self_css"] = "fonts/fonts.css"
    else:
        fam_h = f"family={quote_plus(heading)}:wght@600"
        fam_b = (f"family={quote_plus(body)}:ital,wght@0,400;0,600;0,700;1,400" if body in LATIN or body == "Source Sans 3"
                 else f"family={quote_plus(body)}:wght@400;600;700")
        out["google_css"] = f"https://fonts.googleapis.com/css2?{fam_h}&{fam_b}&display=swap"
    return out


def load_ui(site: dict, site_dir: Path) -> dict:
    lang = site["lang"].split("-")[0].lower()
    base = json.loads((HERE / "i18n" / "en.json").read_text(encoding="utf-8"))
    candidates = [site_dir / "i18n" / f"{lang}.json", HERE / "i18n" / f"{lang}.json"]
    found = next((p for p in candidates if p.exists()), None)
    if not found and lang != "en":
        raise SystemExit(f"No interface strings for '{lang}'. Translate template/i18n/en.json into "
                         f"{site_dir / 'i18n' / (lang + '.json')} (same keys) and rebuild.")
    ui = dict(base)
    if found:
        loc = json.loads(found.read_text(encoding="utf-8"))
        missing = sorted(set(base) - set(loc))
        if missing:
            raise SystemExit(f"{found} is missing keys: {', '.join(missing)}")
        ui.update(loc)
    ui.update(site.get("ui", {}))
    return ui


def validate(site: dict) -> list[str]:
    errs = [f"missing top-level key: {k}" for k in REQUIRED if k not in site]
    slugs = [p.get("slug") for p in site.get("pages", [])]
    if "index" not in slugs:
        errs.append("pages must include slug 'index'")
    if len(slugs) != len(set(slugs)):
        errs.append("duplicate page slugs")
    for p in site.get("pages", []):
        for s in p.get("sections", []):
            if s.get("type") not in render.SECTIONS:
                errs.append(f"page {p.get('slug')}: unknown section type {s.get('type')!r} (known: {', '.join(render.SECTIONS)})")
    return errs


def build(site_path: Path, out: Path, allow_contrast_fail: bool = False) -> dict:
    site_dir = site_path.parent
    site = json.loads(site_path.read_text(encoding="utf-8"))
    errs = validate(site)
    if errs:
        raise SystemExit("site.json invalid:\n  - " + "\n  - ".join(errs))
    lang = site["lang"].split("-")[0].lower()
    site.setdefault("dir", "rtl" if lang in RTL else "ltr")
    site["ui"] = load_ui(site, site_dir)
    site["months"] = site["ui"].get("months")
    site["fonts"] = fonts_for(site)
    site["org"].setdefault("short_name", site["org"]["name"])

    pal = palette.build_palette(site["brand"])
    pal.update({k: v for k, v in site["brand"].get("overrides", {}).items()})
    contrast = palette.audit(pal)
    failures = [c for c in contrast if not c["ok"]]
    if failures and not allow_contrast_fail:
        lines = [f'{c["fg"]} on {c["bg"]}: {c["ratio"]} < {c["min"]} ({c["purpose"]})' for c in failures]
        raise SystemExit("Colour contrast failures:\n  - " + "\n  - ".join(lines))

    if out.exists():
        shutil.rmtree(out)
    (out / "css").mkdir(parents=True)
    shutil.copytree(HERE / "static" / "js", out / "js")
    shutil.copy(HERE / "static" / "css" / "styles.css", out / "css" / "styles.css")
    (out / "css" / "tokens.css").write_text(palette.tokens_css(pal, site["fonts"]), encoding="utf-8")
    if (site_dir / "assets").exists():
        shutil.copytree(site_dir / "assets", out / "assets")
    if site["fonts"].get("google_css") == "" and (site_dir / "fonts").exists():
        shutil.copytree(site_dir / "fonts", out / "fonts")

    pages = []
    for page in site["pages"]:
        name = "index.html" if page["slug"] == "index" else f'{page["slug"]}.html'
        (out / name).write_text(render.render_page(site, page), encoding="utf-8")
        pages.append(name)
    (out / "404.html").write_text(render.render_404(site), encoding="utf-8")
    if site.get("preview"):
        (out / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    report = {"pages": pages, "palette": pal, "contrast": contrast, "fonts": site["fonts"], "preview": bool(site.get("preview"))}
    (out / ".build-report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("site", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--allow-contrast-fail", action="store_true")
    a = ap.parse_args()
    out = a.out or a.site.parent / "dist"
    r = build(a.site.resolve(), out.resolve(), a.allow_contrast_fail)
    print(f"Built {len(r['pages'])} pages into {out}")
    for c in r["contrast"]:
        print(("  ok  " if c["ok"] else "  FAIL"), f'{c["ratio"]:>5} >= {c["min"]:<3} {c["purpose"]}')


if __name__ == "__main__":
    main()
