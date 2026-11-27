"""HTML rendering for charity-sites. Standard library only.

Every visible string comes from site.json (content, with sources) or from the
i18n file for the site language (interface labels). Nothing is invented here.
"""
from __future__ import annotations

import html
import json
import re
from datetime import date

# ---------------------------------------------------------------- utilities

def esc(s) -> str:
    return html.escape("" if s is None else str(s), quote=True)


_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_BOLD = re.compile(r"\*\*(.+?)\*\*")


def md(s: str) -> str:
    """Escape text, then allow **bold** and [label](url) only."""
    out = esc(s)
    out = _BOLD.sub(r"<strong>\1</strong>", out)

    def link(m):
        label, url = m.group(1), m.group(2)
        ext = url.startswith(("http://", "https://"))
        rel = ' rel="noopener"' if ext else ""
        return f'<a href="{url}"{rel}>{label}</a>'
    return _LINK.sub(link, out)


def t(ui: dict, key: str, **kw) -> str:
    s = ui.get(key, key)
    for k, v in kw.items():
        s = s.replace("{" + k + "}", str(v))
    return s


def is_external(href: str) -> bool:
    return href.startswith(("http://", "https://", "mailto:", "tel:"))


def a(href: str, label: str, cls: str = "", attrs: str = "") -> str:
    c = f' class="{cls}"' if cls else ""
    return f'<a href="{esc(href)}"{c}{attrs}>{label}</a>'


ICONS = {
    "arrow-right": '<path d="M5 12h14"/><path d="M13 6l6 6-6 6"/>',
    "arrow-left": '<path d="M19 12H5"/><path d="M11 6l-6 6 6 6"/>',
    "chevron-down": '<path d="M6 9l6 6 6-6"/>',
    "menu": '<path d="M4 7h16"/><path d="M4 12h16"/><path d="M4 17h16"/>',
    "close": '<path d="M6 6l12 12"/><path d="M18 6L6 18"/>',
    "copy": '<rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/>',
    "check": '<path d="M5 12l5 5L20 7"/>',
    "check-circle": '<circle cx="12" cy="12" r="9"/><path d="M8.5 12.5l2.5 2.5 5-5"/>',
    "alert-circle": '<circle cx="12" cy="12" r="9"/><path d="M12 8v5"/><path d="M12 16h.01"/>',
    "alert-triangle": '<path d="M12 3l10 18H2L12 3z"/><path d="M12 10v4"/><path d="M12 18h.01"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5"/><path d="M12 8h.01"/>',
    "phone": '<path d="M5 4h3l2 5-2.5 1.5a11 11 0 0 0 6 6L15 14l5 2v3a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    "map-pin": '<path d="M12 22s7-6.5 7-12a7 7 0 1 0-14 0c0 5.5 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/>',
    "heart": '<path d="M12 21s-7-4.6-9.5-9A5.5 5.5 0 0 1 12 6a5.5 5.5 0 0 1 9.5 6C19 16.4 12 21 12 21z"/>',
    "external-link": '<path d="M14 4h6v6"/><path d="M20 4l-9 9"/><path d="M19 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h5"/>',
    "download": '<path d="M12 4v12"/><path d="M7 11l5 5 5-5"/><path d="M4 20h16"/>',
    "file-text": '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4"/><path d="M9 13h6"/><path d="M9 17h6"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18"/><path d="M8 3v4"/><path d="M16 3v4"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M3 20a6 6 0 0 1 12 0"/><circle cx="17" cy="9" r="2.5"/><path d="M15.5 15.5A5 5 0 0 1 21 20"/>',
    "user-plus": '<circle cx="10" cy="8" r="4"/><path d="M2 21a8 8 0 0 1 16 0"/><path d="M19 8v6"/><path d="M16 11h6"/>',
    "book-open": '<path d="M12 6c-2-2-5-2-9-2v14c4 0 7 0 9 2 2-2 5-2 9-2V4c-4 0-7 0-9 2z"/><path d="M12 6v14"/>',
    "shield-check": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3z"/><path d="M9 12l2 2 4-4"/>',
    "play": '<path d="M8 5l12 7-12 7z"/>',
    "stethoscope": '<path d="M6 3v6a5 5 0 0 0 10 0V3"/><path d="M11 14v3a4 4 0 0 0 8 0v-3"/><circle cx="19" cy="11" r="2"/>',
    "building": '<rect x="4" y="3" width="16" height="18" rx="1"/><path d="M9 7h2"/><path d="M13 7h2"/><path d="M9 11h2"/><path d="M13 11h2"/><path d="M10 21v-4h4v4"/>',
    "handshake": '<path d="M3 10l4-4 5 2 5-2 4 4"/><path d="M12 8l-3.5 3.5a1.5 1.5 0 0 0 2 2.2L13 12l4 4"/><path d="M7 14l3 3"/><path d="M15 18l-1 1"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3a14 14 0 0 1 0 18"/><path d="M12 3a14 14 0 0 0 0 18"/>',
    "home": '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>',
    "megaphone": '<path d="M3 11v2a1 1 0 0 0 1 1h2l5 4V6L6 10H4a1 1 0 0 0-1 1z"/><path d="M15 9a3 3 0 0 1 0 6"/><path d="M18 6a7 7 0 0 1 0 12"/>',
    "lock": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
    "facebook": '<path fill="currentColor" stroke="none" d="M14 8h2.5V4.5H14c-2.5 0-4 1.6-4 4V11H7.5v3.5H10V21h3.5v-6.5H16l.5-3.5h-3V9c0-.6.4-1 1-1z"/>',
    "instagram": '<rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.2" cy="6.8" r="1" fill="currentColor" stroke="none"/>',
    "x": '<path d="M4 4l16 16"/><path d="M20 4L4 20"/>',
    "youtube": '<rect x="2.5" y="6" width="19" height="12" rx="4"/><path fill="currentColor" stroke="none" d="M10 9.5v5l4.5-2.5z"/>',
    "linkedin": '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M8 10v7"/><path d="M8 7v.01"/><path d="M12 17v-4a2 2 0 0 1 4 0v4"/><path d="M12 10v7"/>',
    "tiktok": '<path d="M14 4v10.5a3.5 3.5 0 1 1-3.5-3.5"/><path d="M14 4c.5 2.5 2.5 4 5 4"/>',
    "whatsapp": '<path d="M4 20l1.3-4A8 8 0 1 1 8 18.7z"/><path d="M9 9.5c.5 2 2.5 4 4.5 4.5l1-1.2 2 .9-.4 1.6c-3.6.4-7.6-3.6-7.2-7.2L10.5 7.7l.9 2-1.2 1"/>',
    "telegram": '<path d="M21 4L3 11l6 2 2 6 3-4 5 4z"/><path d="M9 13l8-6"/>',
}
DIRECTIONAL = {"arrow-right", "arrow-left"}


