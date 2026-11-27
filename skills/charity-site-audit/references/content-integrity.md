# Content integrity rules

The rebuilt site is a better presentation of what the organisation already says. It is never a rewrite of what the organisation is.

## Allowed

- Shorten existing text without changing its meaning.
- Split long paragraphs, turn run-on lists into real lists.
- Derive headings from existing statements (a heading may paraphrase a sentence that exists on the source page).
- Fix spelling, grammar, capitalisation (e.g. ALL-CAPS news titles → sentence case) and obvious typos.
- Write short **functional** interface text: navigation labels, buttons, form labels, error messages, breadcrumb labels. Interface strings live in `template/i18n/<lang>.json`, not in content.
- Combine facts the source states in different places (e.g. "Founded 2016 in Istanbul" from the story page) into a fact line.

## Never

- New activities, services, programmes, projects, campaigns or events.
- Patient, family or beneficiary stories, quotes or testimonials that the source does not contain verbatim.
- Partners, sponsors, endorsements, awards, accreditations, "as seen in" logos.
- Impact numbers, beneficiary counts, percentages, financial figures, "your gift buys…" equivalences.
- Medical claims, treatment promises, cure language, eligibility advice.
- Security badges, audit statements, tax-deductibility claims, payment-provider claims the organisation has not made.
- Re-dating content, removing dates from old news, or ordering old items as if they were current.
- Renaming the organisation or changing its legal type (an *association* is not a *foundation*; a *charity* is not an *NGO* unless the source says so).
- Lorem ipsum, sample names ("John Doe", the old site's demo names), sample amounts carried over from a broken form.
- Copying another organisation's text, structure or visual identity.

## When something is missing

Do not fill the gap. Instead:
1. Leave the section out of the public page, or use a neutral functional label.
2. Add `"needs_confirmation": "what to ask"` on the closest object in `site.json`. `check.py` collects these.
3. List it in `OPEN-QUESTIONS.md` under "Organization confirmation required", in the organisation's language.

Typical open questions: how donations are used; bank account holder name and bank; preset amounts; whether monthly giving is supported; consent for photos of children; team roles; dues amount and how to pay them; registration/charity number; privacy policy owner; who receives contact-form messages.

## Source mapping

Every section in `site.json` carries `"src"`: the URL(s) of the page(s) its text came from (comma-separated, or `"fixture"` in tests). `check.py` fails the build if it is missing. `SOURCES.md` in the handoff turns this into a table and lists every **meaningful wording change** (anything beyond typo fixes) with old → new text.

## Sensitive material

- Children: no full names unless the source published them; no diagnosis attached to a named child; no photos without consent flagged.
- Political or legal advocacy: present the organisation's own statements with their dates; do not intensify or soften them.
- Press articles about the organisation: link to them with the outlet name and date; do not paste third-party articles in full (copyright).
