# Charity website UX principles

What the evidence says, and what this skill does about it. Every rule here is applied by default; the source column tells you how strong the evidence is so you can explain trade-offs to the organisation.

## 1. Say who you are within seconds

| Finding | Source | What we do |
|---|---|---|
| Information about the organisation's mission, goals and work was by far the most important factor for donors. In testing, people needed about **6 minutes** to find what an organisation does; NN/g suggests 1 minute as a reasonable goal. | NN/g, *Donation Usability* and *5 Tips to Get Donations* (Nielsen, 2009, reaffirmed in later articles) | The hero states **who** (official name and legal type), **for whom** and **what they do** in the H1 + lead, derived from the organisation's own words. No slogan-only heroes. |
| Unclear mission information "immediately turned off" users. | NN/g report *Attracting Donors and Volunteers on Non-Profit and Charity Websites* | A plain "What we do" section follows the hero, built from the organisation's stated purpose/statutes. |

Rules:
- The first screen (390 × 844 and 1440 × 900) must show: name, who is served, what the organisation does, and a Donate action. Check it in the screenshots.
- Headlines come from existing statements. Never write a new mission.

## 2. Make giving visible and easy, without pressure

| Finding | Source | What we do |
|---|---|---|
| About a quarter of nonprofit homepages tested had no Donate call to action; "Contribute" and similar labels caused confusion compared with "Donate". | NN/g, *5 Tips to Get Donations on Nonprofit and Charity Websites* | One red/warm **Donate** button (the site language's plain word for donate) in the header on every page, in the hero, and in a closing section. It is the only element in the donate colour. |
| A suggested-amount version of Oxfam's mobile donation call to action produced 23% more form completions than a plain "Donate now" button. | NN/g, *The Anchoring Principle* (reporting a Behave.org test) | Preset amount chips + a custom amount field. |
| Evidence on defaults is mixed: suggested amounts can raise average gift but lower participation; effects depend on context. | Goswami & Urminsky, *When should the ask be a nudge?* (University of Chicago) | Use the organisation's **existing** preset amounts if it has any. If it has none, do not invent them: ship custom-amount only and list "preset amounts" as an open question. Never pre-tick monthly giving. |
| Form length (number of visible fields) hurts completion more than the number of steps. Baymard recommends roughly 6–8 fields for a full checkout. | Baymard Institute checkout research | The site only asks for the amount. Personal and card details are collected once, on the payment provider's hosted page. |

Rules:
- No pop-ups, countdown timers, fake scarcity, guilt copy, or pre-selected recurring gifts.
- Keep donation and membership fees visibly separate. If the organisation takes both, explain the difference in one sentence.
- Show every payment method the organisation actually supports today, and nothing else.

## 3. Build trust through verifiable transparency

| Finding | Source | What we do |
|---|---|---|
| Donors want to know where money goes, and credible third-party signals help. | NN/g, *5 Tips…* | Surface what already exists: annual reports, statutory filings, audits, registration numbers, partners, governance. Link to the documents themselves. |
| Organisations rarely state on the homepage where donations are applied. | NN/g study summary | Only state donation use if the organisation documents it. Otherwise list "how donations are used" as **Organization confirmation required** — never on the public page. |

Hard rules (from the content-integrity reference):
- No invented statistics, beneficiary counts, percentages, "₺X buys Y" equivalences, testimonials, partner logos, endorsements, security badges, tax-deduction claims, or audit claims.
- Old content keeps its real date. Never re-date or present it as recent.

## 4. Photography: authentic, dignified, consented

| Principle | Source | What we do |
|---|---|---|
| Respect for the dignity of the people shown; equality; avoid stereotypes and sensationalism. | Dóchas *Code of Conduct on Images and Messages* (adopted by 70+ Irish NGOs) | Prefer photos of people doing things together (events, therapy as activity, families) over helplessness or close-ups of medical equipment. |
| Use images only with the subject's (or parent/guardian's) understanding and permission; record whether they wish to be named. | Dóchas Code, consent principle | Every photo of an identifiable child is flagged "confirm consent" in OPEN-QUESTIONS. Never name children unless the source did. |
| Authentic photos outperform stock for trust. | Practitioner consensus (several nonprofit agencies); treat as guidance, not proof | Use the organisation's own photos. Never AI-generated people presented as beneficiaries. Stock may only be used for neutral textures, never for "patients" or "families". |

See `../../charity-site-audit/references/photography.md` for resolution thresholds, crops and upscaling limits.

## 5. Help the people the organisation serves

