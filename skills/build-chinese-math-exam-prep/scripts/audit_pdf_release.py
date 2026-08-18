#!/usr/bin/env python3
"""Run manifest-driven deterministic checks on released coursebook PDFs."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError as exc:  # pragma: no cover - environment diagnostic
    raise SystemExit("pypdf is required: install it before running this audit") from exc


A4 = (595.276, 841.89)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def count_images(page) -> int:
    resources = page.get("/Resources")
    if resources is None:
        return 0
    resources = resources.get_object()
    xobjects = resources.get("/XObject")
    if xobjects is None:
        return 0
    return sum(
        1
        for value in xobjects.get_object().values()
        if value.get_object().get("/Subtype") == "/Image"
    )


def link_counts(reader: PdfReader) -> tuple[int, int, list[int]]:
    internal = 0
    external = 0
    per_page: list[int] = []
    for page in reader.pages:
        page_links = 0
        for reference in page.get("/Annots", []):
            annotation = reference.get_object()
            if annotation.get("/Subtype") != "/Link":
                continue
            page_links += 1
            action = annotation.get("/A")
            if action is not None and action.get_object().get("/URI") is not None:
                external += 1
            else:
                internal += 1
        per_page.append(page_links)
    return internal, external, per_page


def check_pdf(base: Path, spec: dict) -> tuple[list[str], dict]:
    path = (base / spec["path"]).resolve()
    errors: list[str] = []
    if not path.is_file():
        return [f"{spec['path']}: file missing"], {"path": str(path)}

    reader = PdfReader(path)
    pages = len(reader.pages)
    if pages < int(spec.get("min_pages", 1)):
        errors.append(f"{spec['path']}: {pages} pages below minimum")
    if spec.get("max_pages") is not None and pages > int(spec["max_pages"]):
        errors.append(f"{spec['path']}: {pages} pages above maximum")

    if spec.get("page_size", "A4").upper() == "A4":
        tolerance = float(spec.get("page_size_tolerance", 4.0))
        for index, page in enumerate(reader.pages, start=1):
            width = float(page.mediabox.width)
            height = float(page.mediabox.height)
            portrait = abs(width - A4[0]) <= tolerance and abs(height - A4[1]) <= tolerance
            landscape = abs(width - A4[1]) <= tolerance and abs(height - A4[0]) <= tolerance
            if not (portrait or landscape):
                errors.append(
                    f"{spec['path']}: page {index} is {width:.1f}x{height:.1f}, not A4"
                )

    outline_count = len(reader.outline)
    if spec.get("require_outline", False) and not outline_count:
        errors.append(f"{spec['path']}: no PDF outline/bookmarks")

    internal, external, links_by_page = link_counts(reader)
    if internal < int(spec.get("min_internal_links", 0)):
        errors.append(f"{spec['path']}: only {internal} internal links")
    images = sum(count_images(page) for page in reader.pages)
    if images < int(spec.get("min_images", 0)):
        errors.append(f"{spec['path']}: only {images} image XObjects")

    for paper in spec.get("printable_ranges", []):
        start = int(paper["start"])
        end = int(paper["end"])
        if start < 1 or end > pages or start > end:
            errors.append(
                f"{spec['path']}: invalid printable range {start}-{end}"
            )
            continue
        terms = list(paper.get("forbidden_text", []))
        for page_number in range(start, end + 1):
            text = reader.pages[page_number - 1].extract_text() or ""
            for term in terms:
                if term in text:
                    errors.append(
                        f"{spec['path']}: printable page {page_number} contains {term!r}"
                    )
            if paper.get("forbid_links", True) and links_by_page[page_number - 1]:
                errors.append(
                    f"{spec['path']}: printable page {page_number} has "
                    f"{links_by_page[page_number - 1]} link annotations"
                )

    report = {
        "path": str(path),
        "pages": pages,
        "outline_items": outline_count,
        "internal_links": internal,
        "external_links": external,
        "images": images,
        "sha256": sha256(path),
    }
    return errors, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    if not args.manifest.is_file():
        parser.error(f"manifest not found: {args.manifest}")

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    specs = manifest.get("pdfs", [])
    if not specs:
        parser.error("manifest must contain a non-empty 'pdfs' list")

    all_errors: list[str] = []
    reports: list[dict] = []
    for spec in specs:
        errors, report = check_pdf(args.manifest.parent, spec)
        all_errors.extend(errors)
        reports.append(report)

    result = {"pdfs": reports, "errors": all_errors}
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    for report in reports:
        print(
            f"{report['path']}: pages={report.get('pages')} "
            f"links={report.get('internal_links')}/{report.get('external_links')} "
            f"images={report.get('images')} sha256={report.get('sha256')}"
        )
    for error in all_errors:
        print(f"ERROR: {error}")
    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main())

