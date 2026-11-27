# Photography selection

Photos come **only from the organisation's own website** (images downloaded by `crawl.py` into `audit/images/`). If the operator supplies originals from the organisation, use those. Do not scrape social networks; do not use stock photos of people; do not generate people with AI.

## Step 1: look at every candidate

Open each image in `audit/images/` (the audit report lists them by size). For each, decide:

| Question | Keep if | Reject if |
|---|---|---|
| Is it authentic? | Real event, real members, the organisation's own premises, logo or banners visible, consistent faces across photos | Watermark of a stock agency, studio lighting with generic models, the same image appears on unrelated sites, "Teşekkürler/Thank you" signs held by models |
| Is it dignified? | People active, together, at eye level, faces relaxed | Pity framing, isolated person in a wheelchair, close-up of medical devices, crying children, crowd protest shots used as decoration |
| Is it text-free? | Plain photo | Social-media graphic with text baked in (use only as a news thumbnail, with alt text that repeats the text) |
| Consent risk? | Adults, or children in a group at a public event the organisation organised | Identifiable child alone, faces covered with emoji/blur (signals no consent — do not use) |

## Step 2: resolution thresholds

| Use | Minimum source width | Notes |
|---|---|---|
| Hero (desktop 4:5 crop ~ 600 × 750 rendered, 2× = 1200 × 1500) | **1200 px on the cropped side** | Below this, use the labelled placeholder and write a photography brief. |
| Story/photo card (~ 420 px rendered) | 800 px | |
| News thumbnail 16:9 (~ 384 px rendered) | 640 px | The current site's thumbnails are often 340 px: acceptable only as thumbnails. |
| Team avatar (112 px rendered) | 224 px | |

### Upscaling

Allowed only to reach the card/thumbnail thresholds, at most **2×**, with a model meant for photos (e.g. Upscayl / Real-ESRGAN `realesrgan-x4plus` run at 2×). Check faces after upscaling: if they look waxy or altered, use the original. Never upscale for the hero, never upscale a face that becomes recognisably different, and record every upscaled file in `SOURCES.md`.

If Upscayl's CLI (`upscayl-bin` / `realesrgan-ncnn-vulkan`) is not installed, do not install software without the operator's permission; list the images that would benefit instead.

## Step 3: crops and alt text

- Desktop hero 4:5, mobile hero 5:4 (same image, different `object-position` if needed — set `photo.position` in site.json, e.g. `"50% 30%"`).
- Keep faces in the central 70%. Never crop through faces or hands holding something meaningful.
- Alt text describes what matters for the page in the site language, in one sentence: who, doing what, where/when if known. Decorative images get `alt=""`. Never put names of children in alt text.
- Captions carry the event and date when the source gives them.

## Step 4: photography brief (when the hero is missing)

Write this into `OPEN-QUESTIONS.md` in the organisation's language:
- Scene: members and families together at a real association activity, eye level, daylight.
- Avoid: hospital framing, pity angles, banners covering the frame.
- Format: landscape original ≥ 2400 × 1600 px, subject in the central 70% so both crops work.
- Consent: written guardian consent for every identifiable child; record naming wishes.
- Credit line the organisation wants.