Beneficiaries (patients, families, volunteers) often arrive with an urgent question, not to donate.
- Give "help/support" its own top-level navigation item and a hero secondary action.
- Group resources by task ("after diagnosis", "surgery and anaesthesia", "forms") rather than by the old site's menu.
- Contact details are one tap away on mobile (phone as `tel:` link) and repeated in the footer.
- Medical content: present the organisation's own text faithfully, keep its date, add "this is not medical advice" only if the source page implies it or the organisation confirms. Never add treatment promises.

## 6. Mobile, accessibility and performance are not extras

| Requirement | Source | Target in this template |
|---|---|---|
| Text contrast ≥ 4.5:1 (3:1 for large text); UI components and focus indicators ≥ 3:1. | WCAG 2.2 SC 1.4.3, 1.4.11 | Enforced by `palette.py` + `check.py`. |
| Keyboard focus visible, and not hidden by sticky content. | WCAG 2.2 SC 2.4.7, 2.4.11 | Two-tone focus ring; `scroll-padding` for sticky header/footer; sticky donate bar hides while a field has focus. |
| Pointer targets at least 24 × 24 CSS px (with spacing exceptions). | WCAG 2.2 SC 2.5.8 | We target 44 × 44 for all primary controls, 48 px form fields. |
| Content reflows at 320 CSS px without horizontal scroll; text spacing can be increased. | WCAG 2.2 SC 1.4.10, 1.4.12 | Mobile-first CSS, no fixed widths; checked in the 390 px screenshot pass. |
| Errors identified in text, with suggestions. | WCAG 2.2 SC 3.3.1, 3.3.3; GOV.UK Design System *Error message* | Error summary at the top, message under each field, specific wording ("Enter your email address"), linked with `aria-describedby`, visually hidden "Error:" prefix. |
| Information never by colour alone. | WCAG 2.2 SC 1.4.1 | Selected amounts show a check icon + border; errors have an icon + text. |
| Good Core Web Vitals: LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1 at the 75th percentile. | web.dev, *Web Vitals* | Static HTML, ~30 KB CSS, ~6 KB JS, explicit image dimensions, lazy loading below the fold, page-weight budget in `check.py`. |

A Figma file or an automated check cannot establish conformance. The handoff README lists the manual checks (screen reader, keyboard, zoom) the organisation's developer must run.

## 7. Visual direction: warm, clear, not a SaaS template

- Personality: trustworthy, warm, human, hopeful, clear, professional. Not clinical, childish or dramatic.
- Keep the existing logo untouched; derive the palette from it (`palette.py`), adjusting only lightness for contrast.
- Serif headings + humanist sans body by default (Source Serif 4 / Source Sans 3 for Latin, Cyrillic, Greek and Vietnamese; Noto families for other scripts — see `i18n.md`).
- Vary section rhythm: alternate white / subtle / brand bands, mix numbered lists, quote bands, cards, documents and chips. Never three identical card grids in a row.
- One strong static hero image. No auto-rotating carousels (they hide content, move focus and are rarely seen past slide 1).

## Sources

- Nielsen Norman Group — *5 Tips to Get Donations on Nonprofit and Charity Websites*: https://www.nngroup.com/articles/donations-nonprofit-charity-online/
- Nielsen Norman Group — *Donation Usability: Increasing Online Giving*: https://www.nngroup.com/articles/donation-usability/
- Nielsen Norman Group — *The Anchoring Principle*: https://www.nngroup.com/articles/anchoring-principle/
- Goswami & Urminsky — *When should the ask be a nudge? The effect of default amounts on charitable donations*: https://home.uchicago.edu/ourminsky/Charity_Default_Goswami_Urminsky.pdf
- Baymard Institute — *Checkout Optimization: Minimize Form Fields*: https://baymard.com/research-articles/checkout-flow-average-form-fields
- W3C — *Web Content Accessibility Guidelines (WCAG) 2.2*: https://www.w3.org/TR/WCAG22/
- W3C — *Understanding SC 2.5.8 Target Size (Minimum)*: https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
- W3C — *Understanding SC 2.4.11 Focus Not Obscured (Minimum)*: https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html
- GOV.UK Design System — *Error message*: https://design-system.service.gov.uk/components/error-message/
- web.dev — *Web Vitals*: https://web.dev/articles/vitals
- Dóchas — *Code of Conduct on Images and Messages* (illustrative guide): https://developmenteducation.ie/resource/illustrative-guide-to-the-da%C2%B3chas-code-of-conduct-on-images-and-messages/
