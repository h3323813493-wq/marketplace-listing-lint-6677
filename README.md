# Marketplace Listing Lint

A small, dependency-free Python CLI for checking marketplace product listings before publication.

It helps cross-border sellers and marketplace operators catch common listing quality issues:

- titles that are too long or keyword-stuffed
- missing buyer-facing keywords
- weak description structure
- SKU option names that do not match the title promise
- pricing and discount sanity checks
- image checklist reminders for main-image conversion

The project includes a Malaysia TikTok Shop pet-product example, but the rules are generic enough for other marketplace listings.

## Why this exists

Small sellers often publish products with machine-translated titles, messy descriptions, and inconsistent SKU options. Those problems reduce search relevance, click-through rate, and conversion. This tool gives maintainers and operators a repeatable way to review listing drafts before they go live.

## Quick start

```bash
python -m listing_lint examples/catnip-fish-toy.json
```

Or after installing locally:

```bash
pip install -e .
listing-lint examples/catnip-fish-toy.json
```

Example output:

```text
Score: 82/100
Status: needs_improvement

[warning] title: Title mentions 1/2pcs but SKU options do not clearly expose pack-size choices.
[warning] sku: 54 SKU options detected; consider simplifying or grouping variants.
[info] images: Main image should communicate Catnip, Crinkle Sound, and Indoor Cat Play in 1-3 short callouts.
```

## Input format

The CLI accepts a JSON listing file:

```json
{
  "title": "Mainan Ikan Catnip untuk Kucing, Crinkle Sound Cat Toy 1/2pcs",
  "category": "Pet Supplies > Cat & Dog Accessories > Cat Toys",
  "description": "Penerangan Produk\n\n...",
  "keywords": ["catnip", "crinkle", "cat toy"],
  "sku_options": ["Ikan kuning", "Ikan putih"],
  "price_min": 7.36,
  "price_max": 11.58,
  "discount_price_min": 3.68,
  "discount_price_max": 5.79,
  "image_notes": ["white background", "lifestyle cat image", "benefit callout"]
}
```

## Checks included

| Area | What it checks |
| --- | --- |
| Title | length, duplicate separators, pack-size promise, keyword coverage |
| Description | required sections, paragraph spacing, safety note, overly long blocks |
| SKU | too many variants, mismatch between title and option names |
| Pricing | invalid ranges, discount strength, suspicious discount math |
| Images | main-image conversion checklist based on notes supplied by reviewer |

## Development

Run tests with:

```bash
python -m unittest discover -s tests
```

The package intentionally uses only the Python standard library so it is easy to run in low-friction environments.

## Roadmap

- CSV batch input and export
- Rule profiles for TikTok Shop, Shopee, Lazada, Amazon, and Shopify
- Malay/English keyword dictionaries by category
- HTML/Markdown report output
- GitHub Action for validating listing drafts in pull requests

## License

MIT
