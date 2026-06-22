from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .analyzer import analyze_listing
from .models import Listing


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check marketplace product listing quality.")
    parser.add_argument("listing", type=Path, help="Path to a JSON listing draft.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON report.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        raw = json.loads(args.listing.read_text(encoding="utf-8"))
    except FileNotFoundError:
        parser.error(f"Listing file not found: {args.listing}")
    except json.JSONDecodeError as exc:
        parser.error(f"Invalid JSON: {exc}")

    listing = Listing.from_dict(raw)
    report = analyze_listing(listing)

    if args.json:
        payload = {
            "score": report.score,
            "status": report.status,
            "findings": [item.__dict__ for item in report.findings],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Score: {report.score}/100")
        print(f"Status: {report.status}")
        if report.findings:
            print()
        for finding in report.findings:
            print(f"[{finding.level}] {finding.area}: {finding.message}")

    return 1 if report.status == "blocked" else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
