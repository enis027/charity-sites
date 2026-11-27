# Reading the payment findings

`crawl.py` reports `payments_detected` (provider signatures found in page HTML, script and iframe URLs, and form actions) and `card_form_on_site` (pages whose forms contain card number / CVV / expiry fields).

| Finding | Meaning | What to tell the build and handoff |
|---|---|---|
| A hosted provider (Stripe, PayPal, Donorbox, Givebutter, Mollie, Razorpay…) | The organisation already has an account. | Connect the new donate page to **that** account (payment link or embed). |
| A Turkish payment facilitator (iyzico, PayTR, Param, Sipay, Craftgate, Moka…) | Account exists; most offer payment links. | Use their link product (see payment-providers.md); fixed-amount links go in `links_by_amount`. |
| Bank virtual POS signatures (Nestpay/EST 3D gate, Garanti, POSNET…) | Direct bank integration, often with card fields on the charity's page. | Recommend the bank's hosted page or keeping the existing working donation page and linking to it. Never port card fields. |
| `card_form_on_site` but no known signature | A custom card form posts to their own server. | Treat as above. Note it as a security concern in GAPS.md, neutrally. |
| Only an IBAN | Bank transfer only. | Ship bank transfer; offer the simplest hosted option for their country as a recommendation in the README, not as a live feature. |
| Nothing | No online giving found. | Same as "only an IBAN" if bank details are published; otherwise ask the organisation how it receives donations. |

Always also check manually:
- Does the existing donation flow work end to end up to the provider's page? (Do not submit real card data; stop at the provider's page.)
- Are amounts consistent between steps? Broken totals ("0 TL", "4.545 TL" placeholders) go into GAPS.md.
- Is there a separate membership-dues flow?
