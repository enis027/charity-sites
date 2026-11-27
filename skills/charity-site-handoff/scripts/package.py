#!/usr/bin/env python3
"""Assemble the deliverable for the organisation.

Usage:
  python3 package.py work/example-org --name example-org-website [--zip]

Expects in the work folder:
  site/site.json (+ site/assets, optional site/i18n, site/fonts)
  handoff/README.md          — written in the organisation's language (required)
  handoff/OPEN-QUESTIONS.md  — in the organisation's language (required)
  handoff/EMAIL-DRAFT.md     — for the operator, NOT packaged

Produces work/<name>/:
  site/              the built website — upload this folder to any static host
  source/            site.json, assets, translations (edit these)
  tools/             build.py, check.py and the template (rebuild with one command)
  README.md          how to publish, edit and connect payments (organisation's language)
  OPEN-QUESTIONS.md  what the organisation must confirm
  SOURCES.md         where every section's content came from
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD_SKILL = HERE.parent.parent / "charity-site-build"


def sources_md(site: dict) -> str:
    rows = ["| Page | Section | Heading | Source |", "|---|---|---|---|"]
    for p in site["pages"]:
        if p.get("layout") == "article":
            rows.append(f"| {p['slug']} | article | {p['header'].get('title', '')} | {p.get('src', '')} |")
        if p.get("layout") == "donate":
            rows.append(f"| {p['slug']} | donation | {p['header'].get('title', '')} | payment + bank settings (see below) |")
        for i, s in enumerate(p.get("sections", [])):
            items = s.get("items") if isinstance(s.get("items"), list) else []
            head = s.get("title") or s.get("quote") or (items[0].get("title", "") if items and isinstance(items[0], dict) else "")
            rows.append(f"| {p['slug']} | {i + 1}. {s['type']} | {str(head)[:70]} | {s.get('src', '')} |")
    extra = []
    for key in ("contact", "bank"):
        if site.get(key):
            extra.append(f"- `{key}`: {site[key].get('src', 'missing')}")
    return ("# Content sources\n\nEvery section of the new site and the page its text came from.\n\n" + "\n".join(rows) +
            "\n\n## Settings\n\n" + "\n".join(extra) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("work", type=Path)
    ap.add_argument("--name", required=True)
    ap.add_argument("--zip", action="store_true")
    a = ap.parse_args()
    work = a.work.resolve()
    site_dir = work / "site"
    handoff = work / "handoff"
    for req in (site_dir / "site.json", handoff / "README.md", handoff / "OPEN-QUESTIONS.md"):
        if not req.exists():
            sys.exit(f"missing {req} — write it first (see the handoff skill)")
    out = work / a.name
    if out.exists():
        shutil.rmtree(out)
    (out / "tools").mkdir(parents=True)

    shutil.copytree(BUILD_SKILL / "template", out / "tools" / "template", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy(BUILD_SKILL / "scripts" / "check.py", out / "tools" / "check.py")
    (out / "tools" / "build.py").write_text(
        "#!/usr/bin/env python3\n# Rebuild the website: python3 tools/build.py\n"
        "import subprocess, sys\nfrom pathlib import Path\nroot = Path(__file__).resolve().parent.parent\n"
        "r = subprocess.run([sys.executable, str(root / 'tools/template/build.py'), str(root / 'source/site.json'), '--out', str(root / 'site')])\n"
        "if r.returncode == 0:\n    r = subprocess.run([sys.executable, str(root / 'tools/check.py'), str(root / 'site'), '--site', str(root / 'source/site.json')])\n"
        "sys.exit(r.returncode)\n", encoding="utf-8")

    shutil.copytree(site_dir, out / "source", ignore=shutil.ignore_patterns("dist", "__pycache__"))
    r = subprocess.run([sys.executable, str(out / "tools" / "template" / "build.py"), str(out / "source" / "site.json"), "--out", str(out / "site")])
    if r.returncode:
        sys.exit("build failed")
    chk = subprocess.run([sys.executable, str(out / "tools" / "check.py"), str(out / "site"), "--site", str(out / "source" / "site.json")])
    (out / "site" / ".build-report.json").unlink(missing_ok=True)

    shutil.copy(handoff / "README.md", out / "README.md")
    shutil.copy(handoff / "OPEN-QUESTIONS.md", out / "OPEN-QUESTIONS.md")
    site = json.loads((out / "source" / "site.json").read_text(encoding="utf-8"))
    src = sources_md(site)
    if (handoff / "WORDING-CHANGES.md").exists():
        src += "\n" + (handoff / "WORDING-CHANGES.md").read_text(encoding="utf-8")
    (out / "SOURCES.md").write_text(src, encoding="utf-8")

    if a.zip:
        z = shutil.make_archive(str(out), "zip", root_dir=out.parent, base_dir=out.name)
        print(f"zip: {z}")
    print(f"deliverable: {out}")
    if chk.returncode:
        sys.exit("quality checks failed — fix before sending")


if __name__ == "__main__":
    main()