def icon(name: str, size: str = "", label: str | None = None) -> str:
    body = ICONS.get(name, ICONS["info"])
    cls = "icon" + (f" icon--{size}" if size else "") + (" icon--flip" if name in DIRECTIONAL else "")
    aria = f'role="img" aria-label="{esc(label)}"' if label else 'aria-hidden="true" focusable="false"'
    return f'<svg class="{cls}" viewBox="0 0 24 24" {aria}>{body}</svg>'


def fmt_date(iso: str, locale_months: list[str] | None, lang: str) -> str:
    """Format YYYY-MM-DD as '12 May 2025' style using month names from i18n if given."""
    try:
        y, m, d = (int(x) for x in iso.split("-"))
        date(y, m, d)
    except Exception:
        return esc(iso)
    if locale_months and len(locale_months) == 12:
        mon = locale_months[m - 1]
    else:
        mon = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"][m - 1]
    if lang in ("en-US",):
        return f"{mon} {d}, {y}"
    return f"{d:02d} {mon} {y}" if lang.startswith("tr") else f"{d} {mon} {y}"


def time_tag(site, iso: str) -> str:
    return f'<time datetime="{esc(iso)}">{esc(fmt_date(iso, site.get("months"), site.get("locale", site["lang"])))}</time>'


def money(site, value) -> str:
    """Format an amount with the site's currency symbol position."""
    cur = site.get("currency_display", {})
    sym = cur.get("symbol", site.get("currency", ""))
    pos = cur.get("position", "after")
    sep = cur.get("thousands", ",")
    try:
        n = int(value)
        num = f"{n:,}".replace(",", sep)
    except (TypeError, ValueError):
        num = str(value)
    return f"{sym}{num}" if pos == "before" else f"{num} {sym}"


# ---------------------------------------------------------------- page chrome

def head(site, page) -> str:
    fonts = site["fonts"]
    font_link = ""
    if fonts.get("google_css"):
        font_link = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
                     '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
                     f'<link rel="stylesheet" href="{esc(fonts["google_css"])}">\n')
    if fonts.get("self_css"):
        font_link = f'<link rel="stylesheet" href="{esc(fonts["self_css"])}">\n'
    robots = '<meta name="robots" content="noindex, nofollow">\n' if site.get("preview") else ""
    title = page["title"] if page["slug"] == "index" else f'{page["title"]} · {site["org"]["short_name"]}'
    canonical = ""
    if site.get("base_url") and not site.get("preview"):
        path = "" if page["slug"] == "index" else f'{page["slug"]}.html'
        canonical = f'<link rel="canonical" href="{esc(site["base_url"].rstrip("/") + "/" + path)}">\n'
    og_image = site["org"].get("share_image", "")
    og = (f'<meta property="og:title" content="{esc(title)}">\n'
          f'<meta property="og:description" content="{esc(page.get("description", ""))}">\n'
          f'<meta property="og:type" content="website">\n')
    if og_image:
        og += f'<meta property="og:image" content="{esc(og_image)}">\n'
    body_cls = "has-sticky" if site.get("sticky_donate") and page.get("layout") != "donate" else ""
    return (f'<!DOCTYPE html>\n<html lang="{esc(site["lang"])}" dir="{esc(site.get("dir", "ltr"))}">\n<head>\n'
            '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{esc(title)}</title>\n<meta name="description" content="{esc(page.get("description", ""))}">\n'
            f'{robots}{canonical}{og}'
            f'<link rel="icon" href="{esc(site["org"].get("favicon", site["org"]["logo"]))}">\n'
            f'{font_link}<link rel="stylesheet" href="css/tokens.css">\n<link rel="stylesheet" href="css/styles.css">\n'
            f'</head>\n<body class="{body_cls}">\n'
            f'<a class="skip-link" href="#main">{esc(t(site["ui"], "skip_link"))}</a>\n')


def preview_banner(site) -> str:
    if not site.get("preview"):
        return ""
    ui = site["ui"]
    return (f'<div class="preview-banner" role="note"><div class="container">{icon("alert-triangle")}'
            f'<p><strong>{esc(t(ui, "preview_title"))}.</strong> {esc(t(ui, "preview_text", org=site["org"]["name"]))}</p></div></div>\n')


def header(site, page) -> str:
    ui = site["ui"]
    org = site["org"]
    active = page.get("nav_active", "")
    items, drawer = [], []
    for item in site["nav"]:
        label, href, kids = item["label"], item.get("href", "#"), item.get("children") or []
        is_active = active == label
        if kids:
            subs = "".join(f'<li>{a(k["href"], esc(k["label"]))}</li>' for k in kids)
            cls = ' class="is-active"' if is_active else ""
            items.append(f'<li{cls}><button type="button" aria-expanded="false" aria-haspopup="true">{esc(label)} {icon("chevron-down", "sm")}</button><ul class="submenu list-reset">{subs}</ul></li>')
            drawer.append(f'<li><details><summary>{esc(label)} {icon("chevron-down", "md")}</summary><ul class="list-reset">{subs}</ul></details></li>')
        else:
            cur = ' aria-current="page"' if is_active else ""
            items.append(f'<li>{a(href, esc(label), attrs=cur)}</li>')
            drawer.append(f'<li>{a(href, esc(label), attrs=cur)}</li>')
    member = site.get("header", {}).get("member_cta")
    member_btn = a(member["href"], esc(member["label"]), "btn btn--ghost") if member else ""
    member_drawer = a(member["href"], esc(member["label"]), "btn btn--secondary btn--block") if member else ""
    donate = a(site["donate_href"], esc(t(ui, "donate")), "btn btn--donate")
    logo = f'<img src="{esc(org["logo"])}" alt="{esc(org.get("logo_alt") or org["name"])}" width="{org.get("logo_width", 200)}" height="{org.get("logo_height", 60)}">'
    contact = site.get("contact", {})
    quick = ""
    if contact.get("phone"):
        quick = f'<div class="drawer-contact">{icon("phone", "md")} {a(contact.get("phone_href") or "tel:" + re.sub(r"[^+0-9]", "", contact["phone"]), esc(contact["phone"]))}</div>'
    return (preview_banner(site) +
            f'<header class="site-header">\n<div class="container">\n'
            f'<a class="brand" href="index.html">{logo}</a>\n'
            f'<nav class="nav" aria-label="{esc(t(ui, "main_menu"))}"><ul class="list-reset">{"".join(items)}</ul></nav>\n'
            f'<div class="header-actions">{member_btn}{donate}'
            f'<button class="menu-toggle" type="button" aria-expanded="false" aria-controls="drawer" '
            f'data-label-open="{esc(t(ui, "menu_open"))}" data-label-close="{esc(t(ui, "menu_close"))}" aria-label="{esc(t(ui, "menu_open"))}">'
            f'<span class="icon-open">{icon("menu")}</span><span class="icon-close" hidden>{icon("close")}</span></button></div>\n'
            f'</div>\n<nav class="drawer" id="drawer" aria-label="{esc(t(ui, "mobile_menu"))}"><ul class="list-reset">{"".join(drawer)}</ul>'
            f'<div class="drawer-actions">{a(site["donate_href"], esc(t(ui, "donate")), "btn btn--donate btn--block")}{member_drawer}</div>{quick}</nav>\n'
            f'</header>\n<main id="main" tabindex="-1">\n')


