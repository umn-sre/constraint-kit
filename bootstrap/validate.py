#!/usr/bin/env python3
"""
constraint-kit schema validator
────────────────────────────────
Validates all skills, roles, bundles, and the registry.

Usage:
  python validate.py                    # validate everything
  python validate.py --fix              # auto-fix safe mechanical issues
  python validate.py --fix --dry-run   # preview fixes without writing
  python validate.py --explain          # explain all validation rules
  python validate.py --json            # machine-readable JSON output
  python validate.py --file path/to/file.yaml

Exit codes:  0 = passed,  1 = errors found
Requirements: pip install pyyaml
"""

import argparse
import json
import sys
import textwrap
from pathlib import Path

import yaml

# ── Constants ──────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).parent.parent
REGISTRY_PATH = REPO_ROOT / "registry.yaml"
ROLES_DIR = REPO_ROOT / "roles"
SKILLS_DIR = REPO_ROOT / "skills"
BUNDLES_DIR = REPO_ROOT / "bundles"

CURRENT_SCHEMA_VERSION = "0.1.0"

VALID_MODES = {
    "reasoning",
    "collaborating",
    "generating-code",
    "generating-doc",
    "generating-structured",
}
VALID_PERSONAS = {"engineer", "researcher", "writer", "product-owner", "any"}
VALID_DOC_TYPES = {"technical", "academic", "literary", "structured", "product"}
VALID_ACTIVATION = {"all-required", "context-dependent"}

SKILL_REQUIRED_SECTIONS = ["## Purpose", "## Anti-Patterns", "## Transition"]

# ── Issue model ────────────────────────────────────────────────────────────


class Issue:
    def __init__(self, level, path, message, fix_id=None, fix_data=None):
        self.level = level  # "error" | "warning"
        self.path = path
        self.message = message
        self.fix_id = fix_id
        self.fix_data = fix_data or {}
        self.fixed = False

    def to_dict(self):
        return {
            "level": self.level,
            "path": self.path,
            "message": self.message,
            "fixable": self.fix_id is not None,
            "fix_id": self.fix_id,
            "fixed": self.fixed,
        }


issues: list[Issue] = []


def add_issue(level, path, message, fix_id=None, fix_data=None):
    issues.append(Issue(level, path, message, fix_id, fix_data))


def err(path, msg, fix_id=None, fix_data=None):
    add_issue("error", path, msg, fix_id, fix_data)


def warn(path, msg, fix_id=None, fix_data=None):
    add_issue("warning", path, msg, fix_id, fix_data)


# ── YAML I/O ───────────────────────────────────────────────────────────────


def load_yaml(path):
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        err(str(path), f"YAML parse error: {e}")
        return None
    except FileNotFoundError:
        err(str(path), "File not found")
        return None


def save_yaml(path, data):
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(
            data,
            f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )


def get_all_skill_ids():
    ids = set()
    for meta in SKILLS_DIR.glob("*/meta.yaml"):
        d = load_yaml(meta)
        if d and "id" in d:
            ids.add(d["id"])
    return ids


# ── Skill validation ───────────────────────────────────────────────────────


