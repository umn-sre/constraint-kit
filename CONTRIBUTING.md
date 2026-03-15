# Contributing to constraint-kit

Thanks for your interest in contributing.

Full contribution guidelines are in [`docs/HOW_TO_CONTRIBUTE.md`](docs/HOW_TO_CONTRIBUTE.md).

## Quick summary

- **New skill** — add `skills/<id>/SKILL.md` + `meta.yaml`, update `registry.yaml`, submit a PR
- **New role** — add `roles/<id>.yaml`, update `registry.yaml`, submit a PR
- **New bundle** — add `bundles/<id>.yaml`, update `registry.yaml`, submit a PR
- **Extension listing** — add an entry to `contrib/extensions.yaml`, submit a PR

Before submitting, run the validator locally:

```bash

pip install pyyaml
python bootstrap/validate.py

```

All PRs require a clean validator run. CI enforces this automatically.

See [`docs/HOW_TO_CONTRIBUTE.md`](docs/HOW_TO_CONTRIBUTE.md) for full
criteria, templates, and the review process.