SOCIAL_ICON = {"facebook": "facebook", "instagram": "instagram", "x": "x", "twitter": "x", "youtube": "youtube",
               "linkedin": "linkedin", "tiktok": "tiktok", "whatsapp": "whatsapp", "telegram": "telegram"}
SOCIAL_NAME = {"facebook": "Facebook", "instagram": "Instagram", "x": "X", "twitter": "X", "youtube": "YouTube",
               "linkedin": "LinkedIn", "tiktok": "TikTok", "whatsapp": "WhatsApp", "telegram": "Telegram"}


def social_links(site, cls="social") -> str:
    out = []
    for s in site.get("contact", {}).get("social", []):
        net = s["network"].lower()
        out.append(f'<a href="{esc(s["url"])}" rel="noopener" aria-label="{esc(s.get("label") or SOCIAL_NAME.get(net, net))}">{icon(SOCIAL_ICON.get(net, "globe"), "md")}</a>')
    return f'<div class="{cls}">{"".join(out)}</div>' if out else ""


def footer(site, page) -> str:
    ui = site["ui"]
    org = site["org"]
    f = site.get("footer", {})
    cols = "".join(
        f'<div><h2>{esc(c["title"])}</h2><ul class="list-reset">' +
        "".join(f'<li>{a(l["href"], esc(l["label"]))}</li>' for l in c["links"]) + "</ul></div>"
        for c in f.get("columns", []))
    contact = site.get("contact", {})
    clist = []
    if contact.get("address"):
        clist.append(f'<li>{icon("map-pin", "md")}<span>{esc(contact["address"])}</span></li>')
    if contact.get("phone"):
        clist.append(f'<li>{icon("phone", "md")}{a(contact.get("phone_href") or "tel:" + re.sub(r"[^+0-9]", "", contact["phone"]), esc(contact["phone"]))}</li>')
    if contact.get("email"):
        clist.append(f'<li>{icon("mail", "md")}{a("mailto:" + contact["email"], esc(contact["email"]))}</li>')
    nl = f.get("newsletter")
    news_html = ""
    if nl and (nl.get("action") or site.get("preview")):
        demo = "" if nl.get("action") else ' data-demo="true"'
        news_html = (f'<form class="newsletter" action="{esc(nl.get("action") or "#")}" method="post"{demo} data-newsletter>'
                     f'<h2>{esc(nl.get("title") or t(ui, "newsletter"))}</h2>'
                     + (f'<p class="small">{esc(nl["text"])}</p>' if nl.get("text") else "") +
                     f'<label for="nl-email">{esc(t(ui, "email_label"))}</label>'
                     f'<div class="row"><input id="nl-email" type="email" name="email" autocomplete="email" required placeholder="{esc(t(ui, "email_placeholder"))}">'
                     f'<button class="btn btn--inverse" type="submit">{esc(t(ui, "subscribe"))}</button></div>'
                     f'<p class="newsletter-status" role="status" aria-live="polite"></p></form>')
    logo_rev = org.get("logo_reverse")
    logo_html = f'<img class="footer-logo" src="{esc(logo_rev)}" alt="{esc(org["name"])}" width="{org.get("logo_width", 200)}" height="{org.get("logo_height", 60)}">' if logo_rev else f'<p class="h4">{esc(org["name"])}</p>'
    legal = "".join(f'<li>{a(l["href"], esc(l["label"]))}</li>' for l in f.get("legal_links", []))
    year = f.get("copyright_year") or date.today().year
    sticky = ""
    if site.get("sticky_donate") and page.get("layout") != "donate":
        sticky = (f'<div class="sticky-donate"><div class="text"><b>{esc(site.get("sticky_title") or t(ui, "sticky_title"))}</b>'
                  f'<span>{esc(t(ui, "sticky_text"))}</span></div>{a(site["donate_href"], esc(t(ui, "donate")), "btn btn--donate")}</div>\n')
    return (f'</main>\n<footer class="site-footer" style="--footer-cols:{max(1, len(f.get("columns", [])))}">\n<div class="container">\n<div class="cols">\n'
            f'<div>{logo_html}' + (f'<p class="footer-about">{esc(f["about"])}</p>' if f.get("about") else "") + social_links(site) + '</div>\n'
            f'{cols}\n<div><h2>{esc(t(ui, "contact"))}</h2><ul class="list-reset contact-list">{"".join(clist)}</ul>{news_html}</div>\n'
            f'</div>\n<div class="legal"><p>© {year} {esc(org["name"])}. {esc(t(ui, "rights"))}</p><ul class="list-reset">{legal}</ul></div>\n'
            f'</div>\n</footer>\n{sticky}<script src="js/main.js" defer></script>\n</body>\n</html>\n')


# ---------------------------------------------------------------- building blocks

def btn(site, b: dict) -> str:
    style = b.get("style", "primary")
    label = esc(b["label"])
    if b.get("icon"):
        label += " " + icon(b["icon"], "md")
    return a(b["href"], label, f"btn btn--{style}")


def btns(site, items) -> str:
    return f'<div class="btn-row">{"".join(btn(site, b) for b in items)}</div>' if items else ""


def link_arrow(href: str, label: str) -> str:
    return a(href, f'{esc(label)} {icon("arrow-right", "md")}', "link")


def section_head(sec: dict, row_link: dict | None = None, h: str = "h2") -> str:
    parts = []
    if sec.get("overline"):
        parts.append(f'<p class="overline">{esc(sec["overline"])}</p>')
    if sec.get("title"):
        hid = f' id="{esc(sec["id"])}-h"' if sec.get("id") else ""
        parts.append(f"<{h}{hid}>{esc(sec['title'])}</{h}>")
    if sec.get("lead"):
        parts.append(f'<p class="lead">{md(sec["lead"])}</p>')
    if not parts:
        return ""
    inner = "".join(parts)
    if row_link:
        return f'<div class="section-head section-head--row"><div class="stack">{inner}</div>{link_arrow(row_link["href"], row_link["label"])}</div>'
    return f'<div class="section-head">{inner}</div>'