def validate_skill(skill_dir):
    label = f"skills/{skill_dir.name}"
    meta_path = skill_dir / "meta.yaml"
    skill_path = skill_dir / "SKILL.md"

    if not meta_path.exists():
        err(
            label,
            "missing meta.yaml — create using schema/skill.schema.yaml as template",
        )
        return False

    if not skill_path.exists():
        warn(
            label,
            "missing SKILL.md",
            fix_id="skill_md_stub",
            fix_data={"skill_dir": str(skill_dir), "skill_id": skill_dir.name},
        )

    data = load_yaml(meta_path)
    if data is None:
        return False

    ok = True
    for field in [
        "id",
        "name",
        "description",
        "schema_version",
        "modes",
        "tags",
    ]:
        if field not in data:
            err(
                f"{label}/meta.yaml",
                f"missing required field '{field}' — see schema/skill.schema.yaml",
            )
            ok = False
    if not ok:
        return False

    if data["id"] != skill_dir.name:
        err(
            f"{label}/meta.yaml",
            f"id '{data['id']}' does not match directory name '{skill_dir.name}' "
            f"— rename the directory or correct the id",
        )
        ok = False

    sv = data.get("schema_version")
    if sv is None:
        err(
            f"{label}/meta.yaml",
            "missing schema_version",
            fix_id="schema_version_missing",
            fix_data={"path": str(meta_path)},
        )
        ok = False
    elif sv != CURRENT_SCHEMA_VERSION:
        err(
            f"{label}/meta.yaml",
            f"schema_version '{sv}' should be '{CURRENT_SCHEMA_VERSION}'",
            fix_id="schema_version_wrong",
            fix_data={"path": str(meta_path)},
        )
        ok = False

    modes = data.get("modes", [])
    if not modes:
        err(
            f"{label}/meta.yaml",
            f"modes must have at least one value — valid: {sorted(VALID_MODES)}",
        )
        ok = False
    for m in modes:
        if m not in VALID_MODES:
            err(
                f"{label}/meta.yaml",
                f"invalid mode '{m}' — valid: {sorted(VALID_MODES)}",
            )
            ok = False

    if len(data.get("tags", [])) < 2:
        err(f"{label}/meta.yaml", "tags must contain at least 2 values")
        ok = False

    for p in data.get("personas", []):
        if p not in VALID_PERSONAS:
            err(
                f"{label}/meta.yaml",
                f"invalid persona '{p}' — valid: {sorted(VALID_PERSONAS)}",
            )
            ok = False

    if "personas" not in data:
        warn(
            f"{label}/meta.yaml",
            "personas field absent — add 'personas: [any]' to be explicit",
            fix_id="personas_missing",
            fix_data={"path": str(meta_path)},
        )

    if "generating-doc" in modes and "doc_type" not in data:
        warn(
            f"{label}/meta.yaml",
            f"generating-doc in modes but doc_type not set — valid: {sorted(VALID_DOC_TYPES)}",
            fix_id="doc_type_missing",
            fix_data={"path": str(meta_path)},
        )

    if "doc_type" in data and data["doc_type"] not in VALID_DOC_TYPES:
        err(
            f"{label}/meta.yaml",
            f"invalid doc_type '{data['doc_type']}' — valid: {sorted(VALID_DOC_TYPES)}",
        )
        ok = False

    prov = data.get("provenance")
    if prov:
        for pf in ["source_repo", "source_file", "source_url", "adapted_date"]:
            if pf not in prov:
                err(
                    f"{label}/meta.yaml",
                    f"provenance missing required field '{pf}'",
                )
                ok = False

    if "version" not in data:
        warn(
            f"{label}/meta.yaml",
            "version field absent — add 'version: \"0.1.0\"'",
            fix_id="version_missing",
            fix_data={"path": str(meta_path)},
        )

    if skill_path.exists():
        content = skill_path.read_text()
        for section in SKILL_REQUIRED_SECTIONS:
            if section not in content:
                warn(
                    f"{label}/SKILL.md",
                    f"missing recommended section '{section}' — "
                    "see docs/HOW_TO_CONTRIBUTE.md for the SKILL.md template",
                )

    return ok


# ── Role validation ────────────────────────────────────────────────────────


def validate_role(role_path, known_skill_ids):
    label = f"roles/{role_path.name}"
    data = load_yaml(role_path)
    if data is None:
        return False

    ok = True
    for field in [
        "id",
        "name",
        "description",
        "schema_version",
        "persona",
        "skills",
    ]:
        if field not in data:
            err(
                label,
                f"missing required field '{field}' — see schema/role.schema.yaml",
            )
            ok = False
    if not ok:
        return False

    if data["id"] != role_path.stem:
        err(
            label,
            f"id '{data['id']}' does not match filename '{role_path.stem}'",
        )
        ok = False

    sv = data.get("schema_version")
    if sv is None:
        err(
            label,
            "missing schema_version",
            fix_id="schema_version_missing",
            fix_data={"path": str(role_path)},
        )
        ok = False
    elif sv != CURRENT_SCHEMA_VERSION:
        err(
            label,
            f"schema_version '{sv}' should be '{CURRENT_SCHEMA_VERSION}'",
            fix_id="schema_version_wrong",
            fix_data={"path": str(role_path)},
        )
        ok = False

    if data.get("persona") not in VALID_PERSONAS:
        err(
            label,
            f"invalid persona '{data.get('persona')}' — valid: {sorted(VALID_PERSONAS)}",
        )
        ok = False

    all_mode_keys = list(VALID_MODES) + ["all_modes"]
    for mode_key, mode_data in data.get("skills", {}).items():
        if mode_key.replace("-", "_") not in [
            m.replace("-", "_") for m in all_mode_keys
        ]:
            warn(
                label,
                f"unexpected mode key '{mode_key}' — valid: {sorted(all_mode_keys)}",
            )
        if not isinstance(mode_data, dict):
            continue
        for bucket in ["required", "recommended"]:
            for sid in mode_data.get(bucket, []):
                if sid not in known_skill_ids:
                    err(
                        label,
                        f"unknown skill '{sid}' in skills.{mode_key}.{bucket} "
                        f"— add this skill to the library first",
                    )
                    ok = False
    return ok


