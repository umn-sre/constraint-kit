# Changelog

All notable changes to constraint-kit are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.1] — 2026-03-31

### Added

- skills/incident-causal-synthesis
- skills/source-constrained-synthesis
- skills/vibe-coding-discipline

## [0.1.0] — 2026-03-13

### Added

- Schema definitions for skill, role, bundle, agent (repo path), and
  active-task template (Drive path)
- 9 seed skills: brainstorming, requirements-gathering, document-structure,
  argument-construction, plain-language, decision-records, research-brief,
  test-driven-development (adapted from obra/superpowers),
  systematic-debugging (adapted from obra/superpowers)
- 4 seed roles: engineer, researcher, writer, product-owner
- 5 seed bundles: new-feature-design, document-drafting, research-inquiry,
  engineering-decision, structured-output
- Master registry (registry.yaml) — human and machine readable
- Bootstrap renderer (render.py) with Jinja2 templates for:
  session-prompt, copilot-instructions, active-task
- Bootstrap templates for repo path (agent.yaml) and Drive path
- Schema validator (validate.py) with CI integration
- GitHub repo scaffolding: LICENSE, .gitignore, PR template,
  issue templates, CI workflow
- contrib/ extension listing structure
- Documentation: README, HOW_TO_USE_GITHUB, HOW_TO_USE_DRIVE,
  HOW_TO_CONTRIBUTE