def wrap(sec: dict, inner: str, extra_cls: str = "") -> str:
    tone = {"subtle": "section--subtle", "tint": "section--tint", "accent": "section--accent", "brand": "section--brand"}.get(sec.get("tone", ""), "")
    sid = f' id="{esc(sec["id"])}"' if sec.get("id") else ""
    labelled = f' aria-labelledby="{esc(sec["id"])}-h"' if sec.get("id") and sec.get("title") else ""
    return f'<section class="section {tone} {extra_cls}"{sid}{labelled}><div class="container">{inner}</div></section>\n'


def img_tag(img: dict, eager: bool = False) -> str:
    w = img.get("width", "")
    h = img.get("height", "")
    dims = f' width="{w}" height="{h}"' if w and h else ""
    load = ' fetchpriority="high"' if eager else ' loading="lazy" decoding="async"'
    return f'<img src="{esc(img["src"])}" alt="{esc(img.get("alt", ""))}"{dims}{load}>'


# ---------------------------------------------------------------- sections

def s_hero(site, sec):
    ui = site["ui"]
    facts = "".join(f'<li>{icon(f.get("icon", "check"), "md")}<span>{esc(f["text"])}</span></li>' for f in sec.get("facts", []))
    photo = ""
    p = sec.get("photo")
    if p and p.get("src"):
        cap = f'<figcaption>{esc(p["caption"])}</figcaption>' if p.get("caption") else ""
        img = img_tag(p, eager=True)
        if p.get("position"):
            img = img.replace("<img ", f'<img style="object-position:{esc(p["position"])}" ', 1)
        photo = f'<figure class="hero-photo">{img}{cap}</figure>'
    elif sec.get("photo_placeholder", True):
        photo = (f'<div class="hero-photo photo-placeholder" role="img" aria-label="{esc(t(ui, "photo_placeholder"))}">'
                 f'{icon("users")}<p class="small">{esc(t(ui, "photo_placeholder"))}</p></div>')
    cls = "hero" + ("" if photo else " hero--text-only")
    return (f'<section class="{cls}" aria-labelledby="hero-h"><div class="container"><div class="hero-copy">'
            + (f'<p class="overline">{esc(sec["overline"])}</p>' if sec.get("overline") else "")
            + f'<h1 id="hero-h" class="display">{esc(sec["title"])}</h1>'
            + (f'<p class="lead">{md(sec["lead"])}</p>' if sec.get("lead") else "")
            + btns(site, sec.get("ctas", []))
            + (f'<ul class="facts list-reset">{facts}</ul>' if facts else "")
            + f'</div>{photo}</div></section>\n')


def s_pillars(site, sec):
    items = "".join(
        f'<li class="pillar"><span class="pillar-num" aria-hidden="true">{i + 1:02d}</span><div><h3>{esc(it["title"])}</h3><p>{md(it["text"])}</p></div></li>'
        for i, it in enumerate(sec["items"]))
    return wrap(sec, section_head(sec, sec.get("link")) + f'<ol class="pillars list-reset">{items}</ol>')


def s_quote_band(site, sec):
    photo = ""
    p = sec.get("photo")
    if p and p.get("src"):
        cap = f'<figcaption>{esc(p["caption"])}</figcaption>' if p.get("caption") else ""
        photo = f'<figure class="photo-card">{img_tag(p)}{cap}</figure>'
    body = (f'<div class="stack">' + (f'<p class="overline">{esc(sec["overline"])}</p>' if sec.get("overline") else "")
            + f'<blockquote><p class="h3"{" id=" + chr(34) + esc(sec["id"]) + "-h" + chr(34) if sec.get("id") else ""}>{esc(sec["quote"])}</p>'
            + (f'<footer class="caption">{esc(sec["attribution"])}</footer>' if sec.get("attribution") else "") + '</blockquote>'
            + (f'<p>{md(sec["text"])}</p>' if sec.get("text") else "")
            + (btns(site, [sec["cta"]]) if sec.get("cta") else "") + '</div>')
    sec = dict(sec, tone=sec.get("tone", "brand"))
    return wrap(sec, body + photo, "quote-band")


def s_cards(site, sec):
    cards = []
    for it in sec["items"]:
        ic = f'<span class="card-icon">{icon(it.get("icon", "book-open"))}</span>' if it.get("icon", True) else ""
        link = link_arrow(it["href"], it.get("link_label") or t(site["ui"], "read_more")) if it.get("href") else ""
        hl = "h3" if sec.get("title") else "h2"
        cards.append(f'<article class="card">{ic}<{hl} class="h4">{esc(it["title"])}</{hl}>' + (f'<p class="small">{md(it["text"])}</p>' if it.get("text") else "") + f'{link}</article>')
    cols = sec.get("columns", 3 if len(cards) % 3 == 0 else 4 if len(cards) >= 4 else 2)
    quick = ""
    if sec.get("quick_links"):
        quick = '<ul class="quick-links list-reset">' + "".join(f'<li>{link_arrow(q["href"], q["label"])}</li>' for q in sec["quick_links"]) + "</ul>"
    return wrap(sec, section_head(sec, sec.get("link")) + f'<div class="grid grid-{cols}">{"".join(cards)}</div>{quick}')


def documents_list(site, items) -> str:
    ui = site["ui"]
    out = []
    for d in items:
        out.append(f'<div class="doc-card"><span class="doc-icon">{icon("file-text")}</span><div class="info"><h3>{esc(d["title"])}</h3>'
                   + (f'<p class="caption">{esc(d["meta"])}</p>' if d.get("meta") else "") + '</div>'
                   + a(d["href"], f'{icon("download", "md")} {esc(t(ui, "download"))}<span class="visually-hidden">: {esc(d["title"])}</span>', "btn btn--secondary btn--sm")
                   + '</div>')
    return f'<div class="stack">{"".join(out)}</div>'


def s_documents(site, sec):
    return wrap(sec, section_head(sec, sec.get("link")) + documents_list(site, sec["items"]))


def logos_grid(items) -> str:
    out = []
    for it in items:
        logo = f'<img src="{esc(it["logo"])}" alt="" loading="lazy">' if it.get("logo") else f'<span aria-hidden="true">{icon("building")}</span>'
        inner = f'{logo}<span>{esc(it["name"])}</span>'
        out.append(f'<li>{a(it["href"], inner, "logo-tile")}</li>' if it.get("href") else f'<li class="logo-tile">{inner}</li>')
    return f'<ul class="grid grid-3 list-reset">{"".join(out)}</ul>'


def s_logos(site, sec):
    return wrap(sec, section_head(sec, sec.get("link")) + logos_grid(sec["items"]))


