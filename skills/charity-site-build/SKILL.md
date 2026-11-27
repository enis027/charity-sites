---
name: charity-site-build
description: Builds an accessible, fast, static website for a charity, nonprofit or association from its own audited content — derives a WCAG-compliant palette from the logo, writes a sourced site.json, renders every page in the organisation's language (including right-to-left scripts), and enforces quality gates for contrast, labels, links, card-data safety and invented content. Use when rebuilding or redesigning a nonprofit website after charity-site-audit, or when editing a site produced by this template.
---

# Charity site build

## Overview

Turns the audit into a finished static website: plain HTML, CSS and a few kilobytes of JavaScript that run on any host or straight from a folder. Everything visible comes from two places only: the organisation's own content (in `site.json`, each section with its source URL) and interface labels for the site's language (`template/i18n/<lang>.json`). The template handles layout, accessibility, RTL, palette and the hand-off to a payment provider; your job is the content decisions.

Read before building: [charity-ux-principles.md](references/charity-ux-principles.md) (what works for charities and why), [content-integrity.md](../charity-site-audit/references/content-integrity.md) (what you may and may not write).

## When to Use

- Step 2 of `/charity-site`, after `audit/` exists.
- Editing or extending a site built with this template.

Not for: sites that need logins, member databases, online shops or a CMS. Say so and stop.

## Process

### 1. Plan the information architecture

Use [information-architecture.md](references/information-architecture.md). Decide the pages (at minimum: home, donate, about, help/support, one news article, contact) and the top navigation (≤ 6 items + Donate). Write the old → new navigation map into `audit/CONTENT-INVENTORY.md`. Every existing page must stay reachable: either rebuilt, merged, or linked from a hub to its old URL.

### 2. Prepare assets

- Logo: copy the organisation's original logo file (SVG preferred) to `site/assets/`. Never redraw or "improve" it. Create a single-colour white version for dark backgrounds only if the logo has no reverse version: for SVG, replace fills with white; for raster logos, skip the reverse and let the footer show the name in text.
- Brand colours: take them from the logo's fills (SVG) and the old CSS's most-used colours (`inventory.json → css_colors`). Put 2–4 of them in `brand.colors`. `palette.py` assigns primary/accent/donate roles and adjusts lightness until every pair passes WCAG AA. Override a role (`brand.primary`, `brand.donate`) only if the automatic choice is clearly off-brand, then rebuild and re-check.
- Photos: follow [photography.md](../charity-site-audit/references/photography.md). Resize to the needed size (`python3 scripts/prep_images.py`), never beyond the source.

### 3. Write `site.json`

Schema and every section type: [site-schema.md](references/site-schema.md). Start from `examples/fixture-en/site.json` for structure only — its text is fictional and must not leak into a real site.

Rules that matter most:
- `"preview": true` until the organisation approves. It adds the "unofficial preview" banner, `noindex`, and `robots.txt` disallow.
- Every content section has `"src"` with the source URL(s). `check.py` fails without it.
- Hero: overline + H1 + lead must answer *who they are, whom they serve, what they do* using the organisation's own statements. Primary CTA = Donate, secondary = help/support.
- Use real dates (ISO `YYYY-MM-DD`) for news; keep old items labelled with their dates.
- Anything you could not source: leave it out and add `"needs_confirmation": "question"` on the nearest object.
- Payment: fill `payment` from the audit's detected provider (see the handoff skill's [payment-providers.md](../charity-site-handoff/references/payment-providers.md)). Leave `url` empty if you don't have the organisation's link yet — the preview shows the flow with a notice; the production build hides card giving until it is connected.

### 4. Language

If `template/i18n/<lang>.json` does not exist, translate `en.json` into `site/i18n/<lang>.json` (same keys, natural phrasing, the organisation's own terms for "donate"/"member" where it uses them) and set `"_meta": {"reviewed": false}`. Month names go in `months`. Fonts and text direction are chosen automatically from the language ([i18n.md](references/i18n.md)).

### 5. Build and check

```bash
python3 <skill-dir>/template/build.py work/example-org/site/site.json --out work/example-org/dist
python3 <skill-dir>/scripts/check.py work/example-org/dist --site work/example-org/site/site.json
```

Fix every error. Report every warning to the user. Contrast failures abort the build: adjust `brand` rather than passing `--allow-contrast-fail`.

### 6. Look at it

```bash
python3 <skill-dir>/scripts/screenshots.py work/example-org/dist --out work/example-org/screens
```

This renders every page at 390, 768 and 1440 px (headless Chrome/Chromium/Edge). Open the images and go through [visual-qa.md](references/visual-qa.md). For the mobile pass, also check in a real mobile viewport (browser tool device emulation) because desktop Chrome headless has a minimum window width.

### 7. Independent content review

Ask the `content-integrity-reviewer` agent to compare `site.json` against `audit/pages/` and report anything invented, changed in meaning, re-dated or unsourced. Fix what it finds, rebuild, re-check.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "A short impact stat in the hero will convert better." | Invented numbers are the fastest way to destroy a charity's credibility. Use their documented facts or none. |
| "The custom template will look more unique than this one." | The template encodes accessibility, RTL and payment safety. Change tokens, content and section rhythm; don't fork the components. |
| "I'll leave the card fields; it's just a mock." | Card fields on the charity's page put them in PCI scope and train donors to type cards into it. The template refuses them. |
| "Lighthouse is green, so it's accessible." | Automated checks catch a third of issues. Do the manual checklist. |

## Red Flags

- Text in `site.json` you cannot point to in `audit/pages/`.
- The organisation's name or legal type differs from the audit.
- A donate colour used for anything other than Donate.
- Three identical card grids in a row; a carousel; a hero with only a slogan.
- `check.py` run without `--site` (skips the source check).

## Verification

- [ ] `build.py` succeeds with no contrast failures
- [ ] `check.py --site` reports 0 errors; warnings explained to the user
- [ ] Screenshots at 390/768/1440 reviewed against visual-qa.md; first screen states who/whom/what + Donate
- [ ] content-integrity-reviewer found nothing invented (or its findings are fixed)
- [ ] `preview` is still `true`
