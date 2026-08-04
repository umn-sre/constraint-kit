#!/usr/bin/env python3
"""Validate constraint-kit marketplace and plugin structure.

Stdlib only. Exits non-zero with a list of problems, prints OK otherwise.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ERRORS: list[str] = []


def err(msg: str) -> None:
    ERRORS.append(msg)


def parse_frontmatter(path: Path) -> dict[str, str]:
    """Parse simple 'key: value' YAML frontmatter without external deps."""
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    if not match:
        err(f"{path}: missing frontmatter block")
        return {}
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.startswith((" ", "\t", "#")):
            continue
        if ":" not in line:
            err(f"{path}: malformed frontmatter line: {line!r}")
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


def check_relative_links(md: Path) -> None:
    """Every relative markdown link inside a skill must resolve."""
    for target in re.findall(r"\]\(([^)#]+)\)", md.read_text(encoding="utf-8")):
        target = target.strip()
        if re.match(r"^[a-z]+://", target) or target.startswith("mailto:"):
            continue
        if not (md.parent / target).exists():
            err(f"{md}: broken relative link -> {target}")


def check_skill(skill_dir: Path) -> None:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        err(f"{skill_dir}: missing SKILL.md")
        return
    fields = parse_frontmatter(skill_md)
    if not fields.get("name"):
        err(f"{skill_md}: frontmatter missing 'name'")
    elif fields["name"] != skill_dir.name:
        err(f"{skill_md}: name '{fields['name']}' != directory '{skill_dir.name}'")
    if not fields.get("description"):
        err(f"{skill_md}: frontmatter missing 'description'")
    for md in skill_dir.rglob("*.md"):
        check_relative_links(md)


def check_agent(agent_md: Path) -> None:
    fields = parse_frontmatter(agent_md)
    if not fields.get("name"):
        err(f"{agent_md}: frontmatter missing 'name'")
    if not fields.get("description"):
        err(f"{agent_md}: frontmatter missing 'description'")


def check_plugin(plugin_dir: Path) -> None:
    manifest_path = plugin_dir / "plugin.json"
    if not manifest_path.is_file():
        err(f"{plugin_dir}: missing plugin.json")
        return
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        err(f"{manifest_path}: invalid JSON ({exc})")
        return
    for field in ("name", "description", "version"):
        if not manifest.get(field):
            err(f"{manifest_path}: missing required field '{field}'")
    if manifest.get("name") != plugin_dir.name:
        err(f"{manifest_path}: name != directory '{plugin_dir.name}'")
    for listed in manifest.get("skills", []) + manifest.get("agents", []):
        if not (plugin_dir / listed).exists():
            err(f"{manifest_path}: declared path does not exist: {listed}")

    skills_dir = plugin_dir / "skills"
    if skills_dir.is_dir():
        for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
            check_skill(skill_dir)
    agents_dir = plugin_dir / "agents"
    if agents_dir.is_dir():
        for agent_md in sorted(agents_dir.glob("*.agent.md")):
            check_agent(agent_md)


def check_marketplace() -> None:
    path = ROOT / ".claude-plugin" / "marketplace.json"
    if not path.is_file():
        err(f"{path}: missing")
        return
    try:
        market = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        err(f"{path}: invalid JSON ({exc})")
        return
    if not market.get("name"):
        err(f"{path}: missing 'name'")
    listed = set()
    for entry in market.get("plugins", []):
        name = entry.get("name", "<unnamed>")
        listed.add(name)
        for field in ("description", "source"):
            if not entry.get(field):
                err(f"{path}: plugin '{name}' missing '{field}'")
        source = entry.get("source", "")
        if isinstance(source, str) and not (ROOT / source).is_dir():
            err(f"{path}: plugin '{name}' source dir not found: {source}")
    on_disk = {p.name for p in (ROOT / "plugins").iterdir() if p.is_dir()}
    for missing in on_disk - listed:
        err(f"{path}: plugin directory not listed in marketplace: {missing}")
    for phantom in listed - on_disk:
        err(f"{path}: listed plugin has no directory: {phantom}")


def main() -> int:
    check_marketplace()
    for plugin_dir in sorted(p for p in (ROOT / "plugins").iterdir() if p.is_dir()):
        check_plugin(plugin_dir)
    if ERRORS:
        print(f"FAIL — {len(ERRORS)} problem(s):")
        for problem in ERRORS:
            print(f"  - {problem}")
        return 1
    print("OK — marketplace and plugin structure valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
