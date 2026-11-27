# Contributing

Thank you for helping charities get better websites.

## Ground rules

- Every change must keep the principles in the README intact: no invented content, no card data on the site, accessible by default, humans send email.
- Standard library Python only in scripts and the template. The organisation must be able to rebuild with nothing but Python installed.
- No tracking, analytics, cookies or third-party scripts in the template.

## Before opening a pull request

```bash
python3 scripts/validate_skills.py
python3 -m unittest discover -s tests -t . -v
python3 skills/charity-site-build/template/build.py examples/fixture-en/site.json --out /tmp/fx-en
python3 skills/charity-site-build/scripts/check.py /tmp/fx-en --site examples/fixture-en/site.json
```

If you change anything visual, attach before/after screenshots at 390 and 1440 px (`skills/charity-site-build/scripts/screenshots.py`) and check the RTL fixture too.

## Adding a language

1. Copy `skills/charity-site-build/template/i18n/en.json` to `<lang>.json` (ISO 639-1 code).
2. Translate every value; keep keys and `{placeholders}`; add `months`.
3. Write error messages in the GOV.UK style for your language: say what to do, no blame, no "please/sorry/invalid".
4. Set `_meta.reviewed` to `true` only if a native speaker reviewed it.
5. If the script needs a different font, add it to `FONT_PRESETS` in `template/build.py`.

## Adding a payment-provider recipe

Add it to `skills/charity-site-handoff/references/payment-providers.md` with: the dashboard steps, whether it supports an amount prefill parameter (with a link to the provider's documentation), fixed vs variable amounts, and anything the organisation must check (eligibility for donations, fees). Add its detection signature to `PAYMENT_SIGNATURES` in `skills/charity-site-audit/scripts/crawl.py`. Do not claim behaviour you have not verified in the provider's documentation.

## Adding a section type

1. Implement `s_<type>(site, sec)` in `template/render.py` and register it in `SECTIONS`.
2. Use only tokens from `tokens.css` and logical CSS properties.
3. Add it to the fixture, to `references/site-schema.md`, and test it in LTR and RTL.

## Reporting a problem with a generated site

Open an issue with the check output, screenshots and the relevant `site.json` excerpt. Do not include personal data from an organisation's site.
