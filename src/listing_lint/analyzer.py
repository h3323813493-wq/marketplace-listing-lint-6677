from __future__ import annotations

import re
from collections import Counter

from .models import Finding, Listing, Report

SECTION_HINTS = (
    "penerangan produk",
    "ciri utama",
    "cara penggunaan",
    "sesuai untuk",
    "nota",
)

PACK_PATTERN = re.compile(r"\b(?:1\s*/\s*2\s*pcs|1\s*or\s*2\s*pcs|1pcs|2pcs|pack|set)\b", re.I)


def analyze_listing(listing: Listing) -> Report:
    findings: list[Finding] = []
    findings.extend(_check_title(listing))
    findings.extend(_check_description(listing))
    findings.extend(_check_sku(listing))
    findings.extend(_check_pricing(listing))
    findings.extend(_check_images(listing))

    score = max(0, min(100, 100 - sum(item.points for item in findings)))
    return Report(score=score, findings=tuple(findings))


def _check_title(listing: Listing) -> list[Finding]:
    title = listing.title.strip()
    lowered = title.lower()
    findings: list[Finding] = []

    if not title:
        return [Finding("error", "title", "Title is required.", 40)]
    if len(title) > 120:
        findings.append(Finding("warning", "title", "Title is longer than 120 characters; shorten for mobile readability.", 10))
    elif len(title) < 35:
        findings.append(Finding("info", "title", "Title is concise; make sure it still contains buyer search keywords.", 2))

    separators = sum(title.count(mark) for mark in [",", "|", "/", "-"])
    if separators > 5:
        findings.append(Finding("warning", "title", "Title uses many separators and may look keyword-stuffed.", 7))

    missing_keywords = [kw for kw in listing.keywords if kw.lower() not in lowered]
    if missing_keywords:
        findings.append(Finding("warning", "title", f"Missing title keywords: {', '.join(missing_keywords[:5])}.", 8))

    if PACK_PATTERN.search(title) and not _sku_has_pack_options(listing.sku_options):
        findings.append(Finding("warning", "title", "Title mentions pack size, but SKU options do not clearly expose pack-size choices.", 8))

    return findings


def _check_description(listing: Listing) -> list[Finding]:
    description = listing.description.strip()
    lowered = description.lower()
    findings: list[Finding] = []

    if not description:
        return [Finding("error", "description", "Description is required.", 35)]

    missing_sections = [section for section in SECTION_HINTS if section not in lowered]
    if missing_sections:
        findings.append(Finding("warning", "description", f"Missing helpful sections: {', '.join(missing_sections)}.", 10))

    paragraphs = [block for block in re.split(r"\n\s*\n", description) if block.strip()]
    if len(paragraphs) < 3:
        findings.append(Finding("warning", "description", "Description should use short sections instead of one dense block.", 10))

    long_lines = [line for line in description.splitlines() if len(line) > 180]
    if long_lines:
        findings.append(Finding("info", "description", "Some lines are long; split them for better mobile scanning.", 3))

    if "pantau" not in lowered and "safety" not in lowered and "keselamatan" not in lowered:
        findings.append(Finding("info", "description", "Add a short safety note for pet products.", 4))

    return findings


def _check_sku(listing: Listing) -> list[Finding]:
    findings: list[Finding] = []
    options = listing.sku_options
    if not options:
        findings.append(Finding("info", "sku", "No SKU options supplied for checking.", 2))
        return findings

    if len(options) > 30:
        findings.append(Finding("warning", "sku", f"{len(options)} SKU options detected; consider simplifying or grouping variants.", 8))

    normalized = [option.lower() for option in options]
    counts = Counter(normalized)
    duplicates = [name for name, count in counts.items() if count > 1]
    if duplicates:
        findings.append(Finding("warning", "sku", f"Duplicate SKU option names found: {', '.join(duplicates[:5])}.", 6))

    title = listing.title.lower()
    if "fish" in title or "ikan" in title:
        non_fish = [option for option in options if "ikan" not in option.lower() and "fish" not in option.lower()]
        if len(non_fish) >= max(3, len(options) // 3):
            findings.append(Finding("warning", "sku", "Many SKU options are not fish-related while the title promises a fish toy.", 8))

    return findings


def _check_pricing(listing: Listing) -> list[Finding]:
    findings: list[Finding] = []
    pmin = listing.price_min
    pmax = listing.price_max
    dmin = listing.discount_price_min
    dmax = listing.discount_price_max

    if pmin is None or pmax is None:
        findings.append(Finding("info", "pricing", "Price range not supplied.", 2))
        return findings

    if pmin <= 0 or pmax <= 0 or pmin > pmax:
        findings.append(Finding("error", "pricing", "Invalid price range.", 25))

    if dmin is not None and dmax is not None:
        if dmin <= 0 or dmax <= 0 or dmin > dmax:
            findings.append(Finding("error", "pricing", "Invalid discount price range.", 25))
        elif dmin >= pmin or dmax >= pmax:
            findings.append(Finding("warning", "pricing", "Discount price is not lower than retail price.", 10))
        else:
            discount_rate = 1 - (dmin / pmin)
            if discount_rate < 0.3:
                findings.append(Finding("info", "pricing", "Discount is under 30%; consider stronger launch pricing for traffic tests.", 4))
            elif discount_rate >= 0.5:
                findings.append(Finding("info", "pricing", "Launch discount is strong; monitor margin and stock risk.", 1))

    return findings


def _check_images(listing: Listing) -> list[Finding]:
    notes = " ".join(listing.image_notes).lower()
    findings: list[Finding] = []

    if not notes:
        findings.append(Finding("info", "images", "Add image notes so the reviewer can confirm main-image quality.", 3))
        return findings

    if "white" not in notes and "clean" not in notes:
        findings.append(Finding("info", "images", "Main image should use a clean or white background.", 3))
    if "lifestyle" not in notes and "cat" not in notes:
        findings.append(Finding("info", "images", "Add a lifestyle image showing the pet using the product.", 3))
    if "callout" not in notes and "catnip" not in notes and "crinkle" not in notes:
        findings.append(Finding("info", "images", "Main image should communicate Catnip, Crinkle Sound, and Indoor Cat Play in 1-3 short callouts.", 3))

    return findings


def _sku_has_pack_options(options: tuple[str, ...]) -> bool:
    return any(PACK_PATTERN.search(option) for option in options)
