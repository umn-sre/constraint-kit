# constraint-kit Extensions

This directory lists community extension repositories that add
domain-specific roles, skills, and bundles to constraint-kit.

## What is an extension?

An extension is a separate repository — maintained by its author —
that follows the constraint-kit schema and provides skills, roles,
or bundles for a specific domain, organization, or workflow.

Examples of what an extension might contain:
- Domain-specific writing skills (legal, medical, scientific)
- Organization-specific engineering conventions
- Specialized agile or project management templates
- Industry-specific research frameworks

## How to build an extension

1. Create a new repository (public or private)
2. Add a `constraint-kit.yaml` manifest at the repo root
3. Add your skills in `skills/<id>/` with `SKILL.md` and `meta.yaml`
4. Add your roles in `roles/<id>.yaml` (optional)
5. Add your bundles in `bundles/<id>.yaml` (optional)

Your `constraint-kit.yaml` manifest:

```yaml
schema_version: "0.1.0"
name: My Domain Skills
description: Skills for [domain] work built on constraint-kit.
constraint_kit_version: ">=0.1.0"

skills:
  - id: my-skill
    file: skills/my-skill/SKILL.md
    meta: skills/my-skill/meta.yaml

roles:
  - id: my-role
    file: roles/my-role.yaml

bundles:
  - id: my-bundle
    file: bundles/my-bundle.yaml
```

## How to list your extension here

1. Ensure your repo has a valid `constraint-kit.yaml` manifest
2. Ensure at least one skill, role, or bundle follows the schema
3. Fork constraint-kit and add an entry to `contrib/extensions.yaml`
4. Submit a pull request

Listing is reviewed for schema compliance only — not content quality.
You are responsible for maintaining your extension.

## Using an extension in your project

In your `.constraint-kit/agent.yaml`:

```yaml
extension: path/to/local/clone/constraint-kit.yaml
# or reference directly in task_skills/roles if skills are copied locally
```

See `docs/HOW_TO_USE_GITHUB.md` for full usage instructions.
