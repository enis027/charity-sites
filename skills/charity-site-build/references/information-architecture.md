# Information architecture for charity sites

## Top navigation (≤ 6 items + Donate)

Default model — rename items with the organisation's own words:

| Item | Contains (merge old pages here) |
|---|---|
| Home | |
| About | Story, mission/purpose, team, regions/branches, partners, accountability/reports, statutes |
| Help / Support (name it after the people served: "Family support", "Get help", "Patients") | Guides, condition information, forms, FAQ, regional contacts, videos |
| News | News, announcements, press releases, newsletters, events |
| Contact | Address, phone, email, form, membership/registration links |
| *(optional)* Get involved | Volunteer, membership, events — only if the organisation actually offers these |

Header right side: secondary "Member/Volunteer" ghost link (only if it exists) + the red **Donate** button. On mobile: logo, Donate, menu button.

Rules:
- Every old page stays reachable: rebuilt, merged into a hub, or linked from a hub to its old URL.
- Write the old → new mapping as a table in `audit/CONTENT-INVENTORY.md`; the handoff README repeats it for the organisation.
- Language switcher only if the organisation has real content in more than one language.

## Homepage sequence (default)

1. **Hero** — who / for whom / what (from their own purpose statement), Donate + Help CTAs, 2–3 sourced fact chips (founded, regions, governance). One strong static photo or the labelled placeholder.
2. **What we do** — numbered pillars from their stated purposes/activities (`pillars`).
3. **Story / vision** — a real quote or vision statement on the brand band, with one authentic photo (`quote_band`).
4. **Help for the people served** — resource cards + quick links (`cards`).
5. **Trust** — reports/filings + partners side by side (`columns`), only what exists.
6. **News** — 3 most recent items with real dates (`news`).
7. **Closing donation invitation** — Donate + secondary action, membership vs donation note if both exist (`cta`).
8. Footer — organisation summary, link columns, contact, newsletter (if a form service exists), legal links.

Adapt: if the organisation is mainly a service provider (shelter, food bank), move "Help" directly under the hero. If there is no news in the last two years, put news lower and title it neutrally ("From our archive" in their language is a functional label, acceptable).

## Inner page patterns

| Page | Layout | Sections |
|---|---|---|
| About | default with page header | prose (purpose list, vision quote, story), team, chips (regions), columns (partners + reports) |
| Help hub | default with page header (CTA to registration form) | cards (guides), accordion (key questions from their own content), chips (regional contacts), cta |
| Article | `layout: article` | page header with category + real date, body blocks, aside: other news (with dates), categories, donate box |
| Donate | `layout: donate` | page header; amount → provider hand-off; bank transfer block; trust note (only sourced statements); membership note |
| Contact | default with page header | contact section (details + form if a form service exists), social links, regional contacts link |

## Donation page specifics

- Amount first, everything else on the provider's page.
- Preset amounts = the organisation's existing ones, if any; otherwise custom amount only and an open question.
- Summary shows the same amount everywhere (the old site's mismatched totals are a common defect).
- Membership fees are a different thing: one sentence and a contact or separate link.
- Monthly giving appears only if the organisation has a monthly link.
- Bank transfer always visible when they publish bank details, with copy buttons.
- No pop-ups, timers, guilt copy, pre-ticked boxes.
