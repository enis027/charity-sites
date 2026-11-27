#!/usr/bin/env python3
"""Validate skill and agent files: frontmatter, names, description length, relative links."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALLOWED = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
errors = []


def frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        errors.append(f"{path}: missing YAML frontmatter")
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm


for skill in sorted((ROOT / "skills").iterdir()):
    md = skill / "SKILL.md"
    if not md.exists():
        errors.append(f"{skill}: no SKILL.md")
        continue
    fm = frontmatter(md)
    if fm.get("name") != skill.name:
        errors.append(f"{md}: name '{fm.get('name')}' must equal directory '{skill.name}'")
    desc = fm.get("description", "")
    if not desc or len(desc) > 1024 or "Use when" not in desc:
        errors.append(f"{md}: description must exist, be ≤ 1024 chars and contain 'Use when'")
    extra = set(fm) - ALLOWED
    if extra:
        errors.append(f"{md}: unsupported frontmatter keys {sorted(extra)}")
    for f in [md, *skill.rglob("references/*.md")]:
        for link in re.findall(r"\]\(([^)#\s]+\.md)(?:#[^)]*)?\)", f.read_text(encoding="utf-8")):
            if not link.startswith("http") and not (f.parent / link).resolve().exists():
                errors.append(f"{f}: broken link {link}")

for agent in (ROOT / "agents").glob("*.md"):
    fm = frontmatter(agent)
    if fm.get("name") != agent.stem or not fm.get("description"):
        errors.append(f"{agent}: name must equal file name and description is required")

for cmd in (ROOT / "commands").glob("*.md"):
    if not frontmatter(cmd).get("description"):
        errors.append(f"{cmd}: description is required")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print("skills, agents and commands OK")
