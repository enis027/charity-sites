#!/usr/bin/env python3
"""Quality gates for a built charity-sites website.

Usage:
  python3 check.py dist/ [--site site.json] [--json]

Exits 1 when any error is found. Warnings never fail the build but must be
reported to the user. Standard library only; this does not replace a manual
screen-reader and keyboard pass (see the build skill's accessibility checklist).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

PLACEHOLDER = re.compile(r"lorem ipsum|dolor sit amet|\bTODO\b|\bFIXME\b|\bTBD\b|\bXXX\b|\{[a-z_]+\}|\[\[|\]\]", re.I)
TRANSLATION_KEY = re.compile(r"\b[a-z]{2,}\.[a-z_]{2,}\.[a-z_]{2,}\b")
CARD_HINTS = re.compile(r"cc-(number|csc|exp)|card.?number|cvv|cvc|kart.?numaras|security.?code", re.I)
SKIP_INPUT_TYPES = {"hidden", "submit", "button", "reset", "image"}
IMG_BUDGET = 400_000
PAGE_BUDGET = 1_500_000


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.html_attrs = {}
        self.h = []
        self.imgs = []
        self.links = []
        self.ids = []
        self.labels_for = set()
        self.controls = []
        self.forms = []
        self.text = []
        self.stack = []
        self.metas = []
        self.label_depth = 0
        self.empty_interactive = []
        self._interactive = []
        self.scripts = []
        self.styles = []
        self.hidden_depth = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "html":
            self.html_attrs = a
        elif re.fullmatch(r"h[1-6]", tag):
            self.h.append(int(tag[1]))
        elif tag == "img":
            self.imgs.append(a)
            if self._interactive and a.get("alt"):
                self._interactive[-1][1].append("img")
        elif tag == "a":
            self.links.append(a)
        elif tag == "label":
            self.label_depth += 1
            if a.get("for"):
                self.labels_for.add(a["for"])
        elif tag in ("input", "select", "textarea"):
            if a.get("type", "text") not in SKIP_INPUT_TYPES:
                self.controls.append((tag, a, self.label_depth > 0))
        elif tag == "form":
            self.forms.append(a)
        elif tag == "meta":
            self.metas.append(a)
        elif tag == "script" and a.get("src"):
            self.scripts.append(a["src"])
        elif tag == "link" and a.get("rel") == "stylesheet":
            self.styles.append(a.get("href", ""))
        if tag in ("a", "button"):
            self._interactive.append((tag, [], a))
            if a.get("aria-label"):
                self._interactive[-1][1].append("aria")
        if tag == "svg" and a.get("aria-label") and self._interactive:
            self._interactive[-1][1].append("svg")
        if a.get("class") and "visually-hidden" in a.get("class", "") and self._interactive:
            self._interactive[-1][1].append("vh")
        self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag == "label":
            self.label_depth = max(0, self.label_depth - 1)
        if tag in ("a", "button") and self._interactive:
            t, content, attrs = self._interactive.pop()
            if not content:
                self.empty_interactive.append((t, attrs))
        if self.stack:
            self.stack.pop()

    def handle_data(self, data):
        if self.stack and self.stack[-1] in ("script", "style"):
            return
        s = data.strip()
        if s:
            self.text.append(s)
            if self._interactive:
                self._interactive[-1][1].append("text")


def check_dist(dist: Path, site: dict | None) -> tuple[list[str], list[str]]:
    errors, warns = [], []
    pages = sorted(dist.glob("*.html"))
    if not pages:
        return [f"no HTML files in {dist}"], []
    parsed = {}
    for p in pages:
        pg = Page()
        pg.feed(p.read_text(encoding="utf-8"))
        parsed[p.name] = pg
    all_ids = {name: set(pg.ids) for name, pg in parsed.items()}
    preview = bool(site and site.get("preview"))

    for name, pg in parsed.items():
        where = name
        if not pg.html_attrs.get("lang"):
            errors.append(f"{where}: <html> has no lang attribute")
        if pg.h.count(1) != 1:
            errors.append(f"{where}: expected exactly one <h1>, found {pg.h.count(1)}")
        prev = 0
        for lvl in pg.h:
            if prev and lvl > prev + 1:
                warns.append(f"{where}: heading level jumps from h{prev} to h{lvl}")
                break
            prev = lvl
        dupes = {i for i in pg.ids if pg.ids.count(i) > 1}
        if dupes:
            errors.append(f"{where}: duplicate id(s): {', '.join(sorted(dupes))}")
        if not any(m.get("name") == "viewport" for m in pg.metas):
            errors.append(f"{where}: missing viewport meta")
        if not any(m.get("name") == "description" and m.get("content") for m in pg.metas) and name != "404.html":
            warns.append(f"{where}: empty meta description")
        noindex = any(m.get("name") == "robots" and "noindex" in m.get("content", "") for m in pg.metas)
        if preview and not noindex:
            errors.append(f"{where}: preview build must carry <meta name=robots content=noindex>")
        if site is not None and not preview and noindex:
            errors.append(f"{where}: production build still has noindex")

        for img in pg.imgs:
            if "alt" not in img:
                errors.append(f"{where}: <img src={img.get('src')}> has no alt attribute (use alt=\"\" for decorative images)")
            if not (img.get("width") and img.get("height")):
                warns.append(f"{where}: <img src={img.get('src')}> lacks width/height (layout shift)")
            src = img.get("src", "")
            if src and not urlparse(src).scheme:
                f = dist / unquote(src.split("#")[0].split("?")[0])
                if not f.exists():
                    errors.append(f"{where}: image not found: {src}")
                elif f.stat().st_size > IMG_BUDGET:
                    warns.append(f"{where}: {src} is {f.stat().st_size // 1024} KB (budget {IMG_BUDGET // 1024} KB) — resize/compress")

        for link in pg.links:
            href = link.get("href", "")
            if not href:
                errors.append(f"{where}: <a> without href")
                continue
            u = urlparse(href)
            if u.scheme in ("http", "https", "mailto", "tel"):
                continue
            path, _, frag = href.partition("#")
            target = name if not path else unquote(path)
            tfile = dist / target
            if not tfile.exists():
                errors.append(f"{where}: broken internal link {href}")
            elif frag and target in all_ids and frag not in all_ids[target] and frag != "main":
                errors.append(f"{where}: link {href} points to a missing anchor")

        for tag, a, wrapped in pg.controls:
            cid = a.get("id")
            if not (wrapped or (cid and cid in pg.labels_for) or a.get("aria-label") or a.get("aria-labelledby")):
                errors.append(f"{where}: <{tag} name={a.get('name')}> has no label")
            blob = " ".join(str(v) for v in a.values())
            if CARD_HINTS.search(blob):
                errors.append(f"{where}: card-data field detected ({a.get('name')}). Card details must be entered on the payment provider's hosted page, never on this site (PCI DSS SAQ A).")

        for f in pg.forms:
            if f.get("action", "#") in ("", "#") and f.get("data-demo") != "true" and f.get("id") != "donation-form":
                errors.append(f"{where}: form without a working action (connect a form service or remove it)")
            if not preview and f.get("data-demo") == "true":
                errors.append(f"{where}: production build contains a demo form (form service or payment link not configured)")

        for t, attrs in pg.empty_interactive:
            errors.append(f"{where}: <{t}> with no accessible name ({attrs.get('href') or attrs.get('class') or ''})")

        text = " ".join(pg.text)
        for m in PLACEHOLDER.finditer(text):
            errors.append(f"{where}: placeholder or template text found: “{m.group(0)}”")
        for m in TRANSLATION_KEY.finditer(text):
            if not re.search(r"@|www\.|\.(org|com|net|gov|edu)", text[max(0, m.start() - 30):m.end() + 5]):
                warns.append(f"{where}: possible untranslated key “{m.group(0)}”")

        size = (dist / name).stat().st_size
        for s in pg.styles + pg.scripts:
            if s and not urlparse(s).scheme and (dist / s).exists():
                size += (dist / s).stat().st_size
        for img in pg.imgs:
            s = img.get("src", "")
            if s and not urlparse(s).scheme and (dist / s).exists() and img.get("loading") != "lazy":
                size += (dist / s).stat().st_size
        if size > PAGE_BUDGET:
            warns.append(f"{where}: initial page weight ≈ {size // 1024} KB (budget {PAGE_BUDGET // 1024} KB, fonts excluded)")

    report = dist / ".build-report.json"
    if report.exists():
        r = json.loads(report.read_text(encoding="utf-8"))
        for c in r.get("contrast", []):
            if not c["ok"]:
                errors.append(f"contrast: {c['fg']} on {c['bg']} = {c['ratio']} < {c['min']} ({c['purpose']})")
    else:
        warns.append("no .build-report.json (was this built with build.py?)")

    if site is not None:
        errors += check_sources(site)
    return errors, warns


FUNCTIONAL = {"contact"}


def check_sources(site: dict) -> list[str]:
    """Every content-bearing block must say where its text came from."""
    errs = []
    for p in site.get("pages", []):
        if p.get("layout") == "article" and not p.get("src"):
            errs.append(f"site.json page {p['slug']}: article page has no 'src'")
        for i, s in enumerate(p.get("sections", [])):
            if s.get("type") not in FUNCTIONAL and not s.get("src"):
                errs.append(f"site.json page {p['slug']} section {i} ({s.get('type')}): missing 'src' (source URL of this content)")
    for key in ("contact", "bank"):
        if site.get(key) and not site[key].get("src"):
            errs.append(f"site.json {key}: missing 'src'")
    return errs


def open_questions(site: dict) -> list[str]:
    out = []

    def walk(node, path):
        if isinstance(node, dict):
            if node.get("needs_confirmation"):
                out.append(f"{path}: {node.get('needs_confirmation') if isinstance(node.get('needs_confirmation'), str) else 'confirm'}")
            for k, v in node.items():
                walk(v, f"{path}.{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]")
    walk(site, "site")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("dist", type=Path)
    ap.add_argument("--site", type=Path)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    site = json.loads(a.site.read_text(encoding="utf-8")) if a.site else None
    errors, warns = check_dist(a.dist, site)
    oq = open_questions(site) if site else []
    if a.json:
        print(json.dumps({"errors": errors, "warnings": warns, "open_questions": oq}, ensure_ascii=False, indent=2))
    else:
        for e in errors:
            print("ERROR  ", e)
        for w in warns:
            print("WARN   ", w)
        for q in oq:
            print("CONFIRM", q)
        print(f"\n{len(errors)} error(s), {len(warns)} warning(s), {len(oq)} item(s) needing organisation confirmation")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
