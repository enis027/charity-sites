---
description: Rebuild a charity or nonprofit website from its URL — audit, build, and package a handoff with a payment guide in the organisation's language
argument-hint: <charity website URL>
---

Rebuild the charity website at: $ARGUMENTS

Run the three charity-sites skills in order. Talk to the operator in their language; build the site in the organisation's language.

1. **Audit** — invoke the `charity-site-audit` skill. Crawl the site, read every content page, write `BRIEF.md`, `GAPS.md` and `CONTENT-INVENTORY.md`.
   Checkpoint: show the operator a short summary — who the organisation is, what payment setup it has, broken pages, missing information, how many usable photos. Continue unless the operator stops you.

2. **Build** — invoke the `charity-site-build` skill. Write `site.json` from the audit only, build, run `check.py --site`, review screenshots at 390/768/1440, then run the `content-integrity-reviewer` agent and fix its findings.
   Checkpoint: show the operator the home and donate page screenshots and the check summary.

3. **Handoff** — invoke the `charity-site-handoff` skill. Write README and OPEN-QUESTIONS in the organisation's language, package the zip, and write the approval email draft. Do **not** send any email; tell the operator where the draft and the zip are and which published address it should go to.

Rules that apply throughout:
- Only content the organisation already publishes. Anything missing becomes an "Organization confirmation required" item, never invented text.
- Photos only from the organisation's website (or originals the operator provides from the organisation).
- No card fields on the site; donations hand off to the provider's hosted page.
- Keep `"preview": true` until the organisation approves.

Final message to the operator: what was built, where the zip and email draft are, the check results, the open questions, and the recommended payment path.