# ── Bundle validation ──────────────────────────────────────────────────────


def validate_bundle(bundle_path, known_skill_ids):
    label = f"bundles/{bundle_path.name}"
    data = load_yaml(bundle_path)
    if data is None:
        return False

    ok = True
    for field in ["id", "name", "description", "schema_version", "skills"]:
        if field not in data:
            err(
                label,
                f"missing required field '{field}' — see schema/bundle.schema.yaml",
            )
            ok = False
    if not ok:
        return False

    if data["id"] != bundle_path.stem:
        err(
            label,
            f"id '{data['id']}' does not match filename '{bundle_path.stem}'",
        )
        ok = False

    sv = data.get("schema_version")
    if sv is None:
        err(
            label,
            "missing schema_version",
            fix_id="schema_version_missing",
            fix_data={"path": str(bundle_path)},
        )
        ok = False
    elif sv != CURRENT_SCHEMA_VERSION:
        err(
            label,
            f"schema_version '{sv}' should be '{CURRENT_SCHEMA_VERSION}'",
            fix_id="schema_version_wrong",
            fix_data={"path": str(bundle_path)},
        )
        ok = False

    skill_list = data.get("skills", [])
    if not skill_list:
        err(label, "skills list must not be empty")
        ok = False
    for sid in skill_list:
        if sid not in known_skill_ids:
            err(
                label,
                f"references unknown skill '{sid}' — add this skill first",
            )
            ok = False

    if "activation" in data and data["activation"] not in VALID_ACTIVATION:
        err(
            label,
            f"invalid activation '{data['activation']}' — valid: {sorted(VALID_ACTIVATION)}",
        )
        ok = False

    for p in data.get("personas", []):
        if p not in VALID_PERSONAS:
            err(
                label,
                f"invalid persona '{p}' — valid: {sorted(VALID_PERSONAS)}",
            )
            ok = False
    return ok


# ── Registry validation ────────────────────────────────────────────────────


def validate_registry(known_skill_ids, known_role_ids, known_bundle_ids):
    label = "registry.yaml"
    data = load_yaml(REGISTRY_PATH)
    if data is None:
        return False

    ok = True
    reg_skill_ids = {s["id"] for s in data.get("skills", [])}
    reg_role_ids = {r["id"] for r in data.get("roles", [])}
    reg_bundle_ids = {b["id"] for b in data.get("bundles", [])}

    for sid in known_skill_ids:
        if sid not in reg_skill_ids:
            warn(
                label,
                f"skill '{sid}' on disk has no registry entry — add it to registry.yaml",
                fix_id="registry_skill_missing",
                fix_data={"skill_id": sid},
            )

    for entry in data.get("skills", []):
        if entry.get("id") not in known_skill_ids:
            err(
                label,
                f"registry references skill '{entry.get('id')}' not found on disk",
            )
            ok = False

    for rid in known_role_ids:
        if rid not in reg_role_ids:
            warn(
                label,
                f"role '{rid}' on disk has no registry entry",
                fix_id="registry_role_missing",
                fix_data={"role_id": rid},
            )

    for entry in data.get("roles", []):
        if entry.get("id") not in known_role_ids:
            err(
                label,
                f"registry references role '{entry.get('id')}' not found on disk",
            )
            ok = False

    for bid in known_bundle_ids:
        if bid not in reg_bundle_ids:
            warn(
                label,
                f"bundle '{bid}' on disk has no registry entry",
                fix_id="registry_bundle_missing",
                fix_data={"bundle_id": bid},
            )

    for entry in data.get("bundles", []):
        if entry.get("id") not in known_bundle_ids:
            err(
                label,
                f"registry references bundle '{entry.get('id')}' not found on disk",
            )
            ok = False

    for entry in data.get("bundles", []):
        for sid in entry.get("skills", []):
            if sid not in known_skill_ids:
                err(
                    label,
                    f"registry bundle '{entry.get('id')}' references unknown skill '{sid}'",
                )
                ok = False
    return ok


