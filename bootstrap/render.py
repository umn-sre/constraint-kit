#!/usr/bin/env python3
"""
constraint-kit bootstrap renderer
──────────────────────────────────
Reads a project's agent.yaml (or active-task.md config),
resolves skills from the registry, and renders a session starter
in the requested target format.

Usage:
  # Repo path (technical)
  python render.py .constraint-kit/agent.yaml

  # Explicit output target override
  python render.py .constraint-kit/agent.yaml --target copilot-instructions

  # Drive path: render from filled-in template
  python render.py --drive bootstrap/templates/new-project-drive.md

  # List available roles, skills, bundles
  python render.py --list

Requirements:
  pip install pyyaml jinja2
"""

import argparse
import sys
from datetime import date
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

# ── Paths ──────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).parent.parent
REGISTRY_PATH = REPO_ROOT / "registry.yaml"
ROLES_DIR = REPO_ROOT / "roles"
SKILLS_DIR = REPO_ROOT / "skills"
BUNDLES_DIR = REPO_ROOT / "bundles"
RENDERERS_DIR = Path(__file__).parent / "renderers"

TARGET_TO_TEMPLATE = {
    "session-prompt": "session-prompt.j2",
    "copilot-instructions": "copilot-instructions.j2",
    "active-task-md": "active-task.j2",
    "skill-md": "skill-md.j2",
}

TARGET_TO_OUTPUT = {
    "session-prompt": "session-starter.md",
    "copilot-instructions": ".github/copilot-instructions.md",
    "active-task-md": "active-task.md",
    "skill-md": "SKILL.md",
}

# ── Loaders ────────────────────────────────────────────────────────────────


