---
name: charity-site-handoff
description: Packages a rebuilt charity website for the organisation — a README in the organisation's own language with the easiest way to publish the site and connect its existing payment provider, a list of facts the organisation must confirm, a content-source table, a zip, and a short personal approval email draft for a human to review and send. Use when preparing a rebuilt nonprofit site for delivery after charity-site-build, or when asked how a charity can connect payments to a static site.
---

# Charity site handoff

## Overview

The organisation receives a folder it can publish without a developer, a guide it can read in its own language, and an honest list of what still needs its confirmation. The operator (the person running this skill) receives an email draft. Nothing is sent automatically.

## When to Use

- Step 3 of `/charity-site`, after the build passes its checks.
- When the organisation approves and the preview must become a production build.
- When someone asks how to connect donations to a site built with this template.

## Process

### 1. Decide the payment path

Use [payment-providers.md](references/payment-providers.md) with the audit's payment findings. One recommended path, in this order: keep and connect the provider they already use → link to their existing working donation page → the simplest hosted option in their country. Bank transfer stays visible whenever they publish bank details.

### 2. Write `handoff/README.md` in the organisation's language

Plain language for a non-technical volunteer, using [readme-template.md](references/readme-template.md). Must include:
1. What they are receiving and that it is built only from their published content.
2. How to look at it locally (double-click `site/index.html`).
3. How to publish it — the three easiest free/low-cost options, with steps, plus "upload the `site` folder to your current host via FTP".
4. **Connecting payments** — the single recommended path for *them*, step by step, ending with exactly which value to paste where, how to test, and how to rebuild.
5. Connecting the contact/newsletter forms (or leaving them out).
6. Going live: set `"preview": false`, rebuild, check the result, point the domain.
7. Editing text later (`source/site.json`), adding news, replacing photos (and the consent rule).
8. Accessibility checks their developer should run manually (from visual-qa.md, shortened).
9. Old → new page map, so nothing they had disappears.
10. Who to contact with questions (the operator).

### 3. Write `handoff/OPEN-QUESTIONS.md` in the organisation's language

Title the list with the local equivalent of **"Organization confirmation required"**. Gather from `audit/GAPS.md`, every `needs_confirmation` in `site.json` (`check.py --json` lists them), photo consent flags and the payment setup (account holder, provider account, preset amounts, monthly giving). Each item: the question, why it matters, where it appears on the site.

### 4. Optional: `handoff/WORDING-CHANGES.md`

Table of meaningful wording changes (old text → new text → page), anything beyond typo fixes, shortening or splitting.

### 5. Package

```bash
python3 <skill-dir>/scripts/package.py work/example-org --name example-org-website --zip
```

It copies the source and tools, rebuilds into `site/`, runs the checks, generates `SOURCES.md` and zips everything. Do not send a package whose checks failed.

### 6. Draft the approval email — do not send it

Write `handoff/EMAIL-DRAFT.md` following [outreach-email.md](references/outreach-email.md): in the organisation's language, personal, under 200 words, honest about what it is and is not, with an opt-out line. Address it to a general contact address published on their site.

Then tell the operator: where the zip is, the email draft, the recipient address found, and that **they** should review and send it from their own mailbox. If the operator explicitly asks you to send it with a connected mail tool, show the recipient, subject and full body first and send only after they confirm that exact message. Never send to more than one organisation in one action, and never follow up automatically.

### 7. After approval

Keep `preview: true` until the open questions are answered. Then apply the answers to `site.json`, connect payment links, set `preview: false`, rebuild, re-run checks (production mode refuses demo forms and noindex), re-package.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "I'll send the email to save the operator time." | Sending on someone's behalf is their decision every time. Charities also treat unexpected lookalike-site emails as phishing. |
| "English README is fine, they'll translate it." | The guide is the product for a volunteer-run organisation. Their language, their provider, their dashboard words. |
| "I'll list every payment provider so they can choose." | Choice overload stalls small teams. One recommended path; alternatives in one short paragraph. |
| "Open questions make the work look unfinished." | They are what makes the work trustworthy. |

## Red Flags

- README mentions a provider the organisation does not use without saying it is a recommendation.
- Production build with `preview: false` while open questions remain about bank details or payment links.
- Email body with urgency, flattery or criticism of the current site.
- Any automated sending, bulk sending or follow-up scheduling.

## Verification

- [ ] README.md and OPEN-QUESTIONS.md are in the organisation's language
- [ ] Payment section gives one path, exact paste location and a test step
- [ ] package.py finished with checks passing; zip exists
- [ ] EMAIL-DRAFT.md written; nothing sent without the operator's explicit, per-message confirmation