# ── Auto-fix engine ────────────────────────────────────────────────────────


def apply_fixes(dry_run):
    fixable = [i for i in issues if i.fix_id and not i.fixed]
    if not fixable:
        print("  Nothing to fix.")
        return 0

    applied = 0
    for issue in fixable:
        if _apply_one(issue, dry_run):
            issue.fixed = True
            applied += 1
    return applied


def _apply_one(issue, dry_run):
    fid = issue.fix_id
    fd = issue.fix_data
    tag = "  [DRY RUN]" if dry_run else "  Fixed    "

    if fid == "schema_version_missing":
        path = Path(fd["path"])
        data = load_yaml(path)
        if data is None:
            return False
        print(
            f"{tag} {issue.path}: set schema_version → '{CURRENT_SCHEMA_VERSION}'"
        )
        if not dry_run:
            data["schema_version"] = CURRENT_SCHEMA_VERSION
            save_yaml(path, data)
        return True

    if fid == "schema_version_wrong":
        path = Path(fd["path"])
        data = load_yaml(path)
        if data is None:
            return False
        print(
            f"{tag} {issue.path}: correct schema_version → '{CURRENT_SCHEMA_VERSION}'"
        )
        if not dry_run:
            data["schema_version"] = CURRENT_SCHEMA_VERSION
            save_yaml(path, data)
        return True

    if fid == "version_missing":
        path = Path(fd["path"])
        data = load_yaml(path)
        if data is None:
            return False
        print(f"{tag} {issue.path}: add version: '0.1.0'")
        if not dry_run:
            data["version"] = "0.1.0"
            save_yaml(path, data)
        return True

    if fid == "personas_missing":
        path = Path(fd["path"])
        data = load_yaml(path)
        if data is None:
            return False
        print(f"{tag} {issue.path}: add personas: [any]")
        if not dry_run:
            data["personas"] = ["any"]
            save_yaml(path, data)
        return True

    if fid == "doc_type_missing":
        path = Path(fd["path"])
        data = load_yaml(path)
        if data is None:
            return False
        print(
            f"{tag} {issue.path}: add doc_type: technical  ← review and update if needed"
        )
        if not dry_run:
            data["doc_type"] = "technical"
            save_yaml(path, data)
        return True

    if fid == "skill_md_stub":
        skill_dir = Path(fd["skill_dir"])
        skill_id = fd["skill_id"]
        out_path = skill_dir / "SKILL.md"
        print(f"{tag} {issue.path}: create stub SKILL.md")
        if not dry_run:
            stub = (
                f"# Skill: {skill_id.replace('-', ' ').title()}\n"
                "## Purpose\n[Describe what this skill ensures and why it matters.]\n\n"
                "## When This Skill Is Active\n[Describe when this skill applies.]\n\n"
                "## Agent Behavior\n[Describe what the agent must do.]\n\n"
                "## Anti-Patterns\n- Do NOT [specific thing to avoid]\n\n"
                "## Transition\n[Describe what to hand off to next.]\n"
            )
            out_path.write_text(stub)
        return True

    if fid in (
        "registry_skill_missing",
        "registry_role_missing",
        "registry_bundle_missing",
    ):
        print(f"{tag} {issue.path}: add entry to registry.yaml")
        if not dry_run:
            _fix_registry(fid, fd)
        return True

    return False


def _fix_registry(fid, fd):
    registry = load_yaml(REGISTRY_PATH)
    if registry is None:
        return

    if fid == "registry_skill_missing":
        sid = fd["skill_id"]
        meta = load_yaml(SKILLS_DIR / sid / "meta.yaml") or {}
        registry.setdefault("skills", []).append(
            {
                "id": sid,
                "name": meta.get("name", sid),
                "file": f"skills/{sid}/SKILL.md",
                "meta": f"skills/{sid}/meta.yaml",
                "modes": meta.get("modes", []),
                "personas": meta.get("personas", ["any"]),
                "tags": meta.get("tags", []),
                "pairs_with": meta.get("pairs_with", []),
                "provenance": meta.get("provenance"),
                "description": meta.get("description", ""),
                "version": meta.get("version", CURRENT_SCHEMA_VERSION),
            }
        )

    elif fid == "registry_role_missing":
        rid = fd["role_id"]
        role = load_yaml(ROLES_DIR / f"{rid}.yaml") or {}
        registry.setdefault("roles", []).append(
            {
                "id": rid,
                "name": role.get("name", rid),
                "file": f"roles/{rid}.yaml",
                "persona": role.get("persona", "any"),
                "description": role.get("description", ""),
                "tags": role.get("tags", []),
                "version": role.get("version", CURRENT_SCHEMA_VERSION),
            }
        )

    elif fid == "registry_bundle_missing":
        bid = fd["bundle_id"]
        bundle = load_yaml(BUNDLES_DIR / f"{bid}.yaml") or {}
        registry.setdefault("bundles", []).append(
            {
                "id": bid,
                "name": bundle.get("name", bid),
                "file": f"bundles/{bid}.yaml",
                "personas": bundle.get("personas", ["any"]),
                "primary_modes": bundle.get("primary_modes", []),
                "skills": bundle.get("skills", []),
                "description": bundle.get("description", ""),
                "tags": bundle.get("tags", []),
                "version": bundle.get("version", CURRENT_SCHEMA_VERSION),
            }
        )

    save_yaml(REGISTRY_PATH, registry)


