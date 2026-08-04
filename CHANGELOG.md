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
  `brainstorming`, `writing-specs`, `writing-plans` skills).
- `constraint-dev` plugin (conductor/implementer/reviewer agents +
  `test-driven-development`, `subagent-driven-development`,
  `executing-plans`, `requesting-code-review`, `receiving-code-review`,
  `finishing-a-development-branch` skills).
- Skills adapted and merged from
  [obra/superpowers](https://github.com/obra/superpowers) and
  [mattpocock/skills](https://github.com/mattpocock/skills).
- `project-intake` skill generates `.github/copilot-instructions.md` in
  the target repo — replaces the bootstrap renderer.
- `.constraint-kit/` workspace convention: skills write PROJECT.md,
  GLOSSARY.md, adr/, specs/, plans/, and sdd/ into the consuming repo.
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
