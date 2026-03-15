# How to Contribute to constraint-kit

There are three ways to contribute, depending on your comfort level
with GitHub and the constraint-kit schema.

## Option A — Contribute a Skill

A skill is a single-concern constraint document. It defines how an
agent should behave in a specific situation.

**Good skills are:**
- Focused on one thing (not a grab-bag of rules)
- Applicable to more than one project or person
- Written in plain English with concrete anti-patterns
- Testable — you can tell if an agent is following them or not

**Steps:**

1. Fork the constraint-kit repository
2. Create a branch: `skill/your-skill-name`
3. Create a directory: `skills/your-skill-name/`
4. Add two files following the schema:
   - `skills/your-skill-name/SKILL.md` — the constraint content
   - `skills/your-skill-name/meta.yaml` — metadata
5. Add an entry to `registry.yaml` under `skills:`
6. Submit a pull request

**SKILL.md structure** (follow existing skills as examples):

```markdown

# Skill: [Name]

## Purpose

## When This Skill Is Active

## Agent Behavior

## Anti-Patterns

## Transition

```

**meta.yaml required fields:**

```yaml

id: your-skill-name
name: Your Skill Name
description: One sentence.
schema_version: "0.1.0"
modes: [collaborating]   # one or more valid modes
tags: [tag1, tag2]       # at least two

```

**If adapting from an external source**, include the provenance block:

```yaml

provenance:
  source_repo: owner/repo
  source_file: path/to/original.md
  source_url: https://github.com/...
  adapted_date: "YYYY-MM-DD"
  adaptation_notes: What changed from the original.

```

## Option B — Contribute a Role

A role composes skills into a working identity for a specific type
of work. Roles have a higher review bar than skills because they
affect everyone who adopts them.

**Good roles are:**
- Scoped to a real, distinct type of knowledge work
- Not an extension of an existing role (add skills instead)
- Complete across all modes (or explicitly blank for unused modes)
- Accompanied by a clear onboarding note for new users

**Steps:**

1. Fork the repository
2. Create a branch: `role/your-role-name`
3. Create `roles/your-role-name.yaml` following `schema/role.schema.yaml`
4. Add an entry to `registry.yaml` under `roles:`
5. Submit a pull request

Roles must reference only skills that already exist in the library
or are submitted in the same PR.

## Option C — List an Extension Repository

If you have domain-specific skills that are too narrow for the core
library (organization-specific, highly specialized, or experimental),
maintain them in your own repository and list it in `contrib/`.

**Your extension repo needs:**
- A `constraint-kit.yaml` manifest at the root
- Skills, roles, or bundles following the constraint-kit schema
- A README explaining what it covers and who it is for

**To list it:**

1. Fork constraint-kit
2. Add an entry to `contrib/extensions.yaml`:

```yaml

- id: your-extension-id
  name: Your Extension Name
  repo: https://github.com/you/your-extension
  manifest: constraint-kit.yaml
  description: One sentence on what this covers.
  personas: [engineer]   # who it is for
  tags: [your, tags]
  author: your-handle
  added: "YYYY-MM-DD"
  verified: false

```

1. Submit a pull request

Listing is reviewed for schema compliance and basic sanity only.
Content quality is your responsibility.

## Review criteria

All PRs are reviewed for:
- Schema compliance (`schema_version` field matches, required fields present)
- Scope — skills are single-concern, roles do not duplicate existing roles
- Anti-patterns section present and specific
- Transition section present (for skills)
- No organization-specific content in core skills or roles
  (put org-specific content in an extension instead)

PRs are not reviewed for:
- Content correctness in specialized domains (reviewers are generalists)
- Writing style beyond basic clarity

## Questions

Open an issue with the `question` label.
For discussions about direction or new categories, use `discussion`.