def news_card(site, it) -> str:
    ui = site["ui"]
    thumb = f'<div class="thumb">{img_tag({"src": it["image"], "alt": "", "width": it.get("image_width", 640), "height": it.get("image_height", 360)})}</div>' if it.get("image") else ""
    cat = f'<span class="tag">{esc(it["category"])}</span>' if it.get("category") else ""
    return (f'<article class="card news-card">{thumb}<div class="body"><div class="meta">{cat}{time_tag(site, it["date"])}</div>'
            f'<h3 class="h4">{a(it["href"], esc(it["title"]))}</h3>'
            + (f'<p class="small">{esc(it["excerpt"])}</p>' if it.get("excerpt") else "")
            + f'<span class="read-more" aria-hidden="true">{esc(t(ui, "read_article"))}</span></div></article>')


def s_news(site, sec):
    cards = "".join(news_card(site, it) for it in sec["items"])
    return wrap(sec, section_head(sec, sec.get("link")) + f'<div class="grid grid-3">{cards}</div>')


def s_cta(site, sec):
    sec = dict(sec, tone=sec.get("tone", "tint"))
    inner = ((f'<p class="overline">{esc(sec["overline"])}</p>' if sec.get("overline") else "")
             + f'<h2{" id=" + chr(34) + esc(sec["id"]) + "-h" + chr(34) if sec.get("id") else ""}>{esc(sec["title"])}</h2>'
             + (f'<p class="lead text-col">{md(sec["lead"])}</p>' if sec.get("lead") else "")
             + btns(site, sec.get("ctas", []))
             + (f'<p class="caption text-col">{md(sec["note"])}</p>' if sec.get("note") else ""))
    return wrap(sec, inner, "closing")


def prose_blocks(site, blocks) -> str:
    out = []
    for b in blocks:
        k = b["type"]
        if k == "p":
            out.append(f"<p>{md(b['text'])}</p>")
        elif k in ("h2", "h3"):
            bid = f' id="{esc(b["id"])}"' if b.get("id") else ""
            out.append(f"<{k}{bid}>{esc(b['text'])}</{k}>")
        elif k in ("ul", "ol"):
            out.append(f"<{k}>" + "".join(f"<li><span>{md(i)}</span></li>" for i in b["items"]) + f"</{k}>")
        elif k == "quote":
            cite = f'<footer class="caption">{esc(b["attribution"])}</footer>' if b.get("attribution") else ""
            out.append(f"<blockquote><p>{esc(b['text'])}</p>{cite}</blockquote>")
        elif k == "figure":
            cap = f"<figcaption>{esc(b['caption'])}</figcaption>" if b.get("caption") else ""
            out.append(f"<figure>{img_tag(b)}{cap}</figure>")
        elif k == "alert":
            out.append(alert(b.get("variant", "info"), b.get("title"), b["text"]))
        elif k == "documents":
            out.append(documents_list(site, b["items"]))
        elif k == "accordion":
            out.append(accordion(b["items"]))
        elif k == "buttons":
            out.append(btns(site, b["items"]))
        elif k == "share":
            out.append(share_row(site, b))
    return "".join(out)


def alert(variant: str, title: str | None, text: str, role: str = "") -> str:
    ic = {"success": "check-circle", "warning": "alert-triangle", "error": "alert-circle"}.get(variant, "info")
    r = f' role="{role}"' if role else ""
    return (f'<div class="alert alert--{variant}"{r}>{icon(ic)}<div>' + (f"<h3>{esc(title)}</h3>" if title else "") + f"<p>{md(text)}</p></div></div>")


def accordion(items) -> str:
    return '<div class="accordion">' + "".join(
        f'<details{" open" if it.get("open") else ""}><summary><span>{esc(it["q"])}</span>{icon("chevron-down")}</summary><div class="panel-body prose"><p>{md(it["a"])}</p></div></details>'
        for it in items) + "</div>"


def s_prose(site, sec):
    return wrap(sec, section_head(sec) + f'<div class="prose text-col">{prose_blocks(site, sec["blocks"])}</div>')


def s_accordion(site, sec):
    return wrap(sec, section_head(sec, sec.get("link")) + f'<div class="text-col" style="max-width:880px">{accordion(sec["items"])}</div>')


def s_team(site, sec):
    out = []
    for m in sec["items"]:
        av = f'<span class="avatar">{img_tag({"src": m["photo"], "alt": "", "width": 224, "height": 224})}</span>' if m.get("photo") else f'<span class="avatar" aria-hidden="true">{icon("users")}</span>'
        role = f'<p class="caption">{esc(m["role"])}</p>' if m.get("role") else ""
        out.append(f'<li class="team-card">{av}<h3>{esc(m["name"])}</h3>{role}</li>')
    return wrap(sec, section_head(sec, sec.get("link")) + f'<ul class="team-grid list-reset">{"".join(out)}</ul>')


def s_chips(site, sec):
    out = []
    for c in sec["items"]:
        inner = (icon(c["icon"], "sm") if c.get("icon") else "") + esc(c["label"])
        out.append(f'<li>{a(c["href"], inner, "chip")}</li>' if c.get("href") else f'<li><span class="chip">{inner}</span></li>')
    return wrap(sec, section_head(sec, sec.get("link")) + f'<ul class="chips list-reset">{"".join(out)}</ul>')


def s_columns(site, sec):
    cols = []
    for c in sec["columns"]:
        k = c["type"]
        head = ""
        if c.get("title"):
            ic = icon(c["icon"]) if c.get("icon") else ""
            head = f'<h2 class="h3" style="display:flex;gap:12px;align-items:center">{ic}{esc(c["title"])}</h2>'
        body = (f'<p>{md(c["lead"])}</p>' if c.get("lead") else "")
        if k == "documents":
            body += documents_list(site, c["items"])
        elif k == "logos":
            body += logos_grid(c["items"])
        elif k == "prose":
            body += f'<div class="prose">{prose_blocks(site, c["blocks"])}</div>'
        elif k == "accordion":
            body += accordion(c["items"])
        if c.get("link"):
            body += f'<p>{link_arrow(c["link"]["href"], c["link"]["label"])}</p>'
        cols.append(f'<div class="stack"{" id=" + chr(34) + esc(c["id"]) + chr(34) if c.get("id") else ""}>{head}{body}</div>')
    return wrap(sec, section_head(sec) + f'<div class="grid grid-2 grid-wide">{"".join(cols)}</div>')


