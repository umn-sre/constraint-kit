---
name: upgrading-constraint-kit-layout
description: Use when a repo still has the legacy constraint-kit layout (.constraint-kit/PROJECT.md, GLOSSARY.md, ARCHAEOLOGY.md, plans/, specs/, adr/, agent*.yaml, or root-level SESSION_PLAN.md/ARCHAEOLOGY_NOTES.md) and needs migrating to the current docs/ layout - scans the repo, silently moves unambiguous files, and asks one at a time about destination conflicts, agent*.yaml disposition, and stray items, then reports a final summary. Also invoked passively by project-intake and project-archaeology when they detect legacy markers. Don't use on a repo already on the current docs/ layout, and don't use to author or edit the content of PROJECT.md/GLOSSARY.md/ARCHAEOLOGY.md themselves.
---

# Upgrading Constraint-Kit Layout

One-time-per-repo structural migration from the legacy
`.constraint-kit/` layout to the current `docs/` layout, so that
`project-intake`, `project-archaeology`, and every other constraint-kit
skill finds project context where they now expect it.

**Announce at start:** "I'm using the upgrading-constraint-kit-layout
skill to migrate this repo's layout."
