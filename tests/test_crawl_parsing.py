import struct
import unittest

from tests.helpers import ROOT  # noqa: F401
import crawl


class CrawlParsingTest(unittest.TestCase):
    def test_iban_checksum(self):
        self.assertTrue(crawl.iban_valid("TR 47 0001 0009 5776 7948 2750 01"))
        self.assertTrue(crawl.iban_valid("GB82 WEST 1234 5698 7654 32"))
        self.assertFalse(crawl.iban_valid("TR 48 0001 0009 5776 7948 2750 01"))

    def test_iban_not_reported_as_phone(self):
        text = "IBAN: TR 47 0001 0009 5776 7948 2750 01 — Telefon: +90 533 927 90 45"
        phones = crawl.PHONE_RE.findall(crawl.IBAN_RE.sub(" ", text))
        self.assertEqual(phones, ["+90 533 927 90 45"])

    def test_image_size_png_and_gif(self):
        png = b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + struct.pack(">II", 640, 480) + b"\x08\x02\x00\x00\x00"
        self.assertEqual(crawl.image_size(png), (640, 480))
        gif = b"GIF89a" + struct.pack("<HH", 32, 16)
        self.assertEqual(crawl.image_size(gif), (32, 16))

    def test_extract_text_links_images_forms(self):
        html = """<html lang="tr"><head><title>Bağış</title><meta name="description" content="d"></head><body>
        <nav><a href="/tr/page/hikayemiz">Hikayemiz</a></nav>
        <h1>Bağış Yap</h1><p>Destek olun.</p><img src="/img/a.jpg" alt="Aile">
        <form action="/pay"><input name="card_number"><input name="cvv"></form>
        <script src="https://js.stripe.com/v3/"></script></body></html>"""
        ex = crawl.Extract("https://example.org/tr/bagis")
        ex.feed(html)
        ex.close()
        self.assertEqual(ex.lang, "tr")
        self.assertIn("# Bağış Yap", ex.lines)
        self.assertEqual(ex.links[0]["href"], "https://example.org/tr/page/hikayemiz")
        self.assertEqual(ex.imgs[0]["src"], "https://example.org/img/a.jpg")
        self.assertEqual([f["name"] for f in ex.forms[0]["fields"]], ["card_number", "cvv"])
        self.assertIn("https://js.stripe.com/v3/", ex.scripts)

    def test_payment_signatures_cover_major_providers(self):
        for pid in ("stripe", "paypal", "donorbox", "iyzico", "paytr", "razorpay", "mollie"):
            self.assertIn(pid, crawl.PAYMENT_SIGNATURES)


if __name__ == "__main__":
    unittest.main()
