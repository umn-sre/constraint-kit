## What does this PR add or change?

<!-- One paragraph. Be specific about what is new, changed, or fixed. -->


## Type of change

- [ ] New skill
- [ ] New role
- [ ] New bundle
- [ ] Extension listing (contrib/)
- [ ] Schema change
- [ ] Bug fix (renderer, validator, or tooling)
- [ ] Documentation only
- [ ] Other — describe:


## Checklist

### For new skills
- [ ] `skills/<id>/SKILL.md` exists and follows the structure:
      Purpose / When This Skill Is Active / Agent Behavior / Anti-Patterns / Transition
- [ ] `skills/<id>/meta.yaml` exists with all required fields
- [ ] `registry.yaml` updated with a new entry under `skills:`
- [ ] If adapted from an external source: `provenance` block included in `meta.yaml`
- [ ] Skill is not organization-specific (org-specific content belongs in an extension)

### For new roles
- [ ] `roles/<id>.yaml` exists and follows `schema/role.schema.yaml`
- [ ] All referenced skill ids exist in the library
- [ ] `registry.yaml` updated with a new entry under `roles:`
- [ ] `onboarding_note` is written in plain English, no jargon
- [ ] Role does not duplicate an existing role

### For new bundles
- [ ] `bundles/<id>.yaml` exists and follows `schema/bundle.schema.yaml`
- [ ] All referenced skill ids exist in the library
- [ ] `registry.yaml` updated with a new entry under `bundles:`

### For extension listings
- [ ] Entry added to `contrib/extensions.yaml`
- [ ] Linked repo has a valid `constraint-kit.yaml` manifest
- [ ] `verified: false` (reviewer will set to true after schema check)

### For schema changes
- [ ] Existing skills/roles/bundles still validate against the updated schema
- [ ] Schema version bumped if the change is breaking
- [ ] CHANGELOG updated

### All PRs
- [ ] `schema_version` field is present and correct in all new/modified files
- [ ] No organization-specific content in core library files
- [ ] CI validation passes (schema-validate workflow)


## Testing

<!-- How did you verify this works? Paste a sample render output
     if this adds a skill or role. -->


## Related issues

<!-- Closes #N -->
