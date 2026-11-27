# site.json reference

One JSON file describes the whole site. Paths are relative to the folder containing `site.json` (put images in `assets/`). Internal links are relative file names (`about.html`, `help.html#faq`) so the site works on any host and from a folder. Text fields accept `**bold**` and `[label](url)` where noted as *md*.

## Top level

| Key | Required | Notes |
|---|---|---|
| `preview` | yes | `true` until the organisation approves: banner, `noindex`, `robots.txt` disallow. |
| `lang` | yes | BCP 47, e.g. `tr`, `en`, `ar`, `pt-BR`. Picks fonts, direction, interface strings. |
| `locale`, `currency` | | e.g. `tr-TR`, `TRY`. `locale: "en-US"` switches dates to Month D, YYYY. |
| `currency_display` | | `{"symbol": "₺", "position": "after", "thousands": "."}` |
| `base_url` | | Production URL, used for canonical links (not in preview). |
| `org` | yes | `name` (official, exact), `short_name`, `legal_type`, `logo`, `logo_reverse` (white version or null), `logo_width`/`logo_height` (intrinsic ratio), `logo_alt`, `favicon`, `share_image`. |
| `brand` | yes | `colors`: 2–4 hex colours from the logo/old CSS. Optional `primary`, `accent`, `donate` to force a role, `overrides` to set any token (`{"text-secondary": "#5C5A57"}`) — the contrast audit still runs. |
| `fonts` | | `heading`, `body` (families), `self_hosted: true` to use `fonts/fonts.css` instead of Google Fonts. |
| `ui` | | Override individual interface strings for this site. |
| `contact` | | `address`, `phone`, `phone_href` (optional `tel:`), `email`, `social: [{network, url, label?}]`, `src`. Networks with icons: facebook, instagram, x/twitter, youtube, linkedin, tiktok, whatsapp, telegram. |
| `nav` | yes | `[{label, href}]` or `[{label, children: [{label, href}]}]`. ≤ 6 items. |
| `header.member_cta` | | `{label, href}` — secondary header link (membership/volunteer). |
| `donate_href` | yes | Usually `donate.html`. |
| `sticky_donate` | | Mobile sticky donate bar on every page except the donate page. `sticky_title` overrides its title. |
| `payment` | | See the handoff skill's payment-providers.md. `url`, `provider_name`, `amount_param`, `amount_unit`, `links_by_amount`, `embed_html`, `monthly_url`. |
| `bank` | | `recipient`, `bank_name`, `iban`, `account_number`, `sort_code`, `swift`, `reference_hint` (*md*), `src`. Each number gets a copy button. |
| `donation` | | `presets` (numbers; the organisation's own, or `[]`), `default`, `min`, `summary_note` (*md*), `trust_note: {text, link?, src}` (only sourced statements), `membership_note: {title?, text, src}`, `notes: [{variant, title?, text}]`. |
| `contact_form` | | `action` (form-service URL; empty = demo in preview, omitted in production), `title`, `subjects: []`, `privacy_link: {label, href}`. |
| `footer` | | `about`, `columns: [{title, links: [{label, href}]}]`, `legal_links`, `newsletter: {title?, text?, action, src}` or `null`, `copyright_year`. |
| `pages` | yes | List of pages; one must have `slug: "index"`. |

Add `"needs_confirmation": "question"` to any object whose content the organisation must confirm. `check.py` lists them.

## Page

| Key | Notes |
|---|---|
| `slug` | File name without `.html`; `index` is the home page. |
| `title`, `description` | `<title>` and meta description (≤ 155 characters, from the page's own content). |
| `nav_active` | Label of the nav item to mark as current. |
| `layout` | `default` (sections), `article` (news/guide), `donate`. |
| `header` | Page header: `breadcrumb: [{label, href?}]`, `overline`, `title` (the H1), `lead` (*md*), `ctas`, `date` (ISO), `category`. Required for `article` and `donate`; optional for `default` (the home page uses a `hero` section instead). |
| `sections` | `default` and `donate` layouts: list of sections below. |
| `src`, `body`, `aside` | `article` layout: source URL, list of body blocks, list of aside blocks. |

## Sections (`default` layout)

All sections accept: `type`, `src` (required for content sections), `id` (anchor + labelled region), `tone` (`subtle`, `tint`, `accent`, `brand`), `overline`, `title`, `lead` (*md*), `link: {label, href}` (shown at the right of the heading).

| type | Fields |
|---|---|
| `hero` | `title` (H1), `overline`, `lead`, `ctas: [{label, href, style, icon?}]`, `facts: [{icon, text}]`, `photo: {src, alt, width, height, caption?, position?}`, `photo_placeholder` (default true). Styles: `donate`, `primary`, `secondary`, `ghost`, `inverse`. |
| `pillars` | `items: [{title, text}]` — numbered activities. |
| `quote_band` | `quote`, `attribution`, `text`, `cta`, `photo`. Brand background by default. |
| `cards` | `items: [{icon, title, text, href, link_label}]`, `columns` (2/3/4), `quick_links: [{label, href}]`. |
| `documents` | `items: [{title, meta, href}]` — reports, filings, PDFs. |
| `logos` | `items: [{name, logo?, href?}]` — partners (names always shown as text). |
| `news` | `items: [{date, category, title, href, excerpt, image?, image_width?, image_height?}]`. |
| `cta` | `title`, `lead`, `ctas`, `note` (*md*). Tint background by default. |
| `prose` | `blocks` (see below). |
| `accordion` | `items: [{q, a (md), open?}]`. |
| `team` | `items: [{name, role?, photo?}]`. Leave `role` out if the source doesn't publish it. |
| `chips` | `items: [{label, href?, icon?}]` — regions, topics. |
| `columns` | `columns: [{type: documents|logos|prose|accordion, title, icon, lead, items|blocks, link, id}]` — two side-by-side blocks. |
| `contact` | `blocks` (optional extra prose). Renders contact details from `contact`, social links and the form from `contact_form`. |

## Blocks (`prose`, `article.body`)

`{type: "p", text (md)}`, `{type: "h2"|"h3", text, id?}`, `{type: "ul"|"ol", items: [md…]}`, `{type: "quote", text, attribution?}`, `{type: "figure", src, alt, width, height, caption?}`, `{type: "alert", variant: info|success|warning|error, title?, text}`, `{type: "documents", items}`, `{type: "accordion", items}`, `{type: "buttons", items: [cta…]}`, `{type: "share", url, title}`.

## Aside blocks (`article.aside`)

`{type: "facts", title?, items: [{icon, k, v (md)}], link?}`, `{type: "donate", title?, text?, show_member?}`, `{type: "links", title, items: [{label, href, date?}]}`, `{type: "chips", title, items: [{label, href}]}`, `{type: "alert", …}`, `{type: "steps", title, caption?, items: [{title, text}]}`.

## Icons

`arrow-right, arrow-left, chevron-down, menu, close, copy, check, check-circle, alert-circle, alert-triangle, info, phone, mail, map-pin, heart, external-link, download, file-text, calendar, search, users, user-plus, book-open, shield-check, play, stethoscope, building, handshake, globe, home, megaphone, lock` and the social icons.