# ── Explain mode ───────────────────────────────────────────────────────────

RULES = [
    (
        "id must match filename/directory",
        "The id field in every YAML file must exactly match the filename (roles, bundles) "
        "or directory name (skills). The renderer locates files by id — a mismatch causes "
        "silent load failures.",
    ),
    (
        "schema_version must be current",
        f'Every file must declare schema_version: "{CURRENT_SCHEMA_VERSION}". This lets '
        "the validator detect files written against an older schema and handle them safely "
        "during version transitions. Auto-fixable.",
    ),
    (
        "Modes must be from the valid set",
        f"Valid modes: {sorted(VALID_MODES)}. Arbitrary mode names break skill resolution "
        "in the renderer. Skills with no modes are never loaded.",
    ),
    (
        "At least two tags required",
        "Tags drive skill discovery in the registry. Fewer than two tags makes a skill "
        "hard to find and suggest. Tags should be lowercase kebab-case nouns.",
    ),
    (
        "Personas must be from the valid set",
        f"Valid personas: {sorted(VALID_PERSONAS)}. Personas filter which skills and roles "
        "appear during bootstrap for each user type.",
    ),
    (
        "doc_type recommended when generating-doc in modes",
        f"Valid doc_types: {sorted(VALID_DOC_TYPES)}. This helps the renderer present the "
        "right sub-type context to the AI. Auto-fixable with 'technical' as default.",
    ),
    (
        "SKILL.md should have Purpose, Anti-Patterns, and Transition sections",
        "Purpose explains why the skill matters. Anti-Patterns give the agent specific "
        "things to avoid. Transition tells the agent what to do next — this prevents "
        "context drift between skills. A stub is auto-creatable via --fix.",
    ),
    (
        "Role and bundle skill references must resolve",
        "Every skill id referenced in a role or bundle must exist in the skills/ directory. "
        "Unresolvable ids cause the renderer to crash or produce incomplete output.",
    ),
    (
        "Registry must match disk",
        "registry.yaml is the master index. Skills, roles, and bundles on disk with no "
        "registry entry are invisible to consumers. Missing entries are auto-fixable.",
    ),
    (
        "Provenance block must be complete",
        "When a skill is adapted from an external source, provenance must include "
        "source_repo, source_file, source_url, and adapted_date. This ensures attribution "
        "is complete and upstream diffs can be tracked.",
    ),
]


def print_explanations():
    print("constraint-kit validation rules\n")
    print("=" * 62)
    for title, explanation in RULES:
        print(f"\n{title}")
        print("-" * len(title))
        for line in textwrap.wrap(explanation, width=60):
            print(f"  {line}")
    print()


# ── Output ─────────────────────────────────────────────────────────────────