def share_row(site, b) -> str:
    ui = site["ui"]
    url = b.get("url", "")
    from urllib.parse import quote
    q = quote(url, safe="")
    title = quote(b.get("title", ""), safe="")
    return (f'<div class="share"><span class="h5">{esc(t(ui, "share"))}</span>'
            f'<a class="icon-btn" href="https://www.facebook.com/sharer/sharer.php?u={q}" rel="noopener" aria-label="{esc(t(ui, "share_on", network="Facebook"))}">{icon("facebook", "md")}</a>'
            f'<a class="icon-btn" href="https://twitter.com/intent/tweet?url={q}&amp;text={title}" rel="noopener" aria-label="{esc(t(ui, "share_on", network="X"))}">{icon("x", "md")}</a>'
            f'<a class="icon-btn" href="https://wa.me/?text={title}%20{q}" rel="noopener" aria-label="{esc(t(ui, "share_on", network="WhatsApp"))}">{icon("whatsapp", "md")}</a>'
            f'<a class="icon-btn" href="mailto:?subject={title}&amp;body={q}" aria-label="{esc(t(ui, "share_email"))}">{icon("mail", "md")}</a></div>')


def field(site, fid, label, kind="text", required=True, autocomplete="", inputmode="", placeholder="", hint="", options=None, err_key="err_required", err=None) -> str:
    ui = site["ui"]
    opt = "" if required else f' <span class="opt">{esc(t(ui, "optional"))}</span>'
    star = " *" if required else ""
    desc = [f"{fid}-err"]
    hint_html = ""
    if hint:
        hint_html = f'<p class="hint" id="{fid}-hint">{esc(hint)}</p>'
        desc.insert(0, f"{fid}-hint")
    attrs = (" required" if required else "") + (f' autocomplete="{autocomplete}"' if autocomplete else "") + (f' inputmode="{inputmode}"' if inputmode else "")
    ph = f' placeholder="{esc(placeholder)}"' if placeholder else ""
    db = f' aria-describedby="{" ".join(desc)}"'
    if kind == "textarea":
        ctl = f'<textarea id="{fid}" name="{fid}"{attrs}{ph}{db}></textarea>'
    elif kind == "select":
        opts = f'<option value="">{esc(t(ui, "select_placeholder"))}</option>' + "".join(f"<option>{esc(o)}</option>" for o in options or [])
        ctl = f'<select id="{fid}" name="{fid}"{attrs}{db}>{opts}</select>'
    else:
        ctl = f'<input id="{fid}" name="{fid}" type="{kind}"{attrs}{ph}{db}>'
    empty_text = err or t(ui, err_key, field=label.lower() if site["lang"] in ("en",) else label)
    err_text = t(ui, "err_email") if kind == "email" else empty_text
    return (f'<div class="field"><label for="{fid}">{esc(label)}{star}{opt}</label>{ctl}{hint_html}'
            f'<p class="error" id="{fid}-err" hidden data-msg-empty="{esc(empty_text)}" data-msg-invalid="{esc(t(ui, "err_email"))}">'
            f'{icon("alert-circle", "sm")}<span class="visually-hidden">{esc(t(ui, "error_prefix"))} </span><span class="msg">{esc(err_text)}</span></p></div>')


def s_contact(site, sec):
    ui = site["ui"]
    c = site.get("contact", {})
    items = []
    if c.get("address"):
        items.append(f'<div class="contact-item"><span class="card-icon">{icon("map-pin")}</span><div><p class="caption">{esc(t(ui, "address"))}</p><p>{esc(c["address"])}</p></div></div>')
    if c.get("phone"):
        items.append(f'<div class="contact-item"><span class="card-icon">{icon("phone")}</span><div><p class="caption">{esc(t(ui, "phone"))}</p><p>{a(c.get("phone_href") or "tel:" + re.sub(r"[^+0-9]", "", c["phone"]), esc(c["phone"]))}</p></div></div>')
    if c.get("email"):
        items.append(f'<div class="contact-item"><span class="card-icon">{icon("mail")}</span><div><p class="caption">{esc(t(ui, "email"))}</p><p>{a("mailto:" + c["email"], esc(c["email"]))}</p></div></div>')
    extra = prose_blocks(site, sec.get("blocks", []))
    soc = social_links(site, "chips")
    left = (f'<div class="stack-lg"><div class="stack">{"".join(items)}</div>{extra}'
            + (f'<div class="stack"><h2 class="h5">{esc(t(ui, "follow_us"))}</h2>{soc.replace("<a ", "<a class=" + chr(34) + "icon-btn" + chr(34) + " ")}</div>' if soc else "") + '</div>')
    form_cfg = site.get("contact_form") or {}
    right = ""
    if form_cfg.get("action") or site.get("preview"):
        demo = "" if form_cfg.get("action") else ' data-demo="true"'
        subjects = form_cfg.get("subjects") or []
        privacy = form_cfg.get("privacy_link")
        right = (f'<div><div class="alert alert--success" id="contact-success" role="status" tabindex="-1" hidden>{icon("check-circle")}<div><h3>{esc(t(ui, "message_sent_title"))}</h3><p>{esc(t(ui, "message_sent_text"))}</p></div></div>'
                 f'<form class="panel" id="contact-form" action="{esc(form_cfg.get("action") or "#")}" method="post" novalidate{demo}>'
                 f'<h2 class="h3">{esc(form_cfg.get("title") or t(ui, "send_message"))}</h2><p class="caption">{esc(t(ui, "required_note"))}</p>'
                 f'<div class="alert alert--error error-summary" role="alert" tabindex="-1" hidden>{icon("alert-circle")}<div><h3>{esc(t(ui, "error_summary_title"))}</h3><p>{esc(t(ui, "error_summary_text"))}</p></div></div>'
                 + field(site, "name", t(ui, "name_label"), autocomplete="name", err=t(ui, "err_name"))
                 + '<div class="form-row">' + field(site, "email", t(ui, "email"), "email", autocomplete="email", placeholder=t(ui, "email_placeholder"), err=t(ui, "err_email_empty"))
                 + field(site, "phone", t(ui, "phone_label"), "tel", required=False, autocomplete="tel", inputmode="tel") + "</div>"
                 + (field(site, "subject", t(ui, "subject_label"), "select", options=subjects, err=t(ui, "err_subject")) if subjects else field(site, "subject", t(ui, "subject_label"), required=False))
                 + field(site, "message", t(ui, "message_label"), "textarea", err=t(ui, "err_message"))
                 + (f'<p class="caption">{esc(t(ui, "privacy_note"))} {a(privacy["href"], esc(privacy["label"]))}</p>' if privacy else "")
                 + f'<p class="form-preview-note caption" role="status" hidden>{esc(t(ui, "form_preview_notice"))}</p>'
                 + f'<div class="form-actions"><span></span><button class="btn btn--primary" type="submit">{esc(t(ui, "send_message"))}</button></div></form></div>')
    return wrap(sec, section_head(sec) + f'<div class="grid grid-2 grid-wide">{left}{right}</div>')


