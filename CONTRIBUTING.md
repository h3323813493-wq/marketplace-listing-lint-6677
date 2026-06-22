# Contributing

Thanks for helping improve Marketplace Listing Lint.

Good first contributions:

- add listing examples for more marketplace categories
- improve title and SKU checks
- add rule profiles for TikTok Shop, Shopee, Lazada, Amazon, or Shopify
- improve Malay/English ecommerce wording checks

## Local checks

```bash
python -m unittest discover -s tests
python -m listing_lint examples/catnip-fish-toy.json
```

## Rule design principles

- Keep checks explainable.
- Prefer warnings over hard failures unless the listing is unusable.
- Avoid platform policy claims unless they are backed by public documentation.
- Keep the tool dependency-free unless there is a strong reason to add a dependency.
