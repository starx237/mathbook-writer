#!/usr/bin/env python3
"""对模块化 LaTeX 教材做确定性的结构与日志预检。

本脚本不判断数学正确性；它只定位需要人工复核的工程问题。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


INPUT_RE = re.compile(r"\\(?:input|include)\s*\{([^{}]+)\}")
LABEL_RE = re.compile(r"\\label\s*\{([^{}]+)\}")
REF_RE = re.compile(
    r"\\(?:ref|eqref|pageref|autoref|cref|Cref|vref)\*?\s*\{([^{}]+)\}"
)
HYPERREF_RE = re.compile(r"\\hyperref\s*\[([^\]]+)\]")
PLACEHOLDER_RE = re.compile(
    r"(?i)(?:\bTODO\b|\bFIXME\b|待补|待写|此处补充|PLACEHOLDER)"
)
LOG_RULES = (
    ("error", re.compile(r"Undefined control sequence")),
    ("error", re.compile(r"LaTeX Error:")),
    ("error", re.compile(r"Emergency stop")),
    ("error", re.compile(r"Fatal error")),
    ("error", re.compile(r"There were undefined references")),
    ("error", re.compile(r"There were undefined citations")),
    ("error", re.compile(r"multiply defined", re.IGNORECASE)),
    ("warning", re.compile(r"Overfull \\[hv]box")),
    ("warning", re.compile(r"Underfull \\[hv]box")),
    ("warning", re.compile(r"Missing character:")),
    ("warning", re.compile(r"Token not allowed in a PDF string")),
    ("warning", re.compile(r"Rerun to get cross-references right")),
)


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    location: str
    message: str


def strip_comments(text: str) -> str:
    """删除未转义百分号后的注释，保留行号。"""
    cleaned: list[str] = []
    for line in text.splitlines():
        cut = len(line)
        for i, char in enumerate(line):
            if char != "%":
                continue
            backslashes = 0
            j = i - 1
            while j >= 0 and line[j] == "\\":
                backslashes += 1
                j -= 1
            if backslashes % 2 == 0:
                cut = i
                break
        cleaned.append(line[:cut])
    return "\n".join(cleaned)


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def resolve_input(owner: Path, project_root: Path, raw: str) -> Path | None:
    if "\\" in raw or "#" in raw:
        return None
    candidate = Path(raw.strip())
    if candidate.suffix == "":
        candidate = candidate.with_suffix(".tex")
    if candidate.is_absolute():
        return candidate.resolve()

    # TeX 默认相对启动目录（通常是主文件目录）查找；有些工程则把
    # 子文件路径写成相对当前文件。先采用 TeX 主路径，再兼容后一种体例。
    from_root = (project_root / candidate).resolve()
    if from_root.exists():
        return from_root
    from_owner = (owner.parent / candidate).resolve()
    if from_owner.exists():
        return from_owner
    return from_root


def collect_input_graph(main: Path) -> tuple[list[Path], list[Finding]]:
    main = main.resolve()
    project_root = main.parent
    pending = [main]
    seen: set[Path] = set()
    files: list[Path] = []
    findings: list[Finding] = []

    while pending:
        current = pending.pop()
        if current in seen:
            continue
        seen.add(current)
        if not current.exists():
            findings.append(
                Finding("error", "missing-input", str(current), "输入文件不存在")
            )
            continue
        files.append(current)
        text = strip_comments(current.read_text(encoding="utf-8"))
        for match in INPUT_RE.finditer(text):
            child = resolve_input(current, project_root, match.group(1))
            if child is None:
                findings.append(
                    Finding(
                        "warning",
                        "dynamic-input",
                        f"{current}:{line_number(text, match.start())}",
                        f"无法静态解析输入：{match.group(1)}",
                    )
                )
                continue
            pending.append(child)
    return sorted(files), findings


def load_terms(path: Path | None) -> list[dict[str, str]]:
    if path is None:
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    terms = data.get("forbidden", [])
    if not isinstance(terms, list):
        raise ValueError("terms.json 的 forbidden 必须是数组")
    normalized = []
    for item in terms:
        if not isinstance(item, dict) or not item.get("pattern"):
            raise ValueError("每个 forbidden 项必须含非空 pattern")
        normalized.append(
            {
                "pattern": str(item["pattern"]),
                "replacement": str(item.get("replacement", "")),
                "severity": str(item.get("severity", "warning")).lower(),
            }
        )
    return normalized


def scan_sources(files: Iterable[Path], terms: list[dict[str, str]]) -> list[Finding]:
    findings: list[Finding] = []
    label_locations: dict[str, list[str]] = {}
    references: list[tuple[str, str]] = []

    for path in files:
        raw = path.read_text(encoding="utf-8")
        text = strip_comments(raw)

        for match in LABEL_RE.finditer(text):
            loc = f"{path}:{line_number(text, match.start())}"
            label_locations.setdefault(match.group(1), []).append(loc)

        for regex in (REF_RE, HYPERREF_RE):
            for match in regex.finditer(text):
                loc = f"{path}:{line_number(text, match.start())}"
                for label in (part.strip() for part in match.group(1).split(",")):
                    # 宏定义中的 #1 或动态控制序列无法在静态阶段解析。
                    if label and "#" not in label and "\\" not in label:
                        references.append((label, loc))

        for match in PLACEHOLDER_RE.finditer(text):
            findings.append(
                Finding(
                    "warning",
                    "placeholder",
                    f"{path}:{line_number(text, match.start())}",
                    f"发现占位文本：{match.group(0)}",
                )
            )

        for item in terms:
            try:
                regex = re.compile(item["pattern"])
            except re.error as exc:
                raise ValueError(f"无效术语正则 {item['pattern']!r}: {exc}") from exc
            for match in regex.finditer(text):
                replacement = item["replacement"]
                suggestion = f"；建议：{replacement}" if replacement else ""
                severity = item["severity"]
                if severity not in {"error", "warning", "info"}:
                    severity = "warning"
                findings.append(
                    Finding(
                        severity,
                        "forbidden-term",
                        f"{path}:{line_number(text, match.start())}",
                        f"命中受控术语：{match.group(0)}{suggestion}",
                    )
                )

    for label, locations in label_locations.items():
        if len(locations) > 1:
            findings.append(
                Finding(
                    "error",
                    "duplicate-label",
                    ", ".join(locations),
                    f"标签重复：{label}",
                )
            )

    labels = set(label_locations)
    for label, loc in references:
        if label not in labels:
            findings.append(
                Finding("error", "undefined-reference", loc, f"引用不存在：{label}")
            )

    exercise_suffix_re = re.compile(r"^ch\d{2}-\d+$")
    exercises = {
        label[3:]
        for label in labels
        if label.startswith("ex:") and exercise_suffix_re.fullmatch(label[3:])
    }
    solutions = {
        label[4:]
        for label in labels
        if label.startswith("sol:") and exercise_suffix_re.fullmatch(label[4:])
    }
    for suffix in sorted(exercises - solutions):
        findings.append(
            Finding("error", "missing-solution", "label graph", f"习题无解答：ex:{suffix}")
        )
    for suffix in sorted(solutions - exercises):
        findings.append(
            Finding("error", "orphan-solution", "label graph", f"解答无题目：sol:{suffix}")
        )

    return findings


def scan_log(path: Path | None) -> list[Finding]:
    if path is None:
        return []
    if not path.exists():
        return [Finding("error", "missing-log", str(path), "构建日志不存在")]
    findings: list[Finding] = []
    for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        for severity, regex in LOG_RULES:
            if regex.search(line):
                findings.append(
                    Finding(severity, "latex-log", f"{path}:{number}", line.strip())
                )
    return findings


def print_findings(findings: list[Finding], as_json: bool) -> None:
    ordered = sorted(
        findings,
        key=lambda item: (
            {"error": 0, "warning": 1, "info": 2}.get(item.severity, 3),
            item.code,
            item.location,
        ),
    )
    if as_json:
        print(
            json.dumps(
                [finding.__dict__ for finding in ordered],
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    if not ordered:
        print("未发现静态结构或日志问题。")
        return
    for item in ordered:
        print(f"[{item.severity.upper()}] {item.code} {item.location}: {item.message}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="检查 LaTeX 输入图、标签、题解配对、术语、占位符和构建日志。"
    )
    parser.add_argument("main", type=Path, help="主 TeX 文件")
    parser.add_argument("--terms", type=Path, help="受控术语 JSON")
    parser.add_argument("--log", type=Path, help="XeLaTeX/latexmk 构建日志")
    parser.add_argument("--strict", action="store_true", help="警告也返回失败")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.main.exists():
        print(f"[ERROR] 主文件不存在：{args.main}", file=sys.stderr)
        return 2
    try:
        terms = load_terms(args.terms)
        files, findings = collect_input_graph(args.main)
        findings.extend(scan_sources(files, terms))
        findings.extend(scan_log(args.log))
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] 无法完成检查：{exc}", file=sys.stderr)
        return 2

    if not args.json:
        print(f"已检查 {len(files)} 个实际输入的 TeX 文件。")
    print_findings(findings, args.json)
    errors = sum(item.severity == "error" for item in findings)
    warnings = sum(item.severity == "warning" for item in findings)
    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