SECTIONS = {
    "hero": s_hero, "pillars": s_pillars, "quote_band": s_quote_band, "cards": s_cards, "documents": s_documents,
    "logos": s_logos, "news": s_news, "cta": s_cta, "prose": s_prose, "accordion": s_accordion, "team": s_team,
    "chips": s_chips, "columns": s_columns, "contact": s_contact,
}


# ---------------------------------------------------------------- page-level layouts

def page_header(site, ph: dict) -> str:
    ui = site["ui"]
    crumbs = ph.get("breadcrumb") or []
    bc = ""
    if crumbs:
        lis = []
        for i, c in enumerate(crumbs):
            if i == len(crumbs) - 1:
                lis.append(f'<li><span aria-current="page">{esc(c["label"])}</span></li>')
            elif c.get("href"):
                lis.append(f'<li>{a(c["href"], esc(c["label"]))}</li>')
            else:
                lis.append(f'<li><span>{esc(c["label"])}</span></li>')
        bc = f'<nav aria-label="{esc(t(ui, "breadcrumb"))}"><ol class="breadcrumb list-reset">{"".join(lis)}</ol></nav>'
    meta = ""
    if ph.get("date") or ph.get("category"):
        cat = f'<span class="tag">{esc(ph["category"])}</span>' if ph.get("category") else ""
        d = f'<span class="caption">{icon("calendar", "sm")} {esc(t(ui, "published"))}: {time_tag(site, ph["date"])}</span>' if ph.get("date") else ""
        meta = f'<p class="meta-line">{cat}{d}</p>'
    return (f'<div class="page-header"><div class="container">{bc}'
            + (f'<p class="overline">{esc(ph["overline"])}</p>' if ph.get("overline") else "")
            + f'{meta}<h1>{esc(ph["title"])}</h1>'
            + (f'<p class="lead">{md(ph["lead"])}</p>' if ph.get("lead") else "")
            + btns(site, ph.get("ctas", []))
            + '</div></div>\n')


def aside_blocks(site, blocks) -> str:
    ui = site["ui"]
    out = []
    for b in blocks:
        k = b["type"]
        if k == "facts":
            rows = "".join(f'<div class="kv">{icon(r.get("icon", "info"), "md")}<div><p class="k">{esc(r["k"])}</p><p class="v">{md(r["v"])}</p></div></div>' for r in b["items"])
            out.append(f'<div class="aside-box">' + (f'<h2 class="h5">{esc(b["title"])}</h2>' if b.get("title") else "") + rows
                       + (f'<p>{link_arrow(b["link"]["href"], b["link"]["label"])}</p>' if b.get("link") else "") + "</div>")
        elif k == "donate":
            member = site.get("header", {}).get("member_cta")
            out.append(f'<div class="aside-box aside-box--brand"><h2 class="h5">{esc(b.get("title") or t(ui, "sticky_title"))}</h2>'
                       + (f'<p class="small">{esc(b["text"])}</p>' if b.get("text") else "")
                       + a(site["donate_href"], esc(t(ui, "donate")), "btn btn--donate btn--block")
                       + (a(member["href"], esc(member["label"]), "btn btn--inverse btn--block") if member and b.get("show_member", True) else "") + "</div>")
        elif k == "links":
            lis = "".join(f'<li>{a(l["href"], esc(l["label"]))}' + (time_tag(site, l["date"]) if l.get("date") else "") + "</li>" for l in b["items"])
            out.append(f'<div><h2 class="h5">{esc(b["title"])}</h2><ul class="list-reset link-list">{lis}</ul></div>')
        elif k == "chips":
            lis = "".join(f'<li>{a(c["href"], esc(c["label"]), "chip")}</li>' for c in b["items"])
            out.append(f'<div class="aside-box"><h2 class="h5">{esc(b["title"])}</h2><ul class="chips list-reset">{lis}</ul></div>')
        elif k == "alert":
            out.append(alert(b.get("variant", "info"), b.get("title"), b["text"]))
        elif k == "steps":
            lis = "".join(f'<li class="card" style="flex-direction:row;padding:20px"><span class="pillar-num" aria-hidden="true">{i + 1}</span><div><h3 class="h5">{esc(s["title"])}</h3><p class="small">{md(s["text"])}</p></div></li>' for i, s in enumerate(b["items"]))
            out.append(f'<div class="stack"><h2 class="h4">{esc(b["title"])}</h2>' + (f'<p class="caption">{esc(b["caption"])}</p>' if b.get("caption") else "") + f'<ol class="steps-list list-reset">{lis}</ol></div>')
    return "".join(out)


def layout_article(site, page) -> str:
    body = prose_blocks(site, page.get("body", []))
    aside = aside_blocks(site, page.get("aside", []))
    return (page_header(site, page["header"]) +
            f'<article class="section"><div class="container article-layout"><div class="prose">{body}</div>'
            f'<aside class="stack-lg">{aside}</aside></div></article>\n')


def bank_block(site, suffix="") -> str:
    ui = site["ui"]
    b = site.get("bank")
    if not b:
        return ""
    rows = []
    if b.get("recipient"):
        rows.append(f'<div><p class="caption">{esc(t(ui, "recipient"))}</p><p class="small"><strong>{esc(b["recipient"])}</strong></p></div>')
    if b.get("bank_name"):
        rows.append(f'<div><p class="caption">{esc(t(ui, "bank_name"))}</p><p class="small">{esc(b["bank_name"])}</p></div>')
    for key in ("iban", "account_number", "sort_code", "swift"):
        if b.get(key):
            label = t(ui, key)
            raw = re.sub(r"\s", "", b[key])
            rows.append(f'<div class="bank-row"><div style="flex:1;min-width:200px"><p class="caption">{esc(label)}</p><p class="value">{esc(b[key])}</p></div>'
                        f'<button class="copy-btn" type="button" data-copy="{esc(raw)}" data-label="{esc(label)}" '
                        f'data-done="{esc(t(ui, "copied"))}" data-status="{esc(t(ui, "copied_status", label=label))}">{icon("copy", "md")} '
                        f'<span class="label">{esc(t(ui, "copy_value", label=label))}</span></button></div>')
    if b.get("reference_hint"):
        rows.append(f'<p class="caption">{md(b["reference_hint"])}</p>')
    return (f'<div class="bank-block"><p class="overline overline--muted">{esc(t(ui, "bank_transfer"))}</p>{"".join(rows)}'
            f'<p class="visually-hidden copy-status{suffix}" role="status" aria-live="polite"></p></div>')


