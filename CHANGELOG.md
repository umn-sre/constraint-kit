# Changelog

All notable changes to constraint-kit are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions follow [Semantic Versioning](https://semver.org/).

## [2.0.0] - 2026-08-04

Complete restructure: constraint-kit is now a GitHub Copilot / Claude
Code **plugin marketplace**. See [docs/DESIGN.md](docs/DESIGN.md).

### Added

- `.claude-plugin/marketplace.json` marketplace manifest.
- `constraint-design` plugin (planner agent + `project-intake`,
  `project-archaeology`, `codegraph-setup`, `brainstorming`,
  `writing-specs`, `writing-plans` skills).
- `project-archaeology` skill: the pre-2.0 `session-archaeology`
  skill modernized — same
  provenance modes, confidence tags, and discovery passes, now writing
  `docs/ARCHAEOLOGY.md` and finishing with the same
  PROJECT.md / GLOSSARY.md / copilot-instructions outputs as
  `project-intake`, so new and existing projects onboard to an
  identical workspace.
- CodeGraph integration: all agents use
  [colbymchenry/codegraph](https://github.com/colbymchenry/codegraph)
  for structural code discovery; the `codegraph-setup` skill covers
  install, agent wiring, per-project indexing, and the manual GitHub
  Copilot MCP configuration from
  [codegraph#718](https://github.com/colbymchenry/codegraph/pull/718)
  (CodeGraph lacks native Copilot support).
- `constraint-dev` plugin (conductor/implementer/reviewer agents +
  `test-driven-development`, `subagent-driven-development`,
  `executing-plans`, `session-ledger`, `security-principles`,
  `requesting-code-review`, `receiving-code-review`,
  `finishing-a-development-branch` skills).
- `security-principles` skill: the pre-2.0 `security-compliance`
  secrets-handling skill, renamed and merged with the core principles of
  [davila7/claude-code-templates](https://github.com/davila7/claude-code-templates)'
  security-compliance skill — secrets discipline stays the enforceable
  core, joined by security-by-design principles, dev-facing
  guardrails, and a risk-based finding-severity table. Enterprise GRC
  content excluded as not agent-actionable.
- `umn-compliance` plugin (compliance-analyst agent +
  `umn-security-compliance` skill): org-specific UMN bundle — maps a
  project against the 16 UMN Information Security Policy Standards and
  generates an evidence-based compliance document with a design-gap
  list and annual calendar. Kept as its own plugin so non-UMN
  consumers never install UMN policy; data classification and security
  level are stored in `docs/PROJECT.md` Constraints. The
  constraint-dev skill was renamed `security-compliance` →
  `security-principles` to keep per-task security discipline distinct
  from this compliance-analysis process.
- `session-ledger` skill: the pre-2.0 `session-hygiene` skill,
  renamed and re-homed — session
  ledger, edit verification, loop detection, budget watch, and the
  seven-step wrap-up unchanged in function; lessons-learned/budget
  session entries now append to a `## Session log` section of
  `docs/PROJECT.md` instead of `agent-base.yaml`.
- Skills adapted and merged from
  [obra/superpowers](https://github.com/obra/superpowers) and
  [mattpocock/skills](https://github.com/mattpocock/skills).
- `project-intake` skill generates `.github/copilot-instructions.md` in
  the target repo — replaces the bootstrap renderer.
- Project artifact convention: skills write PROJECT.md, GLOSSARY.md, and
  ARCHAEOLOGY.md into `docs/`; adr/, specs/, and plans/ into
  `docs/constraint-kit/`; and SDD scratch into `.constraint-kit/sdd/`.
- `scripts/validate.py` structure validation (stdlib only) and matching
  CI workflow.

### Removed

- `bootstrap/` rendering/validation/compliance pipeline.
- Custom YAML schemas (`schema/`), roles, bundles, registries, and
  `contrib/` extension registry.
- The original skill library (`skills/`), Drive/multisurface docs,
  scenario docs, and pipeline diagrams. All previous content remains
  available in git history (tag/commit prior to 2.0.0).

## [0.1.0] and earlier

The pre-2.0 skills/roles/bundles framework with Python bootstrap
rendering. See git history for details.
