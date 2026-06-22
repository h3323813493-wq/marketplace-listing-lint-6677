from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable


@dataclass(frozen=True)
class Finding:
    """A single listing-quality finding."""

    level: str
    area: str
    message: str
    points: int = 0


@dataclass(frozen=True)
class Listing:
    """Normalized product-listing draft."""

    title: str
    category: str = ""
    description: str = ""
    keywords: tuple[str, ...] = ()
    sku_options: tuple[str, ...] = ()
    price_min: float | None = None
    price_max: float | None = None
    discount_price_min: float | None = None
    discount_price_max: float | None = None
    image_notes: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Listing":
        def tuple_of_strings(value: Any) -> tuple[str, ...]:
            if value is None:
                return ()
            if isinstance(value, str):
                return (value,)
            if isinstance(value, Iterable):
                return tuple(str(item).strip() for item in value if str(item).strip())
            return ()

        def number(value: Any) -> float | None:
            if value in (None, ""):
                return None
            try:
                return float(value)
            except (TypeError, ValueError):
                return None

        return cls(
            title=str(raw.get("title", "")).strip(),
            category=str(raw.get("category", "")).strip(),
            description=str(raw.get("description", "")).strip(),
            keywords=tuple_of_strings(raw.get("keywords")),
            sku_options=tuple_of_strings(raw.get("sku_options")),
            price_min=number(raw.get("price_min")),
            price_max=number(raw.get("price_max")),
            discount_price_min=number(raw.get("discount_price_min")),
            discount_price_max=number(raw.get("discount_price_max")),
            image_notes=tuple_of_strings(raw.get("image_notes")),
        )


@dataclass(frozen=True)
class Report:
    """Listing audit result."""

    score: int
    findings: tuple[Finding, ...] = field(default_factory=tuple)

    @property
    def status(self) -> str:
        if any(item.level == "error" for item in self.findings):
            return "blocked"
        if self.score >= 85:
            return "ready"
        if self.score >= 65:
            return "needs_improvement"
        return "poor"
