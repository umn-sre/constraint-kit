# constraint-kit — GitHub Repository Setup Guide

Complete instructions for initializing the public constraint-kit
repository and configuring it for community contributions.

Two methods are shown throughout for GitHub operations:

- **Method A — gh CLI** (recommended): faster, scriptable, stays in the terminal
- **Method B — Web UI**: fallback if `gh` is not installed

## Step 0 — Install and authenticate gh (Method A only)

Skip if you prefer the web UI.

```bash

# macOS

brew install gh

# Linux — see https://github.com/cli/cli/blob/trunk/docs/install_linux.md

# Authenticate

gh auth login

# Prompts: GitHub.com → HTTPS → Login with a web browser

# Follow the one-time device code in your browser

```

Verify:

```bash

gh auth status

```

## Step 1 — Initialize the local repo

Run from the `constraint-kit/` directory:

```bash

cd constraint-kit/

git init
git checkout -b main

git add \
  .github/ \
  .gitignore \
  .markdownlintrc \
  CHANGELOG.md \
  CONTRIBUTING.md \
  LICENSE \
  README.md \
  bootstrap/ \
  bundles/ \
  contrib/ \
  docs/ \
  pyproject_mdcompliance_snippet.toml \
  registry.yaml \
  roles/ \
  schema/ \
  skills/

git status   # verify — should show only the files above

```

## Step 2 — First commit

```bash

git commit -m "feat: initial release of constraint-kit v0.1.0

Add schema, seed skills, roles, bundles, bootstrap renderer,
schema validator, GitHub scaffolding, and documentation.

Skills (11):
  brainstorming, requirements-gathering, document-structure,
  argument-construction, plain-language, decision-records,
  research-brief, markdown-compliance, python-compliance,
  test-driven-development (adapted obra/superpowers),
  systematic-debugging (adapted obra/superpowers)

Roles (4):
  engineer, researcher, writer, product-owner

Bundles (5):
  new-feature-design, document-drafting, research-inquiry,
  engineering-decision, structured-output

Bootstrap:
  render.py        — session-prompt, copilot-instructions, active-task
  render_drive.py  — self-contained Drive session starters
  validate.py      — schema validation with CI integration
  pycompliance.py  — Python compliance auto-fixer
  mdcompliance.py  — Markdown compliance auto-fixer
  batch_comply.py  — parallel Python compliance for directories

Closes #0"

```

## Step 3 — Create the GitHub repository

### Method A — gh CLI

```bash

gh repo create constraint-kit \
  --public \
  --description "A model-agnostic skills framework for keeping AI assistants focused and constraint-driven across sessions." \
  --source . \
  --remote origin \
  --push

```

This creates the repo, sets the remote, and pushes `main` in one command.
Skip Step 4 — the push is already done.

### Method B — Web UI

1. Go to <https://github.com/new>
2. Repository name: `constraint-kit`
3. Description: `A model-agnostic skills framework for keeping AI assistants focused and constraint-driven across sessions.`
4. Visibility: **Public**
5. Do NOT initialize with README, .gitignore, or license —
   these already exist locally
6. Click **Create repository**

## Step 4 — Push (Method B only)

Skip if you used Method A — the push was done in Step 3.

```bash

git remote add origin https://github.com/umn-sre/constraint-kit.git
git push -u origin main

```

## Step 5 — Create the v0.1.0 tag

```bash

git tag -a v0.1.0 -m "constraint-kit v0.1.0 — initial release"
git push origin v0.1.0

```

This creates the tag that the CI workflow, extension manifests, and
the private repo's submodule will reference.

## Step 6 — Private extension repo submodule

After the public repo is live, wire `ck-personal` to it:

```bash

cd ck-personal/
mkdir -p vendor
git submodule add \
  https://github.com/umn-sre/constraint-kit.git \
  vendor/constraint-kit

# Pin to v0.1.0

cd vendor/constraint-kit
git checkout v0.1.0
cd ../..

git add .gitmodules vendor/
git commit -m "chore: add constraint-kit v0.1.0 as submodule"

```

Anyone cloning `ck-personal` later runs:

```bash

git submodule update --init --recursive

```

## Step 7 — Repository settings

### Method A — gh CLI

Set merge strategy (squash only) and auto-delete branches:

```bash

gh repo edit constraint-kit \
  --enable-squash-merge \
  --disable-merge-commit \
  --disable-rebase-merge \
  --delete-branch-on-merge

```

Set topics:

```bash

gh repo edit constraint-kit \
  --add-topic ai-tools \
  --add-topic prompt-engineering \
  --add-topic llm \
  --add-topic constraints \
  --add-topic skills \
  --add-topic gemini \
  --add-topic github-copilot \
  --add-topic claude \
  --add-topic model-agnostic \
  --add-topic context-management

```

Branch protection for `main` (requires admin scope — re-auth if needed):

```bash

gh api repos/umn-sre/constraint-kit/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["validate"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
  --field restrictions=null

```

### Method B — Web UI

