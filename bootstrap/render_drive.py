#!/usr/bin/env python3
"""
constraint-kit Drive session starter renderer
──────────────────────────────────────────────
Renders fully self-contained session starter documents for each role,
suitable for Google Drive sharing with non-technical users.

All skill content is inlined — no file references. Users attach the
rendered .md file to a Gemini or Claude browser session and go.

Usage:
  # Render all four role starters to ./drive-output/
  python render_drive.py

  # Render a specific role
  python render_drive.py --role researcher

  # Render to a custom output directory
  python render_drive.py --out /path/to/drive/folder

  # Render with a specific starting mode
  python render_drive.py --role researcher --mode collaborating

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
ROLES_DIR = REPO_ROOT / "roles"
SKILLS_DIR = REPO_ROOT / "skills"
BUNDLES_DIR = REPO_ROOT / "bundles"
RENDERERS_DIR = Path(__file__).parent / "renderers"

# Default starting modes per role — sensible for a first Drive session
ROLE_DEFAULT_MODE = {
    "engineer": "collaborating",
    "researcher": "collaborating",
    "writer": "collaborating",
    "product-owner": "collaborating",
}

# Default bundles to activate per role for Drive starters
ROLE_DEFAULT_BUNDLES = {
    "engineer": ["new-feature-design"],
    "researcher": ["research-inquiry"],
    "writer": ["document-drafting"],
    "product-owner": ["structured-output"],
}

# ── Loaders ────────────────────────────────────────────────────────────────


def load_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_role(role_id: str) -> dict:
    path = ROLES_DIR / f"{role_id}.yaml"
    if not path.exists():
        sys.exit(f"ERROR: Role '{role_id}' not found.")
    return load_yaml(path)


def load_skill_with_content(skill_id: str) -> dict:
    meta_path = SKILLS_DIR / skill_id / "meta.yaml"
    skill_path = SKILLS_DIR / skill_id / "SKILL.md"

    if not meta_path.exists():
        return {
            "id": skill_id,
            "name": skill_id,
            "description": "",
            "modes": [],
            "content": "",
        }

    meta = load_yaml(meta_path)
    meta["file"] = str(skill_path.relative_to(REPO_ROOT))

    if skill_path.exists():
        meta["content"] = skill_path.read_text().strip()
    else:
        meta["content"] = f"# {meta.get('name', skill_id)}\n(Content not found)"

    return meta


def load_bundle(bundle_id: str) -> dict:
    path = BUNDLES_DIR / f"{bundle_id}.yaml"
    if not path.exists():
        sys.exit(f"ERROR: Bundle '{bundle_id}' not found.")
    return load_yaml(path)


# ── Skill resolution ───────────────────────────────────────────────────────


def resolve_skills_with_content(role: dict, mode: str, bundles: list) -> tuple:
    """Returns (required_skills, recommended_skills) with full content inlined."""
    required_ids = set()
    recommended_ids = set()

    # all_modes baseline
    for sid in role.get("skills", {}).get("all_modes", {}).get("required", []):
        required_ids.add(sid)
    for sid in (
        role.get("skills", {}).get("all_modes", {}).get("recommended", [])
    ):
        recommended_ids.add(sid)

    # mode-specific
    mode_data = role.get("skills", {}).get(mode, {})
    for sid in mode_data.get("required", []):
        required_ids.add(sid)
    for sid in mode_data.get("recommended", []):
        recommended_ids.add(sid)

    # bundles
    for bundle_id in bundles:
        bundle = load_bundle(bundle_id)
        for sid in bundle.get("skills", []):
            required_ids.add(sid)

    recommended_ids -= required_ids

    required = [load_skill_with_content(sid) for sid in sorted(required_ids)]
    recommended = [
        load_skill_with_content(sid) for sid in sorted(recommended_ids)
    ]

    return required, recommended


# ── Render ─────────────────────────────────────────────────────────────────


def render_role(role_id: str, mode: str, out_dir: Path):
    role = load_role(role_id)
    bundles = ROLE_DEFAULT_BUNDLES.get(role_id, [])
    required, recommended = resolve_skills_with_content(role, mode, bundles)

    env = Environment(
        loader=FileSystemLoader(str(RENDERERS_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.tests["containing"] = lambda seq, val: val in seq

    template = env.get_template("drive-session-starter.j2")

    context = {
        "project": "[fill in your project name]",
        "role": role,
        "task": "[fill in what you are working on]",
        "mode": mode,
        "doc_type": "",
        "skills_full": required,
        "recommended": recommended,
        "context": "",
        "session_history": [],
        "render_date": date.today().isoformat(),
    }

    output = template.render(**context)

    # Output filename: role-session-starter.md
    out_file = out_dir / f"{role_id}-session-starter.md"
    out_file.write_text(output)
    print(f"  Written: {out_file}")
    return out_file


# ── CLI ────────────────────────────────────────────────────────────────────

ALL_ROLES = ["engineer", "researcher", "writer", "product-owner"]


def main():
    parser = argparse.ArgumentParser(
        description="Render Drive session starters for constraint-kit roles"
    )
    parser.add_argument(
        "--role",
        choices=ALL_ROLES,
        help="Render a specific role only (default: all roles)",
    )
    parser.add_argument(
        "--mode",
        choices=[
            "reasoning",
            "collaborating",
            "generating-doc",
            "generating-code",
            "generating-structured",
        ],
        help="Starting mode (default: collaborating for all roles)",
    )
    parser.add_argument(
        "--out",
        default="drive-output",
        metavar="DIR",
        help="Output directory (default: ./drive-output/)",
    )
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    roles_to_render = [args.role] if args.role else ALL_ROLES

    print(f"Rendering Drive session starters → {out_dir}/")
    print()

    for role_id in roles_to_render:
        mode = args.mode or ROLE_DEFAULT_MODE.get(role_id, "collaborating")
        print(f"  [{role_id}] mode: {mode}")
        render_role(role_id, mode, out_dir)

    print()
    print(f"Done. {len(roles_to_render)} file(s) written to {out_dir}/")
    print()
    print("Next steps:")
    print("  1. Open each file and fill in 'project' and 'task' fields,")
    print("     or leave them as placeholders for users to fill in.")
    print("  2. Upload to your constraint-kit shared Drive folder.")
    print("  3. Share the folder with your community.")
    print("  4. Users: make a copy, fill in the top fields, attach to session.")


if __name__ == "__main__":
    main()
