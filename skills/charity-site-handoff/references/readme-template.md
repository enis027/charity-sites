# README template for the organisation

Write it in the organisation's language. Replace every <…>. Keep sentences short; this is read by volunteers, not developers. Use their own words for donation, member, association.

---

# <Organisation name> — new website

This folder contains a redesigned website for <organisation>, built only from the content already published on <old domain>. It is plain HTML and CSS: no database, no plugins, no monthly fee required.

## What's inside

| Folder / file | What it is |
|---|---|
| `site/` | The finished website. This is the folder you publish. |
| `source/site.json` | All texts, links and settings. Edit this to change the site. |
| `source/assets/` | Logo and photos. |
| `tools/` | Rebuilds the site after edits. |
| `OPEN-QUESTIONS.md` | Things we need you to confirm before the site goes live. |
| `SOURCES.md` | Which page of your current site each section's text came from. |

## 1. Look at it

Open `site/index.html` in your browser. It currently shows an "unofficial preview" banner and cannot take payments. That is intentional until you approve it.

## 2. Connect donations — <recommended provider>

<Why this path: e.g. "You already use iyzico, so we connect the new site to the same account." / "Your site doesn't take card donations today; the simplest option in <country> is …">

1. <Dashboard step>
2. <Dashboard step>
3. Copy the link. Open `source/site.json`, find `"payment"` and paste it:
   ```json
   "payment": { "provider": "<id>", "provider_name": "<Name>", "url": "<paste here>", "amount_param": "<value or empty>", "amount_unit": "<minor|major>" }
   ```
4. Rebuild (section 5) and open `site/donate.html`. Choose an amount and press the button: you should land on <provider>'s page with the amount filled in <if supported>.
5. Make one small test payment in <provider>'s test mode or with a real small amount you refund afterwards.

Card details are typed only on <provider>'s secure page, never on your site.

Bank transfer details are shown on the donation page. Please confirm the account holder name in OPEN-QUESTIONS.md.

<If membership dues exist: one paragraph on how dues are paid and that they are separate from donations.>

## 3. Contact and newsletter forms

A static site needs a small form service to receive messages. The easiest: <Formspree / Web3Forms / Netlify Forms>. Create a form, copy its address into `"contact_form": {"action": "…"}` (and `"newsletter": {"action": "…"}`), rebuild. Without it, the published site shows your email and phone instead of a form.

## 4. Publish

Choose one:
- **Your current host:** upload the *contents* of `site/` with your hosting panel's file manager or FTP, replacing the old files (keep a backup).
- **Cloudflare Pages / Netlify (free plans available):** create a site, drag and drop the `site` folder, then connect your domain in their dashboard.
- **GitHub Pages:** upload `site/` to a repository and enable Pages.

## 5. Going live / rebuilding after edits

1. Answer OPEN-QUESTIONS.md.
2. In `source/site.json` set `"preview": false`.
3. Run `python3 tools/build.py` (Python 3.10+, nothing else to install). It rebuilds `site/` and checks it. Fix anything it reports as ERROR.
4. Publish `site/` again.

## 6. Everyday edits

- Text: edit `source/site.json` (keep the quotes and commas), rebuild.
- News: copy an existing news page block in `site.json`, change title, date (YYYY-MM-DD) and text.
- Photos: put the file in `source/assets/`, reference it, write a short description (`alt`). Only use photos of children with written consent from their parents or guardians.

## 7. For your web developer

- Accessibility: the build enforces colour contrast, labels and link checks; please also test with a keyboard and a screen reader (VoiceOver/NVDA) and at 200% zoom.
- Privacy: fonts load from Google Fonts. <If EU/UK: "Consider self-hosting them (see tools/template/README or i18n notes)">.
- No tracking or cookies are included.

## 8. Where did my pages go?

| Old page | New location |
|---|---|
| <old URL> | <new page/section> |

## Questions

<Operator name and contact>
