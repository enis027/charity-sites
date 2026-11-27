#!/usr/bin/env python3
"""Audit a charity's existing website.

Polite, same-site crawl that inventories everything the rebuild needs:
pages and their text, images (downloaded with real dimensions), brand colours,
fonts, logo candidates, contact details, bank details (IBANs are checksum-
validated), forms, the payment provider currently in use, broken pages and
content problems (untranslated keys, placeholder text, sample data).

Usage:
  python3 crawl.py https://example.org [--out audit] [--max-pages 80] [--delay 1.0]
                   [--no-images] [--max-images 200]

Standard library only. Respects robots.txt and identifies itself.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import ssl
import struct
import sys
import time
import urllib.error
import urllib.request
import urllib.robotparser
from collections import Counter, deque
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse

UA = "charity-sites-audit/0.1 (+https://github.com/enis027/charity-sites; respectful single-site audit)"
HTML_TYPES = ("text/html", "application/xhtml+xml")
SKIP_EXT = re.compile(r"\.(pdf|docx?|xlsx?|pptx?|zip|rar|7z|mp3|mp4|mov|avi|wmv|webm|jpe?g|png|gif|webp|svg|ico|css|js|xml|rss|json)(\?|$)", re.I)

PAYMENT_SIGNATURES = {
    # provider id: (display name, [substrings found in HTML, script src, iframe src or form action])
    "stripe": ("Stripe", ["js.stripe.com", "buy.stripe.com", "donate.stripe.com", "checkout.stripe.com"]),
    "paypal": ("PayPal", ["paypal.com/donate", "paypal.com/cgi-bin/webscr", "paypalobjects.com", "paypal.com/sdk", "paypal.me/"]),
    "donorbox": ("Donorbox", ["donorbox.org"]),
    "givebutter": ("Givebutter", ["givebutter.com"]),
    "givewp": ("GiveWP (WordPress)", ["give-form", "/plugins/give/", "give-donation"]),
    "classy": ("Classy / GoFundMe Pro", ["classy.org", "gofundme.com/c/", "gofundmepro"]),
    "justgiving": ("JustGiving", ["justgiving.com"]),
    "gofundme": ("GoFundMe", ["gofundme.com"]),
    "every_org": ("Every.org", ["every.org"]),
    "zeffy": ("Zeffy", ["zeffy.com"]),
    "raisely": ("Raisely", ["raisely.com"]),
    "enthuse": ("Enthuse", ["enthuse.com"]),
    "caf": ("CAF Donate", ["cafdonate.cafonline.org", "cafonline.org/donate"]),
    "blackbaud": ("Blackbaud", ["bbox.blackbaudhosting", "blackbaud.com", "bbcheckout"]),
    "mollie": ("Mollie", ["mollie.com", "payment-links.mollie.com"]),
    "gocardless": ("GoCardless", ["gocardless.com", "pay.gocardless"]),
    "helloasso": ("HelloAsso", ["helloasso.com"]),
    "twingle": ("Twingle", ["twingle.de"]),
    "betterplace": ("betterplace.org", ["betterplace.org"]),
    "razorpay": ("Razorpay", ["checkout.razorpay.com", "razorpay.com", "rzp.io"]),
    "paystack": ("Paystack", ["paystack.com", "paystack.co"]),
    "flutterwave": ("Flutterwave", ["flutterwave.com", "checkout.flutterwave"]),
    "mercadopago": ("Mercado Pago", ["mercadopago", "mpago.la"]),
    "pagseguro": ("PagSeguro / PagBank", ["pagseguro", "pagbank"]),
    "payu": ("PayU", ["payu.", "secure.payu"]),
    "square": ("Square", ["squareup.com", "square.link", "squarecdn"]),
    "iyzico": ("iyzico", ["iyzipay", "iyzico.com", "iyzi.link"]),
    "paytr": ("PayTR", ["paytr.com"]),
    "param": ("Param", ["param.com.tr", "turkpos"]),
    "craftgate": ("Craftgate", ["craftgate.io"]),
    "sipay": ("Sipay", ["sipay.com.tr"]),
    "moka": ("Moka", ["mokapos", "moka.com"]),
    "papara": ("Papara", ["papara.com"]),
    "nestpay": ("Bank virtual POS (Nestpay/EST 3D)", ["est3dgate", "nestpay", "3dpay", "fim/est3dgate"]),
    "garanti": ("Garanti BBVA virtual POS", ["sanalposprov.garanti", "garantibbva"]),
    "posnet": ("Yapı Kredi POSNET", ["posnet"]),
    "twint": ("TWINT", ["twint"]),
    "mpesa": ("M-Pesa", ["mpesa", "safaricom"]),
    "woocommerce": ("WooCommerce", ["woocommerce"]),
}

IBAN_RE = re.compile(r"\b([A-Z]{2}[  ]?\d{2}(?:[  ]?[A-Z0-9]{4}){2,7}(?:[  ]?[A-Z0-9]{1,4})?)\b")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?:\+|00)\d[\d \-().]{7,}\d|\b0\d{2,4}[ \-]?\d{3}[ \-]?\d{2,4}(?:[ \-]?\d{2})?\b")
HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
FONT_RE = re.compile(r"font-family\s*:\s*([^;}{]+)", re.I)
DATE_RE = re.compile(r"\b(\d{1,2}[./-]\d{1,2}[./-]\d{2,4}|\d{4}-\d{2}-\d{2}|\d{1,2} [A-Za-zÀ-ÿĞğİıŞşÇçÖöÜü]{3,10} \d{4})\b")
TRANSLATION_KEY = re.compile(r"\b[a-z]{2,}\.[a-z_]{2,}\.[a-z_]{2,}\b")
PLACEHOLDER = re.compile(r"lorem ipsum|dolor sit amet|\bTODO\b|\bTBD\b|sample text|örnek metin", re.I)


def iban_valid(raw: str) -> bool:
    s = re.sub(r"\s", "", raw).upper()
    if not 15 <= len(s) <= 34:
        return False
    s = s[4:] + s[:4]
    num = "".join(str(int(c, 36)) for c in s)
    return int(num) % 97 == 1


def image_size(data: bytes) -> tuple[int, int] | None:
    try:
        if data[:8] == b"\x89PNG\r\n\x1a\n":
            return struct.unpack(">II", data[16:24])
        if data[:6] in (b"GIF87a", b"GIF89a"):
            return struct.unpack("<HH", data[6:10])
        if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            chunk = data[12:16]
            if chunk == b"VP8X":
                return (int.from_bytes(data[24:27], "little") + 1, int.from_bytes(data[27:30], "little") + 1)
            if chunk == b"VP8 ":
                w, h = struct.unpack("<HH", data[26:30])
                return (w & 0x3FFF, h & 0x3FFF)
            if chunk == b"VP8L":
                b = data[21:25]
                return (1 + (((b[1] & 0x3F) << 8) | b[0]), 1 + (((b[3] & 0xF) << 10) | (b[2] << 2) | ((b[1] & 0xC0) >> 6)))
        if data[:2] == b"\xff\xd8":
            i = 2
            while i < len(data):
                if data[i] != 0xFF:
                    i += 1
                    continue
                marker = data[i + 1]
                if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                    h, w = struct.unpack(">HH", data[i + 5:i + 9])
                    return (w, h)
                seg = struct.unpack(">H", data[i + 2:i + 4])[0]
                i += 2 + seg
        if b"<svg" in data[:2000]:
            m = re.search(rb'viewBox="[\d.\-]+[ ,]+[\d.\-]+[ ,]+([\d.]+)[ ,]+([\d.]+)"', data[:4000])
            if m:
                return (int(float(m.group(1))), int(float(m.group(2))))
    except Exception:
        return None
    return None


class Extract(HTMLParser):
    BLOCK = {"p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "td", "th", "dt", "dd", "blockquote", "figcaption", "caption", "div", "section", "article", "br", "tr", "label", "option", "button"}

    def __init__(self, base: str):
        super().__init__(convert_charrefs=True)
        self.base = base
        self.lines: list[str] = []
        self.buf: list[str] = []
        self.prefix = ""
        self.title = ""
        self.in_title = False
        self.skip = 0
        self.links: list[dict] = []
        self.imgs: list[dict] = []
        self.forms: list[dict] = []
        self.scripts: list[str] = []
        self.iframes: list[str] = []
        self.styles: list[str] = []
        self.inline_css: list[str] = []
        self.meta: dict = {}
        self.lang = ""
        self.icons: list[str] = []
        self.headings: list[tuple[int, str]] = []
        self.cur_link = None
        self.cur_heading = None
        self.in_style = False
        self.bg_images: list[str] = []
        self.svgs_logo = 0

    def flush(self):
        text = re.sub(r"\s+", " ", "".join(self.buf)).strip()
        if text:
            self.lines.append(self.prefix + text)
            if self.cur_heading:
                self.headings.append((self.cur_heading, text))
        self.buf = []
        self.prefix = ""

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        style = a.get("style", "")
        for m in re.finditer(r"url\(['\"]?([^'\")]+)", style):
            self.bg_images.append(urljoin(self.base, m.group(1)))
        if tag in ("script", "noscript", "template"):
            if tag == "script" and a.get("src"):
                self.scripts.append(urljoin(self.base, a["src"]))
            self.skip += 1
            return
        if tag == "style":
            self.in_style = True
            return
        if tag == "html":
            self.lang = a.get("lang", "")
        if tag == "title":
            self.in_title = True
        if tag == "meta":
            k = a.get("name") or a.get("property")
            if k:
                self.meta[k.lower()] = a.get("content", "")
        if tag == "link":
            rel = a.get("rel", "").lower()
            if "stylesheet" in rel and a.get("href"):
                self.styles.append(urljoin(self.base, a["href"]))
            if "icon" in rel and a.get("href"):
                self.icons.append(urljoin(self.base, a["href"]))
        if tag == "iframe" and a.get("src"):
            self.iframes.append(urljoin(self.base, a["src"]))
        if tag == "form":
            self.forms.append({"action": urljoin(self.base, a.get("action", "")) if a.get("action") else "", "method": a.get("method", "get").lower(), "fields": []})
        if tag in ("input", "select", "textarea") and self.forms:
            self.forms[-1]["fields"].append({"tag": tag, "type": a.get("type", ""), "name": a.get("name", ""), "placeholder": a.get("placeholder", ""), "autocomplete": a.get("autocomplete", "")})
        if tag == "img":
            src = a.get("src") or a.get("data-src") or a.get("data-lazy-src") or ""
            srcset = a.get("srcset") or a.get("data-srcset") or ""
            if srcset:
                best = sorted(((int(re.sub(r"\D", "", p.split()[-1]) or 0), p.split()[0]) for p in srcset.split(",") if p.strip() and len(p.split()) > 1), reverse=True)
                if best and best[0][0]:
                    src = best[0][1]
            if src and not src.startswith("data:"):
                self.imgs.append({"src": urljoin(self.base, src), "alt": a.get("alt"), "class": a.get("class", ""), "id": a.get("id", ""), "context": " ".join(self.buf)[-120:]})
        if tag == "svg" and re.search(r"logo", a.get("class", "") + a.get("id", ""), re.I):
            self.svgs_logo += 1
        if tag == "a":
            href = a.get("href", "")
            if href and not href.startswith(("javascript:", "#")):
                self.cur_link = {"href": urljoin(self.base, href), "text": ""}
        if re.fullmatch(r"h[1-6]", tag):
            self.flush()
            self.cur_heading = int(tag[1])
            self.prefix = "#" * int(tag[1]) + " "
        elif tag == "li":
            self.flush()
            self.prefix = "- "
        elif tag in self.BLOCK:
            self.flush()

    def handle_endtag(self, tag):
        if tag in ("script", "noscript", "template"):
            self.skip = max(0, self.skip - 1)
            return
        if tag == "style":
            self.in_style = False
            return
        if tag == "title":
            self.in_title = False
        if tag == "a" and self.cur_link:
            self.cur_link["text"] = re.sub(r"\s+", " ", self.cur_link["text"]).strip()
            self.links.append(self.cur_link)
            self.cur_link = None
        if re.fullmatch(r"h[1-6]", tag):
            self.flush()
            self.cur_heading = None
        elif tag in self.BLOCK:
            self.flush()

    def handle_data(self, data):
        if self.in_style:
            self.inline_css.append(data)
            return
        if self.skip:
            return
        if self.in_title:
            self.title += data
            return
        self.buf.append(data)
        if self.cur_link is not None:
            self.cur_link["text"] += data

    def close(self):
        super().close()
        self.flush()


class Crawler:
    def __init__(self, start: str, out: Path, max_pages: int, delay: float, images: bool, max_images: int):
        self.start = start if urlparse(start).scheme else "https://" + start
        u = urlparse(self.start)
        self.host = u.netloc.lower()
        self.hosts = {self.host, self.host[4:] if self.host.startswith("www.") else "www." + self.host}
        self.out = out
        self.max_pages = max_pages
        self.delay = delay
        self.images = images
        self.max_images = max_images
        self.robots = urllib.robotparser.RobotFileParser()
        self.robots_ok = True
        try:
            self.robots.set_url(f"{u.scheme}://{u.netloc}/robots.txt")
            self.robots.read()
        except Exception:
            self.robots_ok = False
        self.ctx = ssl.create_default_context()
        self.last = 0.0
        self.pages: dict[str, dict] = {}
        self.failures: dict[str, str] = {}
        self.redirects: dict[str, str] = {}
        self.referenced_by: dict[str, set] = {}
        self.external_links: Counter = Counter()
        self.css_colors: Counter = Counter()
        self.fonts: Counter = Counter()

    def allowed(self, url: str) -> bool:
        return (not self.robots_ok) or self.robots.can_fetch(UA, url)

    def fetch(self, url: str, binary_cap: int = 8_000_000):
        wait = self.delay - (time.time() - self.last)
        if wait > 0:
            time.sleep(wait)
        self.last = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "*"})
        try:
            with urllib.request.urlopen(req, timeout=30, context=self.ctx) as r:
                data = r.read(binary_cap)
                return r.status, r.geturl(), r.headers.get("Content-Type", ""), data, None
        except urllib.error.HTTPError as e:
            return e.code, url, "", b"", f"HTTP {e.code}"
        except ssl.SSLError as e:
            return 0, url, "", b"", f"TLS error: {e.reason if hasattr(e, 'reason') else e}"
        except Exception as e:  # network, timeout: retry once after a pause
            if not getattr(self, "_retrying", False):
                self._retrying = True
                time.sleep(3)
                try:
                    return self.fetch(url, binary_cap)
                finally:
                    self._retrying = False
            return 0, url, "", b"", f"{type(e).__name__}: {e}"

    def same_site(self, url: str) -> bool:
        return urlparse(url).netloc.lower() in self.hosts

    def norm(self, url: str) -> str:
        url, _ = urldefrag(url)
        u = urlparse(url)
        path = u.path or "/"
        return f"{u.scheme}://{u.netloc.lower()}{path}" + (f"?{u.query}" if u.query else "")

    def run(self):
        q = deque([self.norm(self.start)])
        later: deque = deque()  # other language sections etc., crawled after the start section
        seen = set(q)
        prefix = urlparse(self.start).path.rstrip("/")
        prefix = prefix if prefix.count("/") == 1 and len(prefix) <= 6 else ""  # e.g. "/tr"
        while (q or later) and len(self.pages) < self.max_pages:
            url = q.popleft() if q else later.popleft()
            if not self.allowed(url):
                self.failures[url] = "disallowed by robots.txt"
                continue
            status, final, ctype, data, err = self.fetch(url)
            if err or status >= 400:
                self.failures[url] = err or f"HTTP {status}"
                continue
            if final != url:
                self.redirects[url] = final
            if not any(t in ctype for t in HTML_TYPES):
                continue
            charset = re.search(r"charset=([\w-]+)", ctype)
            html = data.decode(charset.group(1) if charset else "utf-8", errors="replace")
            ex = Extract(final)
            ex.feed(html)
            ex.close()
            self.record(url, final, html, ex)
            for link in ex.links:
                href = self.norm(link["href"])
                if self.same_site(href):
                    self.referenced_by.setdefault(href, set()).add(url)
                    if href not in seen and not SKIP_EXT.search(href):
                        seen.add(href)
                        p = urlparse(href).path
                        other_lang = re.match(r"^/[a-z]{2}(/|$)", p) and not (prefix and p.startswith(prefix))
                        (later if other_lang else q).append(href)
                elif href.startswith("http"):
                    self.external_links[urlparse(href).netloc.lower()] += 1
        self.leftover = [u for u in q] + [u for u in later]

    def record(self, url, final, html, ex: Extract):
        text = "\n".join(ex.lines)
        lower = html.lower()
        payments = {}
        blobs = [lower] + [s.lower() for s in ex.scripts + ex.iframes] + [f["action"].lower() for f in ex.forms]
        for pid, (name, sigs) in PAYMENT_SIGNATURES.items():
            hits = sorted({s for s in sigs for b in blobs if s in b})
            if hits:
                payments[pid] = {"name": name, "evidence": hits}
        card_form = any(
            re.search(r"card|kart|cvv|cvc|cc-|expir|son ?kullanma", " ".join(f.get(k, "") for k in ("name", "placeholder", "autocomplete")), re.I)
            for form in ex.forms for f in form["fields"])
        ibans = []
        for m in IBAN_RE.finditer(text):
            raw = m.group(1).replace(" ", " ")
            ibans.append({"iban": raw, "valid": iban_valid(raw)})
        for css in ex.inline_css:
            self.css_colors.update(c.upper() if len(c) == 7 else c.upper() for c in HEX_RE.findall(css))
            self.fonts.update(f.strip().split(",")[0].strip("'\" ") for f in FONT_RE.findall(css))
        self.pages[url] = {
            "url": url, "final_url": final, "title": ex.title.strip(), "lang": ex.lang,
            "description": ex.meta.get("description", ""), "og_image": ex.meta.get("og:image", ""),
            "headings": ex.headings, "text": text, "words": len(text.split()),
            "links": ex.links, "images": ex.imgs, "bg_images": ex.bg_images, "forms": ex.forms,
            "scripts": ex.scripts, "iframes": ex.iframes, "styles": ex.styles, "icons": ex.icons,
            "emails": sorted(set(EMAIL_RE.findall(text) + re.findall(r"mailto:([^\"'?>\s]+)", html))),
            "phones": sorted(set(p.strip() for p in PHONE_RE.findall(IBAN_RE.sub(" ", text)))),
            "ibans": ibans, "dates": sorted(set(DATE_RE.findall(text)))[:40],
            "payments": payments, "card_form_on_site": card_form,
            "translation_keys": sorted(set(k for k in TRANSLATION_KEY.findall(text) if "@" not in k and not re.search(r"\.(com|org|net|tr|gov|edu)\b", k))),
            "placeholders": sorted(set(m.group(0) for m in PLACEHOLDER.finditer(text))),
            "logo_svg": ex.svgs_logo,
        }

    def collect_css(self):
        urls = Counter(s for p in self.pages.values() for s in p["styles"] if self.same_site(s))
        for css_url, _ in urls.most_common(8):
            status, _, _, data, err = self.fetch(css_url, 3_000_000)
            if err:
                continue
            css = data.decode("utf-8", errors="replace")
            self.css_colors.update(c.upper() for c in HEX_RE.findall(css) if len(c) == 7)
            self.fonts.update(f.strip().split(",")[0].strip("'\" ") for f in FONT_RE.findall(css))

    def download_images(self):
        img_dir = self.out / "images"
        img_dir.mkdir(parents=True, exist_ok=True)
        refs: dict[str, dict] = {}
        for p in self.pages.values():
            for im in p["images"]:
                r = refs.setdefault(im["src"], {"src": im["src"], "alts": set(), "pages": set(), "logo_hint": False, "contexts": []})
                if im.get("alt"):
                    r["alts"].add(im["alt"])
                r["pages"].add(p["url"])
                if re.search(r"logo", (im["src"] + im.get("class", "") + im.get("id", "") + (im.get("alt") or "")), re.I):
                    r["logo_hint"] = True
                if im.get("context"):
                    r["contexts"].append(im["context"])
            for bg in p["bg_images"]:
                refs.setdefault(bg, {"src": bg, "alts": set(), "pages": set(), "logo_hint": False, "contexts": [], "background": True})["pages"].add(p["url"])
            if p.get("og_image"):
                refs.setdefault(urljoin(p["url"], p["og_image"]), {"src": urljoin(p["url"], p["og_image"]), "alts": set(), "pages": set(), "logo_hint": False, "contexts": [], "og": True})["pages"].add(p["url"])
            for ic in p["icons"]:
                refs.setdefault(ic, {"src": ic, "alts": set(), "pages": set(), "logo_hint": True, "contexts": [], "icon": True})["pages"].add(p["url"])
        out = []
        for i, (src, r) in enumerate(sorted(refs.items(), key=lambda kv: -len(kv[1]["pages"]))):
            entry = {"src": src, "alts": sorted(r["alts"]), "pages": sorted(r["pages"]), "used_on_pages": len(r["pages"]),
                     "logo_hint": r["logo_hint"], "background": r.get("background", False), "og": r.get("og", False), "icon": r.get("icon", False),
                     "context": r["contexts"][0] if r["contexts"] else ""}
            if self.images and i < self.max_images:
                status, final, ctype, data, err = self.fetch(src)
                if err:
                    entry["error"] = err
                else:
                    ext = (re.search(r"\.(jpe?g|png|gif|webp|svg|ico|avif)(?:\?|$)", final, re.I) or re.search(r"(jpeg|png|gif|webp|svg|avif)", ctype))
                    ext = (ext.group(1).lower() if ext else "bin").replace("jpeg", "jpg")
                    name = hashlib.sha1(src.encode()).hexdigest()[:12] + "." + ext
                    (img_dir / name).write_bytes(data)
                    size = image_size(data)
                    entry.update({"file": f"images/{name}", "bytes": len(data), "width": size[0] if size else None, "height": size[1] if size else None, "content_type": ctype})
            out.append(entry)
        return out


def boilerplate(pages: dict) -> set[str]:
    """Lines that appear on most pages (menus, footers) so page text shows only real content."""
    n = len(pages)
    if n < 3:
        return set()
    c = Counter(line for p in pages.values() for line in set(p["text"].splitlines()))
    return {line for line, k in c.items() if k >= max(3, 0.6 * n)}


def slug(url: str) -> str:
    u = urlparse(url)
    s = (u.path.strip("/") or "home") + (("-" + u.query) if u.query else "")
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s)[:90] or "home"


def write_outputs(c: Crawler, images: list[dict]):
    out = c.out
    (out / "pages").mkdir(parents=True, exist_ok=True)
    bp = boilerplate(c.pages)
    (out / "boilerplate.md").write_text("# Text repeated on most pages (menus, footer)\n\n" + "\n".join(sorted(bp)) + "\n", encoding="utf-8")
    index = []
    for url, p in c.pages.items():
        body = "\n\n".join(l for l in p["text"].splitlines() if l not in bp)
        name = slug(url) + ".md"
        header = (f"---\nsource: {url}\nfinal_url: {p['final_url']}\ntitle: {json.dumps(p['title'], ensure_ascii=False)}\n"
                  f"lang: {p['lang']}\ndescription: {json.dumps(p['description'], ensure_ascii=False)}\nwords: {p['words']}\n---\n\n")
        imgs = "\n".join(f"- {im['src']} (alt: {im.get('alt')!r})" for im in p["images"])
        (out / "pages" / name).write_text(header + body + ("\n\n## Images on this page\n" + imgs if imgs else "") + "\n", encoding="utf-8")
        index.append({"url": url, "file": f"pages/{name}", "title": p["title"], "words": len(body.split())})

    payments: dict[str, dict] = {}
    for p in c.pages.values():
        for pid, info in p["payments"].items():
            e = payments.setdefault(pid, {"name": info["name"], "evidence": set(), "pages": set()})
            e["evidence"].update(info["evidence"])
            e["pages"].add(p["url"])
    payments_out = {k: {"name": v["name"], "evidence": sorted(v["evidence"]), "pages": sorted(v["pages"])} for k, v in payments.items()}
    ibans = {}
    for p in c.pages.values():
        for ib in p["ibans"]:
            key = re.sub(r"\s", "", ib["iban"])
            ibans.setdefault(key, {"iban": ib["iban"], "valid": ib["valid"], "pages": set()})["pages"].add(p["url"])
    broken = [{"url": u, "error": e, "linked_from": sorted(c.referenced_by.get(u, []))[:5]} for u, e in c.failures.items()]
    issues = []
    for p in c.pages.values():
        for k in p["translation_keys"]:
            issues.append({"type": "untranslated_key", "page": p["url"], "value": k})
        for k in p["placeholders"]:
            issues.append({"type": "placeholder_text", "page": p["url"], "value": k})
        if p["words"] < 40:
            issues.append({"type": "thin_or_empty_page", "page": p["url"], "value": f"{p['words']} words"})
        if p["card_form_on_site"]:
            issues.append({"type": "card_fields_on_site", "page": p["url"], "value": "Card fields rendered on the charity's own page (direct virtual POS integration)"})
        for im in p["images"]:
            if im.get("alt") is None:
                issues.append({"type": "img_missing_alt", "page": p["url"], "value": im["src"]})
    inv = {
        "start_url": c.start, "crawled_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "user_agent": UA,
        "robots_txt_read": c.robots_ok, "pages_crawled": len(c.pages), "not_crawled_due_to_limit": c.leftover[:200],
        "languages": Counter(p["lang"] for p in c.pages.values()).most_common(),
        "pages": index, "redirects": c.redirects, "broken": broken,
        "emails": sorted({e for p in c.pages.values() for e in p["emails"]}),
        "phones": Counter(ph for p in c.pages.values() for ph in p["phones"]).most_common(20),
        "ibans": [dict(v, pages=sorted(v["pages"])) for v in ibans.values()],
        "payments_detected": payments_out,
        "card_form_on_site": sorted(p["url"] for p in c.pages.values() if p["card_form_on_site"]),
        "forms": [{"page": p["url"], **f} for p in c.pages.values() for f in p["forms"]],
        "css_colors": c.css_colors.most_common(30), "fonts": c.fonts.most_common(10),
        "external_domains": c.external_links.most_common(40),
        "social": sorted({l["href"].rstrip("/") for p in c.pages.values() for l in p["links"]
                          if re.search(r"(facebook|instagram|twitter|x\.com|youtube|linkedin|tiktok|t\.me)\.?", l["href"], re.I)
                          and not re.search(r"sharer|intent/|share\?|/share/|shareArticle|api\.whatsapp|wa\.me/\?", l["href"], re.I)}),
        "images": images, "issues": issues,
        "dates_seen": sorted({d for p in c.pages.values() for d in p["dates"]})[:200],
    }
    grouped: dict[tuple, dict] = {}
    for i in issues:
        g = grouped.setdefault((i["type"], i["value"]), {"type": i["type"], "value": i["value"], "pages": []})
        g["pages"].append(i["page"])
    inv["issues"] = list(grouped.values())
    (out / "inventory.json").write_text(json.dumps(inv, ensure_ascii=False, indent=2, default=list), encoding="utf-8")
    (out / "REPORT.md").write_text(report_md(inv), encoding="utf-8")
    return inv


def report_md(inv: dict) -> str:
    L = [f"# Site audit: {inv['start_url']}", "", f"Crawled {inv['pages_crawled']} pages on {inv['crawled_at']} (robots.txt read: {inv['robots_txt_read']}).", ""]
    if inv["not_crawled_due_to_limit"]:
        L += [f"**Page limit reached.** {len(inv['not_crawled_due_to_limit'])} more URLs were queued; raise --max-pages if they matter.", ""]
    L += ["## Payment setup today"]
    if inv["payments_detected"]:
        for k, v in inv["payments_detected"].items():
            L.append(f"- **{v['name']}** (`{k}`): evidence {', '.join(v['evidence'])} on {len(v['pages'])} page(s)")
    else:
        L.append("- No known payment provider detected in page HTML, scripts, iframes or form actions.")
    if inv["card_form_on_site"]:
        L.append(f"- Card fields are rendered on the charity's own pages ({len(inv['card_form_on_site'])} page(s)), which suggests a direct bank virtual-POS integration. The rebuild must hand off to a hosted payment page instead.")
    L += ["", "## Bank details found"]
    L += [f"- {b['iban']} — checksum {'valid' if b['valid'] else 'INVALID'} — on {len(b['pages'])} page(s)" for b in inv["ibans"]] or ["- none"]
    L += ["", "## Contact details", f"- Emails: {', '.join(inv['emails']) or 'none found'}", f"- Phones: {', '.join(p for p, _ in inv['phones'][:6]) or 'none found'}", f"- Social: {', '.join(inv['social']) or 'none found'}"]
    L += ["", "## Broken or inaccessible pages"]
    L += [f"- {b['url']} — {b['error']}" + (f" (linked from {b['linked_from'][0]})" if b["linked_from"] else "") for b in inv["broken"]] or ["- none"]
    L += ["", "## Content issues"]
    L += [f"- {i['type']}: {i['value']} — {len(i['pages'])} page(s), e.g. {i['pages'][0]}" for i in inv["issues"][:80]] or ["- none"]
    L += ["", "## Brand signals", f"- Top CSS colours: {', '.join(f'{c} ({n})' for c, n in inv['css_colors'][:12])}", f"- Fonts: {', '.join(f for f, _ in inv['fonts'][:6])}"]
    imgs = [i for i in inv["images"] if i.get("width")]
    L += ["", "## Images (largest first)", "| file | size | alt | used on | notes |", "|---|---|---|---|---|"]
    for i in sorted(imgs, key=lambda x: -(x["width"] * x["height"]))[:40]:
        notes = ", ".join(n for n, f in (("logo?", i["logo_hint"]), ("background", i["background"]), ("og", i["og"]), ("icon", i["icon"])) if f)
        L.append(f"| {i.get('file', '')} | {i['width']}×{i['height']} | {(i['alts'][0] if i['alts'] else '')[:40]} | {i['used_on_pages']} | {notes} |")
    L += ["", "## Pages", "| words | title | url |", "|---|---|---|"]
    L += [f"| {p['words']} | {p['title'][:60]} | {p['url']} |" for p in sorted(inv["pages"], key=lambda p: -p["words"])]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url")
    ap.add_argument("--out", type=Path, default=Path("audit"))
    ap.add_argument("--max-pages", type=int, default=80)
    ap.add_argument("--delay", type=float, default=1.0, help="seconds between requests (be polite to small servers)")
    ap.add_argument("--no-images", action="store_true")
    ap.add_argument("--max-images", type=int, default=200)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    c = Crawler(a.url, a.out, a.max_pages, a.delay, not a.no_images, a.max_images)
    print(f"Crawling {c.start} (max {a.max_pages} pages, {a.delay}s between requests)…", file=sys.stderr)
    c.run()
    c.collect_css()
    images = c.download_images()
    inv = write_outputs(c, images)
    print(f"Done: {inv['pages_crawled']} pages, {len(inv['broken'])} broken, {len(images)} images, "
          f"payments: {', '.join(v['name'] for v in inv['payments_detected'].values()) or 'none detected'}. See {a.out}/REPORT.md", file=sys.stderr)


if __name__ == "__main__":
    main()
