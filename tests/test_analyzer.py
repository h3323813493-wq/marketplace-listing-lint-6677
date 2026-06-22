import unittest

from listing_lint import Listing, analyze_listing


class AnalyzerTests(unittest.TestCase):
    def test_ready_listing_scores_high(self):
        listing = Listing.from_dict(
            {
                "title": "Mainan Ikan Catnip untuk Kucing, Crinkle Sound Cat Toy",
                "description": "Penerangan Produk\n\nMainan lembut.\n\nCiri Utama\n\n- Catnip\n\nCara Penggunaan\n\nGunakan di rumah.\n\nSesuai Untuk\n\nKucing.\n\nNota\n\nPantau untuk keselamatan.",
                "keywords": ["catnip", "crinkle", "cat toy"],
                "sku_options": ["Ikan kuning", "Ikan putih"],
                "price_min": 7.36,
                "price_max": 11.58,
                "discount_price_min": 3.68,
                "discount_price_max": 5.79,
                "image_notes": ["clean white", "cat lifestyle", "catnip crinkle callout"],
            }
        )
        report = analyze_listing(listing)
        self.assertGreaterEqual(report.score, 85)
        self.assertEqual(report.status, "ready")

    def test_empty_title_blocks_listing(self):
        report = analyze_listing(Listing.from_dict({"description": "Some text"}))
        self.assertEqual(report.status, "blocked")
        self.assertTrue(any(item.area == "title" and item.level == "error" for item in report.findings))

    def test_pack_size_without_pack_sku_is_warned(self):
        listing = Listing.from_dict(
            {
                "title": "Mainan Ikan Catnip untuk Kucing 1/2pcs",
                "description": "Penerangan Produk\n\nText\n\nCiri Utama\n\nText\n\nCara Penggunaan\n\nText\n\nSesuai Untuk\n\nText\n\nNota\n\nPantau keselamatan.",
                "sku_options": ["Ikan kuning", "Ikan putih"],
            }
        )
        report = analyze_listing(listing)
        self.assertTrue(any("pack size" in item.message for item in report.findings))

    def test_many_non_fish_skus_are_warned(self):
        listing = Listing.from_dict(
            {
                "title": "Mainan Ikan Catnip untuk Kucing",
                "description": "Penerangan Produk\n\nText\n\nCiri Utama\n\nText\n\nCara Penggunaan\n\nText\n\nSesuai Untuk\n\nText\n\nNota\n\nPantau keselamatan.",
                "sku_options": ["Ikan kuning", "Beruang", "Buaya", "Dinosaur", "Ular"],
            }
        )
        report = analyze_listing(listing)
        self.assertTrue(any("not fish-related" in item.message for item in report.findings))


if __name__ == "__main__":
    unittest.main()
