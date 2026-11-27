# charity-sites (repository instructions)

This file configures agents working on this repository itself. The reusable assets are the skills in `skills/`.

## Layout

- `skills/<name>/SKILL.md` — one skill per directory; frontmatter `name` equals the directory, `description` says what it does and "Use when…".
- Skill-specific scripts and references live inside the skill so each skill is self-contained when copied.
- `examples/` holds fictional fixtures only. Never commit real organisations' content or photos.

## Before committing

```bash
python3 scripts/validate_skills.py
python3 -m unittest discover -s tests -t . -v
```

## Rules

- Standard library Python only (template, scripts, tests).
- Do not weaken `check.py` gates or contrast targets to make something pass; fix the cause.
- Keep interface strings in `template/i18n/*.json`, never hard-coded in `render.py`.
- Payment code never collects card details.
