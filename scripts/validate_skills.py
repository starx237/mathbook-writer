#!/usr/bin/env python3
"""Validate the public skill packages in this repository."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def validate_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        return ["missing SKILL.md"]

    content = skill_file.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(content)
    if match is None:
        return ["missing or malformed YAML frontmatter"]

    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        return [f"invalid YAML frontmatter: {exc}"]

    if not isinstance(frontmatter, dict):
        return ["frontmatter must be a mapping"]
    if set(frontmatter) != {"name", "description"}:
        errors.append("frontmatter must contain only name and description")

    name = frontmatter.get("name")
    if not isinstance(name, str) or not NAME_RE.fullmatch(name):
        errors.append("name must use lowercase hyphen-case")
    elif name != skill_dir.name:
        errors.append("name must match the skill directory name")

    description = frontmatter.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append("description must be a non-empty string")
    elif len(description) > 1024 or "<" in description or ">" in description:
        errors.append("description is invalid or too long")

    agent_file = skill_dir / "agents" / "openai.yaml"
    if not agent_file.is_file():
        errors.append("missing agents/openai.yaml")
    else:
        try:
            agent = yaml.safe_load(agent_file.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"invalid agents/openai.yaml: {exc}")
        else:
            prompt = (agent or {}).get("interface", {}).get("default_prompt", "")
            if f"${name}" not in prompt:
                errors.append("default_prompt must reference the current skill name")

    return errors


def main() -> int:
    skill_dirs = sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())
    if not skill_dirs:
        print("ERROR: no skill directories found", file=sys.stderr)
        return 1

    failed = False
    for skill_dir in skill_dirs:
        errors = validate_skill(skill_dir)
        if errors:
            failed = True
            for error in errors:
                print(f"ERROR: {skill_dir.name}: {error}")
        else:
            print(f"OK: {skill_dir.name}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