def load_registry():
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_role(role_id: str) -> dict:
    role_path = ROLES_DIR / f"{role_id}.yaml"
    if not role_path.exists():
        sys.exit(f"ERROR: Role '{role_id}' not found at {role_path}")
    with open(role_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_skill(skill_id: str) -> dict:
    meta_path = SKILLS_DIR / skill_id / "meta.yaml"
    skill_path = SKILLS_DIR / skill_id / "SKILL.md"
    if not meta_path.exists():
        # Fall back to registry entry only
        return {
            "id": skill_id,
            "name": skill_id,
            "description": "",
            "file": str(skill_path),
            "modes": [],
        }
    with open(meta_path, encoding="utf-8") as f:
        meta = yaml.safe_load(f)
    meta["file"] = str(skill_path.relative_to(REPO_ROOT))
    return meta


def load_bundle(bundle_id: str) -> dict:
    bundle_path = BUNDLES_DIR / f"{bundle_id}.yaml"
    if not bundle_path.exists():
        sys.exit(f"ERROR: Bundle '{bundle_id}' not found at {bundle_path}")
    with open(bundle_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ── Skill resolution ───────────────────────────────────────────────────────


def resolve_skills(
    role: dict, mode: str, task_skills: list, bundles: list, suppress: list
) -> tuple:
    """
    Returns (required_skills, recommended_skills) as lists of skill dicts.
    Merges role baseline + task_skills + bundle skills, minus suppressed.
    """
    required_ids = set()
    recommended_ids = set()

    # Role baseline — all_modes
    for sid in role.get("skills", {}).get("all_modes", {}).get("required", []):
        required_ids.add(sid)
    for sid in (
        role.get("skills", {}).get("all_modes", {}).get("recommended", [])
    ):
        recommended_ids.add(sid)

    # Role baseline — mode-specific
    mode_skills = role.get("skills", {}).get(mode, {})
    for sid in mode_skills.get("required", []):
        required_ids.add(sid)
    for sid in mode_skills.get("recommended", []):
        recommended_ids.add(sid)

    # Task-specific additional skills
    for sid in task_skills:
        required_ids.add(sid)

    # Bundle skills
    for bundle_id in bundles:
        bundle = load_bundle(bundle_id)
        for sid in bundle.get("skills", []):
            required_ids.add(sid)

    # Suppress
    for sid in suppress:
        required_ids.discard(sid)
        recommended_ids.discard(sid)

    # recommended should not overlap with required
    recommended_ids -= required_ids

    required_skills = [load_skill(sid) for sid in sorted(required_ids)]
    recommended_skills = [load_skill(sid) for sid in sorted(recommended_ids)]

    return required_skills, recommended_skills


# ── Rendering ──────────────────────────────────────────────────────────────


def render(agent: dict, target_override: str = None) -> str:
    role = load_role(agent["role"])
    mode = agent["mode"]
    target = target_override or agent.get("target", "session-prompt")

    required_skills, recommended_skills = resolve_skills(
        role=role,
        mode=mode,
        task_skills=agent.get("task_skills", []),
        bundles=agent.get("bundles", []),
        suppress=agent.get("suppress_skills", []),
    )

    template_name = TARGET_TO_TEMPLATE.get(target)
    if not template_name:
        sys.exit(
            f"ERROR: Unknown target '{target}'. Valid: {list(TARGET_TO_TEMPLATE.keys())}"
        )

    env = Environment(
        loader=FileSystemLoader(str(RENDERERS_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # Add a simple 'containing' test for Jinja2
    env.tests["containing"] = lambda seq, val: val in seq

    template = env.get_template(template_name)

    context = {
        "project": agent.get("project", "unnamed-project"),
        "role": role,
        "task": agent.get("task", "(no task defined)"),
        "mode": mode,
        "skills": required_skills,
        "recommended": recommended_skills,
        "context": agent.get("context", ""),
        "session_history": agent.get("session_history", []),
        "doc_type": agent.get("doc_type", ""),
        "render_date": date.today().isoformat(),
    }

    return template.render(**context)


# ── CLI ────────────────────────────────────────────────────────────────────


def cmd_list():
    registry = load_registry()
    print("\n── ROLES ──────────────────────────────────────────")
    for r in registry.get("roles", []):
        print(f"  {r['id']:<20} {r['description'].strip()[:60]}")

    print("\n── BUNDLES ─────────────────────────────────────────")
    for b in registry.get("bundles", []):
        print(f"  {b['id']:<20} {b['description'].strip()[:60]}")

    print("\n── SKILLS ──────────────────────────────────────────")
    for s in registry.get("skills", []):
        modes = ", ".join(s.get("modes", []))
        print(f"  {s['id']:<28} [{modes}]")
    print()


def load_agent_with_base(path: Path) -> dict:
    """
    Load agent.yaml, merging with base file if extends: is set.

    Merge strategy:
    - Scalar fields (role, mode, task, target, project): override wins
    - List fields (task_skills, bundles, suppress_skills): override wins
    - session_history: lists concatenated (base first, then override)
    - context: override wins if present and non-empty; base used otherwise
    - extends: consumed during merge, not passed to renderer
    """
    with path.open(encoding="utf-8") as f:
        agent = yaml.safe_load(f) or {}

    base_path_str = agent.pop("extends", None)
    if not base_path_str:
        return agent

    base_path = path.parent / base_path_str
    if not base_path.exists():
        sys.exit(f"ERROR: extends base file not found: {base_path}")

    with base_path.open(encoding="utf-8") as f:
        base = yaml.safe_load(f) or {}

    # Base values are the starting point — override file wins on conflict
    merged = {**base}

    for key, value in agent.items():
        if key == "session_history":
            # Concatenate — base history first, then override additions
            base_history = base.get("session_history") or []
            override_history = value or []
            merged["session_history"] = base_history + override_history
        elif key == "context":
            # Override wins only if non-empty
            if value and str(value).strip():
                merged["context"] = value
        else:
            merged[key] = value

    return merged


def cmd_render(agent_path: str, target_override: str, write: bool):
    path = Path(agent_path)
    if not path.exists():
        sys.exit(f"ERROR: File not found: {agent_path}")

    agent = load_agent_with_base(path)

    output = render(agent, target_override)

    target = target_override or agent.get("target", "session-prompt")
    output_filename = TARGET_TO_OUTPUT.get(target, "output.md")

    if write:
        out_path = path.parent / output_filename
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output)
        print(f"Written to: {out_path}")
    else:
        print(output)


def main():
    parser = argparse.ArgumentParser(
        description="constraint-kit bootstrap renderer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "agent_yaml",
        nargs="?",
        help="Path to agent.yaml (e.g. .constraint-kit/agent.yaml)",
    )
    parser.add_argument(
        "--target",
        choices=list(TARGET_TO_TEMPLATE.keys()),
        help="Override the target format from agent.yaml",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write rendered output to file instead of printing to stdout",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available roles, bundles, and skills",
    )

    args = parser.parse_args()

    if args.list:
        cmd_list()
        return

    if not args.agent_yaml:
        parser.print_help()
        sys.exit(1)

    cmd_render(args.agent_yaml, args.target, args.write)


if __name__ == "__main__":
    main()
