#!/usr/bin/env python3
"""Audit semantic structure in math-exam crash-course LaTeX sources.

This is a triage tool. It can prove structural defects, but it cannot certify
mathematical correctness, pedagogical depth, or whether a list split is natural.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


PROBLEM_RE = re.compile(r"\\problemid\{([^{}]+)\}")
ANSWER_RE = re.compile(r"\\begin\{examanswer\}(.*?)\\end\{examanswer\}", re.S)
IDEA_RE = re.compile(r"\\begin\{idea\}(.*?)\\end\{idea\}", re.S)
LINK_RE = re.compile(r"\\knowledgelink\{")
MOCK_PAPER_RE = re.compile(r"\\begin\{mockpaper\}(.*?)\\end\{mockpaper\}", re.S)
FORBIDDEN_PRINT_RE = re.compile(
    r"\\begin\{(?:examanswer|idea|methodbox)\}|\\knowledgelink\{|"
    r"考试规范解答|思路与动机|解题方法|(?<!无)答案|提示"
)
STRUCTURE_RE = re.compile(
    r"\\begin\{(?:examsteps|enumerate|itemize|align\*?|gather\*?|cases)\}"
    r"|\\paragraph\{|\\textbf\{(?:步骤|情形|第[一二三四五六七八九十]+问)"
)
BOLD_RE = re.compile(r"\\textbf\{([^{}]{1,100})\}")


@dataclass
class ProblemRow:
    problem_id: str
    source: str
    answers: int
    ideas: int
    ordered: bool
    knowledge_links: int
    answer_length: int
    idea_length: int
    answer_structured: bool
    idea_bold_labels: int


def strip_comments(text: str) -> str:
    return re.sub(r"(?m)(?<!\\)%.*$", "", text)


def visible_length(text: str) -> int:
    text = strip_comments(text)
    text = re.sub(r"\\knowledgelink\{[^{}]+\}\{([^{}]*)\}", r"\1", text)
    text = re.sub(r"\\(?:begin|end)\{[^{}]*\}", " ", text)
    text = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?", " ", text)
    text = re.sub(r"[{}$\\_^&~]", " ", text)
    return len(re.sub(r"\s+", "", text))


def source_for_offset(
    sources: list[tuple[Path, int, int]], offset: int
) -> str:
    for path, start, end in sources:
        if start <= offset < end:
            return str(path)
    return "<combined>"


def balanced_group(text: str, start: int) -> tuple[str, int]:
    if start >= len(text) or text[start] != "{":
        raise ValueError("expected opening brace")
    depth = 0
    for index in range(start, len(text)):
        char = text[index]
        escaped = index > 0 and text[index - 1] == "\\"
        if char == "{" and not escaped:
            depth += 1
        elif char == "}" and not escaped:
            depth -= 1
            if depth == 0:
                return text[start + 1 : index], index + 1
    raise ValueError("unbalanced LaTeX group")


def command_first_args(text: str, command: str) -> list[str]:
    results: list[str] = []
    pattern = re.compile(re.escape(command) + r"\s*\{")
    cleaned = strip_comments(text)
    for match in pattern.finditer(cleaned):
        brace = cleaned.find("{", match.start())
        try:
            arg, _ = balanced_group(cleaned, brace)
        except ValueError:
            continue
        results.append(arg.strip())
    return results


def audit(files: list[Path], require_links: bool, allowed: set[str]) -> dict:
    chunks: list[str] = []
    source_ranges: list[tuple[Path, int, int]] = []
    cursor = 0
    for path in files:
        text = path.read_text(encoding="utf-8")
        chunks.append(text)
        source_ranges.append((path, cursor, cursor + len(text)))
        cursor += len(text) + 2
    combined = "\n\n".join(chunks)

    errors: list[str] = []
    warnings: list[str] = []
    rows: list[ProblemRow] = []
    matches = list(PROBLEM_RE.finditer(combined))
    seen: set[str] = set()

    for index, match in enumerate(matches):
        problem_id = match.group(1).strip()
        if problem_id in seen:
            errors.append(f"duplicate problem id: {problem_id}")
        seen.add(problem_id)
        stop = matches[index + 1].start() if index + 1 < len(matches) else len(combined)
        unit = combined[match.end() : stop]
        answers = list(ANSWER_RE.finditer(unit))
        ideas = list(IDEA_RE.finditer(unit))
        answer = answers[0].group(1) if answers else ""
        idea = ideas[0].group(1) if ideas else ""
        row = ProblemRow(
            problem_id=problem_id,
            source=source_for_offset(source_ranges, match.start()),
            answers=len(answers),
            ideas=len(ideas),
            ordered=bool(
                answers and ideas and answers[0].start() < ideas[0].start()
            ),
            knowledge_links=len(LINK_RE.findall(idea)),
            answer_length=visible_length(answer),
            idea_length=visible_length(idea),
            answer_structured=bool(STRUCTURE_RE.search(answer)),
            idea_bold_labels=len(BOLD_RE.findall(idea)),
        )
        rows.append(row)

        if problem_id not in allowed:
            if len(answers) != 1:
                errors.append(
                    f"{problem_id}: expected one examanswer, found {len(answers)}"
                )
            if len(ideas) != 1:
                errors.append(f"{problem_id}: expected one idea, found {len(ideas)}")
            if answers and ideas and not row.ordered:
                errors.append(f"{problem_id}: idea precedes formal answer")
            if answers and not row.answer_length:
                errors.append(f"{problem_id}: empty formal answer")
            if ideas and not row.idea_length:
                errors.append(f"{problem_id}: empty ideas section")
            if require_links and ideas and not row.knowledge_links:
                errors.append(f"{problem_id}: ideas section has no knowledge link")

        if row.answer_length >= 500 and not row.answer_structured:
            warnings.append(
                f"{problem_id}: long formal answer lacks visible structure; review manually"
            )
        if row.idea_length < 120 and problem_id not in allowed:
            warnings.append(
                f"{problem_id}: short motivation candidate; inspect depth manually"
            )

    label_counts = [row.idea_bold_labels for row in rows]
    run_start = 0
    for index in range(1, len(rows) + 1):
        ended = index == len(rows) or label_counts[index] != label_counts[run_start]
        if not ended:
            continue
        count = label_counts[run_start]
        if count in (3, 4) and index - run_start >= 4:
            warnings.append(
                f"{rows[run_start].problem_id}..{rows[index - 1].problem_id}: "
                f"{index - run_start} consecutive motivations use {count} bold labels; "
                "check for forced templating"
            )
        run_start = index

    for paper_index, match in enumerate(MOCK_PAPER_RE.finditer(combined), start=1):
        leak = FORBIDDEN_PRINT_RE.search(match.group(1))
        if leak:
            errors.append(
                f"mockpaper {paper_index}: forbidden answer/hint token {leak.group(0)!r}"
            )

    declared = command_first_args(combined, r"\DeclareMockProblem")
    printed = command_first_args(combined, r"\PrintMockProblem")
    solved = command_first_args(combined, r"\SolveMockProblem")
    for name, values in (
        ("declared", declared),
        ("printed", printed),
        ("solved", solved),
    ):
        duplicates = sorted({item for item in values if values.count(item) > 1})
        if duplicates:
            errors.append(f"duplicate {name} mock IDs: {', '.join(duplicates)}")
    if declared or printed or solved:
        declared_set, printed_set, solved_set = map(set, (declared, printed, solved))
        if declared_set != printed_set:
            errors.append(
                "mock declaration/print ID mismatch: "
                f"missing_print={sorted(declared_set - printed_set)}, "
                f"undeclared_print={sorted(printed_set - declared_set)}"
            )
        if declared_set != solved_set:
            errors.append(
                "mock declaration/solution ID mismatch: "
                f"missing_solution={sorted(declared_set - solved_set)}, "
                f"undeclared_solution={sorted(solved_set - declared_set)}"
            )

    return {
        "files": [str(path) for path in files],
        "problem_count": len(rows),
        "rows": [asdict(row) for row in rows],
        "errors": errors,
        "warnings": warnings,
        "mock_counts": {
            "declared": len(declared),
            "printed": len(printed),
            "solved": len(solved),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--allow-missing", action="append", default=[])
    parser.add_argument("--require-links", action="store_true")
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()

    missing_files = [str(path) for path in args.files if not path.is_file()]
    if missing_files:
        parser.error(f"missing input files: {', '.join(missing_files)}")

    result = audit(args.files, args.require_links, set(args.allow_missing))
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    print(
        f"problems={result['problem_count']} "
        f"errors={len(result['errors'])} warnings={len(result['warnings'])}"
    )
    for issue in result["errors"]:
        print(f"ERROR: {issue}")
    for issue in result["warnings"]:
        print(f"WARNING: {issue}")
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
