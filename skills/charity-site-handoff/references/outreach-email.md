# Approval email to the organisation

The skill **drafts** the email. A person (the operator) reads it, edits it and sends it from their own mailbox. The skill never sends email on its own, never sends in bulk, and never sends without the operator's explicit "send it" for that one message, with the recipient and full text shown first.

## Why it is one-to-one and manual

- Unsolicited bulk email to organisations is regulated almost everywhere (e.g. GDPR/ePrivacy in the EU, KVKK and the Electronic Commerce Law in Türkiye, CAN-SPAM in the US, CASL in Canada). A single, personal, relevant message to a published contact address is the safest form, and still must identify the sender honestly and offer an easy way to say no.
- Charities are frequent phishing targets. An automated message with a link to a lookalike site of their own brand will be treated as phishing — correctly.

## Recipient

Use an address the organisation publishes for general contact (from the audit: `inventory.json → emails`). Prefer `info@`/`contact@` over personal addresses. Never guess addresses.

## Content (write it in the organisation's language)

1. **Who you are**, in one sentence, with a real name and how to reach you.
2. **What you made and why**: an unofficial redesign proposal of their website, built from their own published content; no cost, no obligation (say so only if true — the operator decides).
3. **What it is not**: not live, not indexed by search engines, does not take payments, not affiliated with them.
4. **How to look at it**: attach the zip, or link to a private preview the operator controls. Never use a domain that resembles theirs.
5. **What happens if they want it**: they receive the full source with a README in their language; three-step summary of publishing and connecting their payment provider.
6. **What you need from them** only if they want to proceed: the top 3–5 open questions (bank account holder, photos with consent, preset amounts…).
7. **Opt-out**: "If you'd rather not hear about this again, just reply 'no' and I won't contact you again."

Length: under 200 words in the body. No marketing superlatives, no urgency, no flattery about their current site, no criticism of whoever built it.

## Template structure (fill in the organisation's language)

```
Subject: <Organisation name> — unofficial website redesign proposal

Hello <team name as published, e.g. "DMD Türkiye team">,

I'm <name>, <one line about yourself>. I prepared an unofficial redesign of <organisation>'s website using only the content already published on <domain>.

It is a proposal, not a live site: it isn't public, it isn't indexed and it can't take payments.
<Attachment / link line>

If you'd like to use it, you'll get the full code with a guide in <language> explaining how to publish it and connect your existing payment provider (<detected provider or "bank transfer">).

To finish it I'd only need a few confirmations from you: <3 short bullet questions>.

If this isn't useful, just reply "no" and I won't contact you again.

<Name>
<Contact details>
```

## After a reply

- "Yes": run the handoff with `"preview": true` kept until they confirm the open questions; then produce the production build.
- "No" or no reply: do not follow up more than once, and not within two weeks.
- Changes requested: apply them in `site.json`, rebuild, re-run checks, resend the zip.
