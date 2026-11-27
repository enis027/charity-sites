"""Accessible palette generation for charity-sites.

Takes the organisation's brand colours (usually extracted from its logo) and
derives a full token set whose text/background pairs meet WCAG 2.2 AA.
Standard library only.
"""
from __future__ import annotations

import colorsys

WHITE = "#FFFFFF"


def hex_to_rgb(h: str) -> tuple[float, float, float]:
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f"not a hex colour: {h!r}")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def rgb_to_hex(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{round(max(0.0, min(1.0, c)) * 255):02X}" for c in rgb)


def luminance(h: str) -> float:
    def lin(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = hex_to_rgb(h)
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def mix(a: str, b: str, t: float) -> str:
    """Linear mix in sRGB: t=0 -> a, t=1 -> b."""
    ra, rb = hex_to_rgb(a), hex_to_rgb(b)
    return rgb_to_hex(tuple(x + (y - x) * t for x, y in zip(ra, rb)))  # type: ignore[arg-type]


def _with_lightness(h: str, l: float) -> str:
    r, g, b = hex_to_rgb(h)
    hh, _, s = colorsys.rgb_to_hls(r, g, b)
    return rgb_to_hex(colorsys.hls_to_rgb(hh, max(0.0, min(1.0, l)), s))


def darken_until(h: str, bg: str, target: float) -> str:
    """Lower HSL lightness (keeping hue and saturation) until contrast >= target."""
    if contrast(h, bg) >= target:
        return h.upper()
    r, g, b = hex_to_rgb(h)
    _, l, _ = colorsys.rgb_to_hls(r, g, b)
    lo, hi = 0.0, l
    for _ in range(40):
        mid = (lo + hi) / 2
        if contrast(_with_lightness(h, mid), bg) >= target:
            lo = mid
        else:
            hi = mid
    out = _with_lightness(h, lo)
    if contrast(out, bg) < target:  # extremely saturated edge case
        out = "#000000"
    return out


def darken_until_all(h: str, bgs: list[str], target: float) -> str:
    """Darken until the colour meets `target` against every background in `bgs`."""
    out = h
    for _ in range(3):
        for bg in bgs:
            out = darken_until(out, bg, target)
    return out


def hue_distance(a: str, b: str) -> float:
    d = abs(hue_deg(a) - hue_deg(b)) % 360
    return min(d, 360 - d)


def tint(h: str, amount: float = 0.92) -> str:
    return mix(h, WHITE, amount)


def saturation(h: str) -> float:
    r, g, b = hex_to_rgb(h)
    return colorsys.rgb_to_hls(r, g, b)[2]


def hue_deg(h: str) -> float:
    r, g, b = hex_to_rgb(h)
    return colorsys.rgb_to_hls(r, g, b)[0] * 360


def pick_roles(colors: list[str]) -> dict[str, str]:
    """Assign brand colours to roles.

    primary: darkest saturated colour (headings, header, footer)
    accent:  most saturated remaining colour (decorative, links after darkening)
    donate:  warmest strong colour (red/orange family) if present, else a safe red
    """
    cs = [c.upper() for c in colors if c]
    if not cs:
        cs = ["#1F3A5F"]
    chroma = [c for c in cs if saturation(c) > 0.2] or cs
    primary = min(chroma, key=luminance)
    rest = [c for c in chroma if c != primary] or [primary]
    warm = [c for c in rest if (hue_deg(c) <= 30 or hue_deg(c) >= 330) and saturation(c) > 0.45]
    # Donate prefers the reddest brand colour (closest hue to 0°), then the most saturated.
    donate = min(warm, key=lambda c: (min(hue_deg(c), 360 - hue_deg(c)), -saturation(c))) if warm else "#C8362B"
    accent_pool = [c for c in rest if c != donate and hue_distance(c, donate) >= 30] or [primary]
    def accent_score(c: str) -> float:
        h = hue_deg(c)
        return saturation(c) - (0.5 if 40 < h < 75 else 0.0)  # yellows make poor accents/links
    accent = max(accent_pool, key=accent_score)
    return {"primary": primary, "accent": accent, "donate": donate}


def build_palette(brand: dict) -> dict[str, str]:
    """brand = {"colors": [...]} or explicit {"primary","accent","donate"}."""
    roles = pick_roles(brand.get("colors", []))
    for k in ("primary", "accent", "donate"):
        if brand.get(k):
            roles[k] = brand[k].upper()
    accent = roles["accent"]
    donate = darken_until(roles["donate"], WHITE, 4.5)  # white label on donate button
    primary_target = 7.0
    if hue_distance(roles["primary"], donate) < 25 and saturation(roles["primary"]) > 0.2:
        # Brand is a single warm colour: keep the bright shade for Donate and use a
        # deep shade of the same hue for header/footer/headings so they stay distinct.
        primary_target = 12.0
    primary = darken_until(roles["primary"], WHITE, primary_target)
    donate_hover = darken_until(donate, WHITE, contrast(donate, WHITE) + 0.8)
    # Neutral grey tinted towards the primary hue so the page feels related to the brand.
    neutral_base = mix(primary, "#808080", 0.85)
    light_surfaces = [WHITE, mix(neutral_base, WHITE, 0.95), tint(primary, 0.94), tint(accent, 0.9)]
    # Links use the accent only when it is a clear, non-warning hue. Reds read as errors,
    # yellows/oranges turn muddy brown when darkened, greys look disabled.
    h = hue_deg(accent)
    accent_ok = saturation(accent) >= 0.3 and not (h <= 20 or h >= 330) and not (20 < h < 75) and accent != donate
    link = darken_until_all(accent if accent_ok else primary, light_surfaces, 4.5)
    p = {
        "brand-primary": primary,
        "brand-primary-hover": mix(primary, "#000000", 0.3) if contrast(primary, WHITE) < 12 else mix(primary, WHITE, 0.15),
        "brand-accent": accent,
        "accent-strong": darken_until_all(accent, light_surfaces, 3.0),
        "brand-donate": donate,
        "brand-donate-hover": donate_hover,
        "link": link,
        "tint-primary": tint(primary, 0.94),
        "tint-accent": tint(accent, 0.9),
        "tint-donate": tint(donate, 0.92),
        "surface": WHITE,
        "surface-subtle": mix(neutral_base, WHITE, 0.95),
        "surface-muted": mix(neutral_base, WHITE, 0.9),
        "border": mix(neutral_base, WHITE, 0.78),
        "border-input": darken_until(neutral_base, WHITE, 3.0),
        "text-body": darken_until_all(mix(neutral_base, "#000000", 0.7), light_surfaces, 12.0),
        "text-secondary": darken_until_all(neutral_base, light_surfaces, 4.6),
        "success": "#276B43", "success-tint": "#E8F4EC",
        "warning": "#8A5300", "warning-tint": "#FFF4E0",
        "error": "#B3261E", "error-tint": "#FDECEA",
    }
    p["text-heading"] = primary
    return p


# Pairs that must pass; (foreground token, background token, minimum ratio, purpose)
REQUIRED_PAIRS = [
    ("text-body", "surface", 4.5, "body text on page"),
    ("text-body", "surface-subtle", 4.5, "body text on alternate sections"),
    ("text-heading", "surface", 4.5, "headings"),
    ("text-secondary", "surface", 4.5, "captions/dates"),
    ("text-secondary", "surface-subtle", 4.5, "captions on alternate sections"),
    ("link", "surface", 4.5, "links"),
    ("link", "surface-subtle", 4.5, "links on alternate sections"),
    ("surface", "brand-primary", 4.5, "white text on primary (header/footer/buttons)"),
    ("surface", "brand-donate", 4.5, "white label on donate button"),
    ("surface", "brand-donate-hover", 4.5, "white label on donate hover"),
    ("text-heading", "tint-primary", 4.5, "headings on tinted bands"),
    ("text-body", "tint-accent", 4.5, "body on accent tint"),
    ("border-input", "surface", 3.0, "input borders (non-text contrast)"),
    ("brand-primary", "surface", 3.0, "focus ring"),
    ("accent-strong", "surface", 3.0, "icons (non-text contrast)"),
    ("accent-strong", "surface-subtle", 3.0, "icons on alternate sections"),
    ("error", "surface", 4.5, "error text"),
    ("error", "error-tint", 4.5, "error text on error alert"),
    ("success", "success-tint", 4.5, "success text on success alert"),
    ("warning", "warning-tint", 4.5, "warning text on warning alert"),
]


def audit(p: dict[str, str]) -> list[dict]:
    out = []
    for fg, bg, minimum, purpose in REQUIRED_PAIRS:
        ratio = contrast(p[fg], p[bg])
        out.append({"fg": fg, "bg": bg, "ratio": round(ratio, 2), "min": minimum, "ok": ratio >= minimum, "purpose": purpose})
    return out


def tokens_css(p: dict[str, str], fonts: dict) -> str:
    lines = ["/* Generated by charity-sites palette.py — edit site.json brand colours, not this file. */", ":root {"]
    for k, v in p.items():
        lines.append(f"  --c-{k}: {v};")
    heading = fonts.get("heading_stack", "Georgia, serif")
    body = fonts.get("body_stack", "system-ui, sans-serif")
    lines += [
        f"  --font-heading: {heading};",
        f"  --font-body: {body};",
        "  --space-1: 4px; --space-2: 8px; --space-3: 12px; --space-4: 16px; --space-5: 20px; --space-6: 24px;",
        "  --space-8: 32px; --space-10: 40px; --space-12: 48px; --space-16: 64px; --space-20: 80px; --space-24: 96px;",
        "  --radius-sm: 4px; --radius-md: 8px; --radius-lg: 12px; --radius-xl: 16px; --radius-2xl: 24px; --radius-full: 999px;",
        "  --size-touch: 44px; --size-control: 48px; --size-control-lg: 56px;",
        "  --container: 1200px; --container-text: 720px;",
        "  --shadow-card: 0 2px 8px rgb(0 0 0 / .06), 0 8px 24px -4px rgb(0 0 0 / .06);",
        "  --shadow-card-hover: 0 12px 32px -6px rgb(0 0 0 / .12);",
        "  --shadow-sticky: 0 -4px 16px rgb(0 0 0 / .14);",
        "  --shadow-dropdown: 0 8px 24px rgb(0 0 0 / .14);",
        "}",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    import json
    import sys
    brand = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {"colors": ["#22274F", "#1D9AD7", "#DB372C"]}
    pal = build_palette(brand)
    print(json.dumps(pal, indent=2))
    for row in audit(pal):
        print(("PASS" if row["ok"] else "FAIL"), f'{row["ratio"]:>5}', f'>= {row["min"]}', row["purpose"])
