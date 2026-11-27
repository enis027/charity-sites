# Visual and manual QA

Run after `check.py` passes. Look at the screenshots from `scripts/screenshots.py` and a real mobile viewport.

## First screen (390 × 844 and 1440 × 900)

- [ ] Organisation name visible (logo or text)
- [ ] H1 + lead say who / whom / what in the organisation's words
- [ ] Donate visible without scrolling, and it is the only element in the donate colour
- [ ] A route for the people served (Help / Support) is visible
- [ ] Preview banner present (preview builds) and readable

## Layout and rhythm

- [ ] No horizontal scrolling at 320–390 px (check `document.documentElement.scrollWidth` in a mobile emulator)
- [ ] Sections alternate background tones; no three identical card grids in a row
- [ ] Long words (German compounds, Turkish suffixes) wrap instead of overflowing
- [ ] Hero photo crop keeps faces in frame on both mobile (5:4) and desktop (4:5); placeholder labelled if no suitable photo
- [ ] Images are sharp at their displayed size (no upscaled blur, no stretched logos)
- [ ] Sticky donate bar does not cover the footer's last links or any focused field

## Typography

- [ ] Body text ≥ 16 px on mobile (template default 18 px); line length ≤ ~75 characters in prose
- [ ] Script renders correctly: Turkish İ/ı/Ş/ğ, accents, Arabic joining, no tofu boxes
- [ ] Headings are hierarchy, not decoration (one H1)

## Keyboard (desktop browser)

- [ ] Tab from the top: skip link appears first and jumps to main content
- [ ] Every link/button shows the focus ring; focus never hides under the sticky header
- [ ] Dropdown menus open with Enter/Space, close with Esc, and all sub-pages are reachable
- [ ] Mobile menu: opens, Esc closes and returns focus to the menu button
- [ ] Donation: arrow keys move between amount chips; Enter submits; errors receive focus

## Screen reader smoke test (VoiceOver, NVDA or TalkBack, 5 minutes)

- [ ] Page title and landmarks (banner, navigation, main, contentinfo) announced
- [ ] Amount chips announced as a radio group with the amount and selected state
- [ ] Error summary and field errors announced ("Error: Enter your email address")
- [ ] Copy-IBAN button announces "copied"
- [ ] Icon-only links (social, share) have names

## Zoom and spacing

- [ ] 200% browser zoom: no content lost
- [ ] Text-spacing bookmarklet (line-height 1.5, letter 0.12em, word 0.16em, paragraph 2em): no clipping

## Content

- [ ] Every date is the real publication date
- [ ] No text the content-integrity reviewer flagged remains
- [ ] Links to the old site (for merged/archived pages) work
