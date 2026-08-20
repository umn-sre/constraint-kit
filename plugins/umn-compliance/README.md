# umn-compliance

University of Minnesota compliance bundle for GitHub Copilot (CLI,
VS Code, coding agent) and Claude Code.

**Org-specific.** Unlike `constraint-design` and `constraint-dev`,
this plugin encodes University of Minnesota policy — install it only
for UMN projects. It is also a home for future compliance skills
(data-classification helpers, vendor assessment, pre-deployment
checklists).

## Skills

| Skill | Purpose |
|---|---|
| `umn-security-compliance` | Initial or annual compliance analysis: maps the project against the 16 UMN Information Security Policy Standards and generates an evidence-based compliance document with a design-gap list and annual calendar |

Distinct from `security-principles` (constraint-dev): that skill is
per-task secure-coding discipline; this one is a periodic, project-wide
analysis process that produces a standalone document.

## Agents

- **compliance-analyst** — runs the analysis end to end; reads
  everything (including `.constraint-kit/` context and CodeGraph),
  writes only the compliance document and the classification lines in
  `.constraint-kit/PROJECT.md` Constraints, never source code. Hands
  design gaps to the **planner** agent (constraint-design) for
  spec/plan work.

## Integration with the other plugins

- Data classification and security level live in
  `.constraint-kit/PROJECT.md` Constraints — captured at intake or on
  first review, reused by every subsequent review.
- Project discovery starts from `project-intake` /
  `project-archaeology` output (PROJECT.md, ARCHAEOLOGY.md) and
  CodeGraph, so an onboarded project needs little re-reading.
- The "Design Changes Required" output feeds the `brainstorming` →
  `writing-specs` → `writing-plans` pipeline.

## Credits

`umn-security-compliance` originated as an internal UMN SRE skill.
Policy content belongs to the
[University of Minnesota Information Security Policy](https://policy.umn.edu/it/securedata).