def print_results(as_json):
    errs = [i for i in issues if i.level == "error" and not i.fixed]
    warns = [i for i in issues if i.level == "warning" and not i.fixed]
    fixed = [i for i in issues if i.fixed]
    fixable_remaining = [i for i in issues if i.fix_id and not i.fixed]

    if as_json:
        print(
            json.dumps(
                {
                    "passed": not errs,
                    "error_count": len(errs),
                    "warning_count": len(warns),
                    "fixed_count": len(fixed),
                    "issues": [i.to_dict() for i in issues],
                },
                indent=2,
            )
        )
        return

    print()

    if fixed:
        print(f"Fixed ({len(fixed)}):")
        for i in fixed:
            print(f"  FIXED  {i.path}: {i.message}")
        print()

    if warns:
        print(f"Warnings ({len(warns)}):")
        for i in warns:
            hint = " [run --fix to auto-resolve]" if i.fix_id else ""
            print(f"  WARN   {i.path}: {i.message}{hint}")
        print()

    if errs:
        print(f"Errors ({len(errs)}):")
        for i in errs:
            print(f"  ERROR  {i.path}: {i.message}")
        print()

    skill_count = len(list(SKILLS_DIR.glob("*/meta.yaml")))
    role_count = len(list(ROLES_DIR.glob("*.yaml")))
    bundle_count = len(list(BUNDLES_DIR.glob("*.yaml")))

    if errs:
        print(f"FAILED — {len(errs)} error(s), {len(warns)} warning(s)")
        if fixable_remaining:
            count = len(fixable_remaining)
            print(
                f"         {count} issue(s) can be auto-fixed: python validate.py --fix"
            )
    else:
        print(
            f"PASSED — {skill_count} skills, {role_count} roles, {bundle_count} bundles"
        )
        if warns:
            print(f"         {len(warns)} warning(s)")
            if fixable_remaining:
                print(
                    f"         {len(fixable_remaining)} can be auto-fixed: python validate.py --fix"
                )
        if fixed:
            print(f"         {len(fixed)} issue(s) auto-fixed this run")


# ── Runner ─────────────────────────────────────────────────────────────────


def run_validation(do_skills, do_roles, do_bundles, do_registry, single_file):
    known_skill_ids = get_all_skill_ids()
    known_role_ids = {p.stem for p in ROLES_DIR.glob("*.yaml")}
    known_bundle_ids = {p.stem for p in BUNDLES_DIR.glob("*.yaml")}

    if single_file:
        path = Path(single_file)
        if "skills" in path.parts:
            validate_skill(path if path.is_dir() else path.parent)
        elif "roles" in path.parts:
            validate_role(
                path if path.suffix == ".yaml" else path, known_skill_ids
            )
        elif "bundles" in path.parts:
            validate_bundle(
                path if path.suffix == ".yaml" else path, known_skill_ids
            )
        else:
            print(f"Cannot determine file type: {single_file}")
            sys.exit(1)
        return

    if do_skills:
        print("Validating skills...")
        for d in sorted(SKILLS_DIR.iterdir()):
            if d.is_dir():
                validate_skill(d)

    if do_roles:
        print("Validating roles...")
        for p in sorted(ROLES_DIR.glob("*.yaml")):
            validate_role(p, known_skill_ids)

    if do_bundles:
        print("Validating bundles...")
        for p in sorted(BUNDLES_DIR.glob("*.yaml")):
            validate_bundle(p, known_skill_ids)

    if do_registry:
        print("Validating registry...")
        validate_registry(known_skill_ids, known_role_ids, known_bundle_ids)


# ── CLI ────────────────────────────────────────────────────────────────────


def main():
    p = argparse.ArgumentParser(
        description="constraint-kit schema validator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--skills", action="store_true")
    p.add_argument("--roles", action="store_true")
    p.add_argument("--bundles", action="store_true")
    p.add_argument("--registry", action="store_true")
    p.add_argument("--file", metavar="PATH")
    p.add_argument("--fix", action="store_true", help="Auto-fix safe issues")
    p.add_argument(
        "--dry-run", action="store_true", help="Preview fixes only (with --fix)"
    )
    p.add_argument(
        "--explain", action="store_true", help="Explain all validation rules"
    )
    p.add_argument(
        "--json", action="store_true", help="Machine-readable JSON output"
    )
    args = p.parse_args()

    if args.explain:
        print_explanations()
        return

    any_flag = (
        args.skills or args.roles or args.bundles or args.registry or args.file
    )
    run_validation(
        do_skills=args.skills or not any_flag,
        do_roles=args.roles or not any_flag,
        do_bundles=args.bundles or not any_flag,
        do_registry=args.registry or not any_flag,
        single_file=args.file,
    )

    if args.fix:
        print()
        label = (
            "Previewing fixes (dry run)..."
            if args.dry_run
            else "Applying fixes..."
        )
        print(label)
        apply_fixes(dry_run=args.dry_run)

    print_results(as_json=args.json)
    sys.exit(
        0
        if not [i for i in issues if i.level == "error" and not i.fixed]
        else 1
    )


if __name__ == "__main__":
    main()
