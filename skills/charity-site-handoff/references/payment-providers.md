# Connecting payments: the easiest safe path

The website never collects card details. The donate page lets the visitor pick an amount, then sends them to the payment provider's **hosted** page (redirect) or shows the provider's own embedded form. This keeps the organisation out of most card-security work: under PCI DSS, merchants that fully outsource card entry to a provider via redirect or iframe generally qualify for the shortest self-assessment (SAQ A). Third-party scripts on the payment page can affect that, so the page ships with none. The organisation should confirm its own obligations with its provider or acquirer.

## Decision order

1. **Keep what already works.** If the audit found a working provider (Stripe, PayPal, Donorbox, iyzico, PayTR, a bank virtual POS…), connect to *that* account. Changing provider is the organisation's decision, not ours.
2. **Existing donation page on another system works?** Link to it: put its URL in `payment.url` with no `amount_param`. Zero integration work.
3. **No online payments today?** Recommend the simplest hosted option available in their country (table below), and keep bank transfer visible meanwhile.
4. **Card fields on their own server today** (direct virtual-POS integration, card number typed into the charity's page): recommend switching to the bank's hosted payment page ("3D Pay Hosting" / "Ortak Ödeme Sayfası") or a payment-link provider. Do not port the card form.

## How the site connects (all providers)

Edit `site.json` → `payment`, then rebuild (`python3 build/build.py site.json`). Or, without rebuilding, edit the `data-url` attribute on `<form id="donation-form">` in `donate.html`.

```json
"payment": {
  "provider": "stripe-payment-link",
  "provider_name": "Stripe",
  "url": "https://donate.stripe.com/XXXX",
  "amount_param": "prefilled_amount",
  "amount_unit": "minor",
  "monthly_url": ""
}
```

| Field | Meaning |
|---|---|
| `url` | The provider's hosted donation/payment link. |
| `amount_param` | Query parameter the provider reads to prefill the amount. Leave empty if the provider has none. |
| `amount_unit` | `minor` = cents/kuruş (amount × 100), `major` = whole units. |
| `links_by_amount` | For providers that only issue **fixed-amount** links: `{"100": "https://…", "250": "https://…"}`. The page then offers exactly those amounts and hides the custom field. |
| `embed_html` | Provider's embed snippet (only if they insist on an embedded form; prefer links). |
| `monthly_url` | A separate link for monthly giving. Only if the organisation actually offers it; the monthly choice appears only when this is set. |

Then set `"preview": false` and rebuild. `check.py` refuses a production build that still has a demo form.

## Provider recipes

Each recipe states what is verified and what the organisation must check in its own dashboard. Write the README section in the organisation's language using these steps.

### Stripe Payment Links (global, where Stripe operates)
- Dashboard → Payment Links → New → choose **"Customers choose what to pay"** (pay-what-you-want). Set a suggested amount if wanted.
- Copy the link into `url`. Set `amount_param: "prefilled_amount"`, `amount_unit: "minor"` — Stripe documents `prefilled_amount` for customer-chooses-price links; the donor can still edit it.
- Verified: prefilled_amount behaviour and that it has no effect on fixed-price links (docs.stripe.com/payment-links/customize). Check: currency and maximum amount limits in their account; customer-chooses-price links are one-time payments (use a separate subscription link for monthly giving if needed).

### PayPal Donate button (global)
- PayPal business account → Pay & Get Paid → PayPal buttons → **Donate** → create. The hosted button gives an ID; the donation link is `https://www.paypal.com/donate/?hosted_button_id=ID`.
- Set `url` to that link and leave `amount_param` empty: hosted donate buttons do not reliably accept a prefilled amount, so the donor enters it on PayPal.
- Verified: hosted_button_id usage (developer.paypal.com/sdk/donate). Check: nonprofit status/fees in their country.

### Donorbox / Givebutter / Zeffy / similar nonprofit platforms
- Use the campaign's public link as `url`; leave `amount_param` empty unless the platform documents a prefill parameter for that campaign. Embedding their widget via `embed_html` also works (requires HTTPS on the site).
- Check: platform fees vs. "donor covers fees" option, recurring options, receipts.

### Mollie Payment Links (EU)
- Dashboard → Payment links → create a reusable link (variable amount if offered in their account). Use as `url`, no `amount_param`.
- Check: whether their link type is reusable; Mollie's own docs list donations as a payment-link use case.

### Razorpay Payment Pages (India)
- Payment Pages → create → amount type **"Customer decides amount"**, set min/max. Use the page URL as `url`.
- Useful: Razorpay offers automated 80G receipts for registered NGOs. Check eligibility.

### PayTR Link ile Ödeme (Türkiye)
- PayTR mağaza paneli → Link ile Ödeme → create a link per amount (links have a fixed amount). Put them in `links_by_amount`, e.g. `{"100": "…", "250": "…", "500": "…"}`.
- Check: account approval documents for associations (dernek), commission, and whether variable-amount links are available on their plan.

### iyzico Link (Türkiye)
- iyzico panel → iyzico Link. Donation use is permitted only under conditions stated by iyzico; **the organisation must confirm with iyzico that donations are allowed on their link account** before going live. Connect as `url` or `links_by_amount` like PayTR.

### Bank virtual POS (sanal POS) with a hosted page
- Many banks offer a hosted 3D payment page ("3D Pay Hosting", "Ortak Ödeme Sayfası"). It usually needs a small server-side step to sign the request, so it is **not** a pure static-site job. Options: keep the existing donation page on the old system and link to it (option 2 above), or ask the bank/provider for a payment-link product.

### Bank transfer only
- Always shown when `bank` is set. Verify the IBAN checksum (the audit does) and confirm the **account holder name** and bank with the organisation before launch.

## Contact and newsletter forms (no server needed)

Static sites need a form service to receive messages. Easiest options: Formspree, Web3Forms, Netlify Forms (if hosted on Netlify), or a Cloudflare Worker. Put the endpoint in `contact_form.action` / `footer.newsletter.action`. Without one, production builds simply omit the forms and show email/phone.

## Writing the payment section of the README

In the organisation's language, include:
1. What the visitor experiences (choose amount → provider's secure page → back to site).
2. The one recommended path for them, with numbered dashboard steps, and where to paste the link.
3. How to test with the provider's test mode before going live.
4. How to switch off the preview banner (`"preview": false`) and rebuild.
5. What still needs their confirmation (account holder name, monthly giving, receipts, refunds policy — "Yapılan bağış iade yapılmamaktadır"-style statements only if they already publish one).