def layout_donate(site, page) -> str:
    ui = site["ui"]
    don = site.get("donation", {})
    pay = site.get("payment", {}) or {}
    presets = don.get("presets") or []
    default = don.get("default")
    links_map = {str(k): v for k, v in (pay.get("links_by_amount") or {}).items() if v}
    connected = bool(pay.get("url") or pay.get("embed_html") or links_map)
    if links_map:
        # Provider only issues fixed-amount links: offer exactly those amounts, no custom field.
        presets = [int(k) for k in links_map]
        default = default if str(default) in links_map else presets[0]
    show_card = connected or site.get("preview")
    parts = [page_header(site, page["header"])]
    main = []
    if show_card and presets is not None:
        chips = "".join(
            f'<label class="amount-chip"><input type="radio" name="preset" value="{p}"{" checked" if p == default else ""}><span>{icon("check")}{esc(money(site, p))}</span></label>'
            for p in presets)
        if pay.get("embed_html") and not pay.get("url"):
            main.append(f'<div class="panel"><h2 class="h4">{esc(t(ui, "donation_title"))}</h2>{pay["embed_html"]}</div>')
        else:
            handoff = t(ui, "payment_handoff_note", provider=pay.get("provider_name") or "")
            not_conn = "" if connected else alert("info", None, t(ui, "payment_not_connected"))
            main.append(
                f'<form class="panel" id="donation-form" novalidate data-url="{esc(pay.get("url", ""))}" '
                f'data-amount-param="{esc(pay.get("amount_param", ""))}" data-amount-unit="{esc(pay.get("amount_unit", "major"))}" '
                f'data-min="{esc(don.get("min", 1))}" data-currency-symbol="{esc(site.get("currency_display", {}).get("symbol", site.get("currency", "")))}" '
                f'data-currency-position="{esc(site.get("currency_display", {}).get("position", "after"))}" data-thousands="{esc(site.get("currency_display", {}).get("thousands", ","))}" '
                f'data-monthly-url="{esc(pay.get("monthly_url", ""))}" data-links="{esc(json.dumps(links_map)) if links_map else ""}"{"" if connected else " data-demo=" + chr(34) + "true" + chr(34)}>'
                f'<h2 class="h4">{esc(t(ui, "donation_title"))}</h2>'
                + (f'<fieldset><legend>{esc(t(ui, "donation_type"))}</legend><div class="amounts">'
                   f'<label class="amount-chip"><input type="radio" name="frequency" value="once" checked><span>{icon("check")}{esc(t(ui, "one_time"))}</span></label>'
                   f'<label class="amount-chip"><input type="radio" name="frequency" value="monthly"><span>{icon("check")}{esc(t(ui, "monthly"))}</span></label></div></fieldset>'
                   if pay.get("monthly_url") else "")
                + (f'<fieldset><legend>{esc(t(ui, "quick_choice"))}</legend><div class="amounts">{chips}</div></fieldset>' if presets else "")
                + ("" if links_map else field(site, "custom-amount", t(ui, "custom_amount"), "text", required=not presets, inputmode="numeric",
                        placeholder=t(ui, "custom_amount_placeholder"), hint=t(ui, "custom_amount_hint") if presets else "", err=t(ui, "err_amount")))
                + f'<div class="total-line"><span>{esc(t(ui, "total"))}</span><span class="amount" data-total>{esc(money(site, default) if default else "–")}</span></div>'
                + not_conn
                + (f'<p class="small kv">{icon("lock", "md")}<span>{esc(handoff)}</span></p>' if pay.get("provider_name") else "")
                + f'<div class="form-actions"><span></span><button class="btn btn--donate" type="submit">{esc(t(ui, "continue_to_payment"))} {icon("arrow-right", "md")}</button></div>'
                + f'<p class="error" id="amount-error" role="alert" hidden data-msg-choose="{esc(t(ui, "choose_amount_error"))}" data-msg-min="{esc(t(ui, "min_amount_error", min=money(site, don.get("min", 1))))}">{icon("alert-circle", "sm")}<span class="msg"></span></p>'
                + f'<p class="form-preview-note caption" role="status" hidden>{esc(t(ui, "form_preview_notice"))}</p>'
                + '</form>')
    if site.get("bank"):
        main.append(bank_block(site, "-main"))
    for n in don.get("notes", []):
        main.append(alert(n.get("variant", "info"), n.get("title"), n["text"]))
    side = []
    if show_card and presets is not None and not (pay.get("embed_html") and not pay.get("url")):
        side.append(f'<div class="panel summary"><h2 class="h5">{esc(t(ui, "donation_summary"))}</h2><dl>'
                    f'<div class="row"><dt>{esc(t(ui, "donation_type"))}</dt><dd data-frequency-label data-once="{esc(t(ui, "one_time"))}" data-monthly="{esc(t(ui, "monthly"))}">{esc(t(ui, "one_time"))}</dd></div>'
                    f'<div class="row"><dt>{esc(t(ui, "amount"))}</dt><dd class="amount" data-total>{esc(money(site, default) if default else "–")}</dd></div></dl>'
                    + (f'<hr><p class="caption">{md(don["summary_note"])}</p>' if don.get("summary_note") else "") + '</div>')
    if don.get("trust_note"):
        tn = don["trust_note"]
        side.append(f'<div class="trust-note">{icon("shield-check")}<div><p>{md(tn["text"])}</p>' + (f'<p>{a(tn["link"]["href"], esc(tn["link"]["label"]))}</p>' if tn.get("link") else "") + '</div></div>')
    if don.get("membership_note"):
        mn = don["membership_note"]
        side.append(alert("info", mn.get("title") or t(ui, "membership_title"), mn["text"]))
    parts.append(f'<section class="section"><div class="container donation-layout"><div class="stack-lg">{"".join(main)}</div>'
                 f'<aside class="donation-side">{"".join(side)}</aside></div></section>\n')
    for sec in page.get("sections", []):
        parts.append(SECTIONS[sec["type"]](site, sec))
    return "".join(parts)


def layout_default(site, page) -> str:
    out = []
    if page.get("header"):
        out.append(page_header(site, page["header"]))
    for sec in page.get("sections", []):
        out.append(SECTIONS[sec["type"]](site, sec))
    return "".join(out)


def render_page(site, page) -> str:
    layout = page.get("layout", "default")
    body = {"article": layout_article, "donate": layout_donate}.get(layout, layout_default)(site, page)
    return head(site, page) + header(site, page) + body + footer(site, page)


def render_404(site) -> str:
    ui = site["ui"]
    page = {"slug": "404", "title": t(ui, "not_found_title"), "description": ""}
    body = (f'<section class="section"><div class="container stack text-col"><p class="overline">404</p><h1>{esc(t(ui, "not_found_title"))}</h1>'
            f'<p class="lead">{esc(t(ui, "not_found_text"))}</p><p>{a("index.html", esc(t(ui, "back_home")), "btn btn--primary")}</p></div></section>')
    return head(site, page) + header(site, page) + body + footer(site, page)
