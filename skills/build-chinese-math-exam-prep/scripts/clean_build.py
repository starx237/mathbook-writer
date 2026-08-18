#!/usr/bin/env python3
"""Copy a LaTeX project to a clean temporary tree and rebuild it with XeLaTeX."""

from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


EXCLUDED_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    "__pycache__",
    "build",
    "dist",
    "rendered",
    "renders",
}
EXCLUDED_SUFFIXES = {
    ".aux",
    ".fdb_latexmk",
    ".fls",
    ".log",
    ".out",
    ".pdf",
    ".synctex.gz",
    ".toc",
    ".xdv",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ignored(_directory: str, names: list[str]) -> set[str]:
    result: set[str] = set()
    for name in names:
        if name in EXCLUDED_DIRS:
            result.add(name)
            continue
        lower = name.lower()
        if any(lower.endswith(suffix) for suffix in EXCLUDED_SUFFIXES):
            result.add(name)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("main_tex", type=Path)
    parser.add_argument("--engine", default="xelatex")
    parser.add_argument("--passes", type=int, default=3)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--allow-overfull", action="store_true")
    args = parser.parse_args()

    root = args.project_root.resolve()
    if not root.is_dir():
        parser.error(f"project root not found: {root}")
    main_source = (root / args.main_tex).resolve()
    try:
        relative_main = main_source.relative_to(root)
    except ValueError:
        parser.error("main_tex must resolve inside project_root")
    if not main_source.is_file():
        parser.error(f"main TeX file not found: {main_source}")
    if args.passes < 1:
        parser.error("--passes must be positive")
    if shutil.which(args.engine) is None:
        parser.error(f"engine not found on PATH: {args.engine}")

    with tempfile.TemporaryDirectory(prefix="math-crash-clean-build-") as temp_name:
        clean_root = Path(temp_name) / "source"
        shutil.copytree(root, clean_root, ignore=ignored)
        clean_main = clean_root / relative_main
        command = [
            args.engine,
            "-interaction=nonstopmode",
            "-halt-on-error",
            clean_main.name,
        ]
        for pass_number in range(1, args.passes + 1):
            result = subprocess.run(
                command,
                cwd=clean_main.parent,
                text=True,
                encoding="utf-8",
                errors="replace",
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            if result.returncode:
                print(result.stdout)
                print(f"ERROR: build failed on pass {pass_number}")
                return 1

        pdf = clean_main.with_suffix(".pdf")
        log = clean_main.with_suffix(".log")
        if not pdf.is_file() or not log.is_file():
            print("ERROR: engine completed without expected PDF/log")
            return 1
        log_text = log.read_text(encoding="utf-8", errors="replace")
        fatal_markers = (
            "LaTeX Error:",
            "Undefined control sequence",
            "There were undefined references",
            "Rerun to get cross-references right",
            "Missing character:",
        )
        found = [marker for marker in fatal_markers if marker in log_text]
        if not args.allow_overfull and "Overfull \\hbox" in log_text:
            found.append("Overfull \\hbox")
        if found:
            print("ERROR: log contains " + ", ".join(found))
            for line in log_text.splitlines():
                if any(marker in line for marker in found):
                    print("  " + line)
            return 1

        if args.output:
            output = args.output.resolve()
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(pdf, output)
            delivered = output
        else:
            delivered = pdf
        print(
            f"clean build ok: pages artifact={delivered} "
            f"bytes={delivered.stat().st_size} sha256={sha256(delivered)}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
