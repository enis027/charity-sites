---
name: charity-site-audit
description: Audits a charity, nonprofit, association or NGO website before a rebuild — crawls it politely, inventories every page, photo, colour, contact and bank detail, detects the payment provider in use, and lists broken pages, missing content and facts the organisation must confirm. Use when someone shares a charity's website URL and wants it improved, redesigned or rebuilt, or asks what is wrong with a nonprofit's site.
---

# Charity site audit

## Overview

A rebuild is only as honest as its inventory. This skill produces a complete, sourced record of what the organisation already publishes, so the build can present it better without inventing anything. Output lives in `audit/` next to the work folder and is the only content source the build skill may use.

## When to Use

- A user pastes a charity/nonprofit/association website and wants it rebuilt (this is step 1 of `/charity-site`).
- A user asks what is wrong with a nonprofit website, or which pages are broken.

Not for: commercial sites, sites behind a login, or crawling social networks.

## Process

### 1. Set up

- Create a work folder named after the domain, e.g. `work/dmdturkiye-org/`. Everything goes inside it.
- Note the operator's language (talk to them in it) and the site's language (the deliverable will use it).

### 2. Crawl

```bash
python3 <skill-dir>/scripts/crawl.py https://example.org --out work/example-org/audit --max-pages 80
```

The crawler respects robots.txt, waits between requests, identifies itself, crawls the start URL's language section first, downloads every image with real pixel dimensions, and writes:

- `audit/REPORT.md` — summary for humans (read this first)
- `audit/inventory.json` — everything, machine-readable
- `audit/pages/*.md` — clean text of each page with its source URL; `audit/boilerplate.md` holds menu/footer text repeated on every page
- `audit/images/` — the organisation's images

If `REPORT.md` says the page limit was reached and the queued URLs look important (news archive, guides), re-run with a higher `--max-pages`. If pages have almost no words, the site is probably rendered by JavaScript: read those pages with a browser tool instead and save their text into `audit/pages/` with a `source:` line.

### 3. Read everything that matters

Read `REPORT.md`, then every page file that holds real content. Also open linked PDFs that are reports, statutes or guides (titles and dates at minimum). Look at every candidate photo (see [photography.md](references/photography.md)).

### 4. Write the organisation brief

Create `audit/BRIEF.md` (English or the operator's language) with a source URL after every fact:

- **Identity**: official name exactly as published, legal type (association, foundation, charity, cooperative… — copy it, never upgrade it), founding year/place, registration numbers if published, languages, country, currency.
- **Purpose and activities**: the organisation's own statement of purpose, verbatim or near-verbatim, and the activities it says it carries out.
- **Audiences**: who it serves (patients, families, volunteers, donors, press) and what each needs from the site.
- **Giving today**: payment provider detected (see [payment-detection.md](references/payment-detection.md)), whether card fields sit on their own page, bank details (IBAN checksum result from the report), membership dues vs donations, any published refund/terms statements, preset amounts on the existing form (and whether they are consistent).
- **Trust material**: reports, filings, audits, governance, team, partners — each with its URL and date.
- **Contact**: address(es), phone(s), emails, social profiles (official profiles only, not share links), forms and where they post.
- **News and dates**: list news/announcements with their real publication dates. Mark anything older than two years as archive.

### 5. Write the gap list

Create `audit/GAPS.md`:
- Broken or empty pages (404, timeouts, "under construction", pages with a title and no body).
- Problems on live pages: untranslated keys (e.g. `site.bagis.title`), sample names or amounts, mismatched totals, missing alt text, mixed languages, links to generic URLs (e.g. `youtube.com` instead of a channel).
- Missing information the rebuild needs: bank account holder, how donations are used, consent for photos of children, roles of team members, hero-quality photo, etc. Each becomes an **Organization confirmation required** item later.

### 6. Content inventory table

Create `audit/CONTENT-INVENTORY.md`: one row per page with URL, title, date, what it contains, keep/merge/archive recommendation, and the new location in the rebuilt site. This becomes the old → new navigation map.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "The homepage tells me enough." | Purpose, bank details, dates and documents usually sit on inner pages and PDFs. Skipping them means inventing later. |
| "That page is 404, I'll write a short FAQ instead." | Missing content is a gap to report, not a gap to fill. |
| "The Instagram has better photos." | Only the organisation's website (or originals the organisation provides) is in scope. |
| "The IBAN looks right." | Use the checksum result. A wrong IBAN on a donation page sends money to the wrong place or nowhere. |

## Red Flags

- `BRIEF.md` facts without a source URL.
- The legal type changed between the source and the brief.
- Photos chosen without opening them.
- No `GAPS.md`, or a gap list with nothing in it on a site with obvious problems.

## Verification

- [ ] `audit/REPORT.md`, `inventory.json`, `pages/`, `images/` exist
- [ ] `BRIEF.md` covers identity, purpose, audiences, giving, trust, contact, news — each fact sourced
- [ ] `GAPS.md` lists broken pages, live-page defects and missing information
- [ ] `CONTENT-INVENTORY.md` maps every content page to keep/merge/archive and a new location
- [ ] Payment setup today is stated with evidence (or "none detected")
