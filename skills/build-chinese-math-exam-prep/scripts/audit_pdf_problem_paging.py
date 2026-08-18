#!/usr/bin/env python3
"""Locate problem/answer/motivation starts in a rendered crash-course PDF."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

try:
    import pdfplumber
except ImportError as exc:  # pragma: no cover - environment diagnostic
    raise SystemExit("pdfplumber is required: install it before running this audit") from exc


PROBLEM_RE = re.compile(r"\\(?:problemid|SolveMockProblem)\{([^{}]+)\}")


@dataclass
class Row:
    problem_id: str
    problem_page: int | None
    answer_page: int | None
    idea_page: int | None
    statement_answer_split: bool | None
    answer_crosses_page: bool | None
    status: str


def position(page_index: int, top: float) -> float:
    return page_index * 100_000.0 + top


def search_all(document, needle: str) -> list[tuple[float, int, float]]:
    found: list[tuple[float, int, float]] = []
    for page_index, page in enumerate(document.pages):
        for match in page.search(needle, regex=False):
            top = float(match["top"])
            found.append((position(page_index, top), page_index, top))
    return found


def ordered_problem_positions(
    document,
    ids: list[str],
    minimum_page: int,
    answer_positions: list[tuple[float, int, float]],
):
    chosen: list[tuple[float, int, float] | None] = []
    previous = position(max(0, minimum_page - 1), 0)
    for problem_id in ids:
        candidates = [item for item in search_all(document, problem_id) if item[0] > previous]
        current = None
        for index, candidate in enumerate(candidates):
            next_same = (
                candidates[index + 1][0]
                if index + 1 < len(candidates)
                else float("inf")
            )
            next_answer = next(
                (item for item in answer_positions if item[0] > candidate[0]), None
            )
            if next_answer is not None and next_answer[0] < next_same:
                current = candidate
                break
        if current is None and candidates:
            current = candidates[0]
        chosen.append(current)
        if current is not None:
            previous = current[0]
    return chosen


def first_between(
    positions: list[tuple[float, int, float]], start: float, stop: float
) -> tuple[float, int, float] | None:
    return next((item for item in positions if start < item[0] < stop), None)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("tex", nargs="+", type=Path)
    parser.add_argument("--min-body-page", type=int, default=1)
    parser.add_argument("--answer-label", default="考试规范解答")
    parser.add_argument("--idea-label", default="思路与动机")
    parser.add_argument("--csv-output", type=Path)
    args = parser.parse_args()

    if not args.pdf.is_file():
        parser.error(f"missing PDF: {args.pdf}")
    missing = [str(path) for path in args.tex if not path.is_file()]
    if missing:
        parser.error(f"missing TeX files: {', '.join(missing)}")

    ids: list[str] = []
    for path in args.tex:
        ids.extend(PROBLEM_RE.findall(path.read_text(encoding="utf-8")))
    if not ids:
        parser.error("no \\problemid markers found")

    rows: list[Row] = []
    with pdfplumber.open(args.pdf) as document:
        answer_positions = search_all(document, args.answer_label)
        idea_positions = search_all(document, args.idea_label)
        starts = ordered_problem_positions(
            document, ids, args.min_body_page, answer_positions
        )

        for index, problem_id in enumerate(ids):
            start = starts[index]
            if start is None:
                rows.append(
                    Row(problem_id, None, None, None, None, None, "problem id not found")
                )
                continue
            next_start = (
                starts[index + 1][0]
                if index + 1 < len(starts) and starts[index + 1] is not None
                else position(len(document.pages), 0)
            )
            answer = first_between(answer_positions, start[0], next_start)
            idea = first_between(
                idea_positions, answer[0] if answer else start[0], next_start
            )
            status_parts: list[str] = []
            if answer is None:
                status_parts.append("answer label missing")
            if idea is None:
                status_parts.append("idea label missing")
            statement_split = start[1] != answer[1] if answer else None
            answer_crosses = answer[1] != idea[1] if answer and idea else None
            if statement_split:
                status_parts.append("statement/answer page split")
            if answer_crosses:
                status_parts.append("formal answer reaches a later page")
            rows.append(
                Row(
                    problem_id=problem_id,
                    problem_page=start[1] + 1,
                    answer_page=answer[1] + 1 if answer else None,
                    idea_page=idea[1] + 1 if idea else None,
                    statement_answer_split=statement_split,
                    answer_crosses_page=answer_crosses,
                    status="; ".join(status_parts) if status_parts else "ok",
                )
            )

    if args.csv_output:
        args.csv_output.parent.mkdir(parents=True, exist_ok=True)
        with args.csv_output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
            writer.writeheader()
            writer.writerows(asdict(row) for row in rows)

    missing_count = sum(
        row.problem_page is None or row.answer_page is None or row.idea_page is None
        for row in rows
    )
    split_count = sum(bool(row.statement_answer_split) for row in rows)
    cross_count = sum(bool(row.answer_crosses_page) for row in rows)
    print(
        f"problems={len(rows)} missing_markers={missing_count} "
        f"statement_answer_splits={split_count} answer_cross_page={cross_count}"
    )
    for row in rows:
        if row.status != "ok":
            print(
                f"{row.problem_id}: pages "
                f"{row.problem_page}/{row.answer_page}/{row.idea_page}: {row.status}"
            )
    return 1 if missing_count else 0


if __name__ == "__main__":
    sys.exit(main())