**General** — go to Settings → General:

- [ ] Allow merge commits: **disabled**
- [ ] Allow squash merging: **enabled** (default merge type)
- [ ] Allow rebase merging: **disabled**
- [ ] Automatically delete head branches: **enabled**

**Branch protection** — Settings → Branches → Add rule → `main`:

- [ ] Require a pull request before merging: **enabled**
  - Required approvals: **1**
  - Dismiss stale pull request approvals: **enabled**
- [ ] Require status checks to pass: **enabled**
  - Required check: `validate`
- [ ] Require branches to be up to date: **enabled**
- [ ] Do not allow bypassing the above settings: **enabled**
- [ ] Allow force pushes: **disabled**
- [ ] Allow deletions: **disabled**

**Tag protection** — Settings → Rules → New ruleset → Tags:

- Target: `v*`
- Restriction: Restrict deletions, Restrict force pushes

**Actions permissions** — Settings → Actions → General:

- Actions permissions: **Allow all actions and reusable workflows**
- Workflow permissions: **Read repository contents and packages**

**Topics** — repo main page → ⚙ gear next to About:

```

ai-tools  prompt-engineering  llm  constraints  skills
gemini  github-copilot  claude  model-agnostic  context-management

```

**About description:**

```

A model-agnostic skills framework for keeping AI assistants focused
and constraint-driven across sessions. Works with Gemini, Claude,
Copilot, and any browser-based AI.

```

## Step 8 — Create a GitHub Release

### Method A — gh CLI

```bash

gh release create v0.1.0 \
  --title "constraint-kit v0.1.0 — Initial Release" \
  --notes "## constraint-kit v0.1.0

First public release of the constraint-kit skills framework.

### What's included

**11 skills** — brainstorming, requirements-gathering, document-structure,
argument-construction, plain-language, decision-records, research-brief,
markdown-compliance, python-compliance,
test-driven-development, systematic-debugging

**4 roles** — engineer, researcher, writer, product-owner

**5 bundles** — new-feature-design, document-drafting, research-inquiry,
engineering-decision, structured-output

**Bootstrap renderer** — produces session starters for Gemini, Claude,
Copilot, and Drive users from a simple project config file

**Compliance tooling** — pycompliance.py and mdcompliance.py for
automated Python and Markdown quality enforcement

**Schema validator** — validates all skills, roles, and bundles with
CI integration

### Quick start

See [README.md](README.md) for usage instructions.
Technical path: [docs/HOW_TO_USE_GITHUB.md](docs/HOW_TO_USE_GITHUB.md)
Non-technical path: [docs/HOW_TO_USE_DRIVE.md](docs/HOW_TO_USE_DRIVE.md)
Contributing: [docs/HOW_TO_CONTRIBUTE.md](docs/HOW_TO_CONTRIBUTE.md)" \
  --latest

```

### Method B — Web UI

1. Go to Releases → Draft a new release
2. Tag: `v0.1.0`
3. Title: `constraint-kit v0.1.0 — Initial Release`
4. Body — paste the release notes from Method A above
5. Set as latest release: **enabled**
6. Click **Publish release**

## Step 9 — Private repo init

### Method A — gh CLI

```bash

cd ck-personal/
git init
git checkout -b main

# After Step 6 above (submodule wired), stage everything

git add .
git commit -m "feat: initial ck-personal extension repo

Private constraint-kit extension with SRE / infrastructure skills.

Skills: sre-conventions, vault-secrets, github-actions-patterns,
        python-runbooks, azure-automation
Role:   sre-engineer
Bundles: runbook-development, infrastructure-decision
Project: ssl-cert-pipeline (active)"

gh repo create ck-personal \
  --private \
  --description "Personal constraint-kit extension — SRE and infrastructure skills" \
  --source . \
  --remote origin \
  --push

```

## Method B — Web UI

```bash

cd ck-personal/
git init
git checkout -b main

git add .
git commit -m "feat: initial ck-personal extension repo

Private constraint-kit extension with SRE / infrastructure skills.

Skills: sre-conventions, vault-secrets, github-actions-patterns,
        python-runbooks, azure-automation
Role:   sre-engineer
Bundles: runbook-development, infrastructure-decision
Project: ssl-cert-pipeline (active)"

```

Then create a **Private** repo at <https://github.com/new>, name it
`ck-personal`, and push:

```bash

git remote add origin https://github.com/umn-sre/ck-personal.git
git push -u origin main

```

## Post-setup checklist

- [ ] `constraint-kit` repo is public on GitHub
- [ ] CI passes on `main` (validate workflow green)
- [ ] `v0.1.0` tag exists and has a Release
- [ ] Branch protection on `main` is active
- [ ] Topics are set for discoverability
- [ ] `ck-personal` is private, submodule pinned to `v0.1.0`
- [ ] `ck-personal` CI passes (if you add a validate workflow there)
- [ ] Drive session starters uploaded to shared folder
- [ ] Shared folder link added to `constraint-kit` README
