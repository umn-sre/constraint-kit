# constraint-kit

A model-agnostic, context-aware framework for keeping AI assistants
focused, consistent, and constraint-driven across sessions.

Works with Gemini, Claude, GitHub Copilot, ChatGPT, or any
browser-based AI assistant. No plugins, no API keys, no lock-in.

## The problem it solves

AI assistants drift. Give them rules at the start of a session and
by the middle of a long conversation they are ignoring them, inventing
conventions, or producing output that conflicts with your standards.

constraint-kit fixes this by keeping rules on disk — not in memory —
and re-injecting them at each task boundary. The AI looks things up
rather than relying on recall. Drift becomes structurally impossible
rather than a matter of luck.

## How it works

Every project has a small config file (`agent.yaml` for repos,
`active-task.md` for Drive users) that declares:

- **Role** — who the agent is (`engineer`, `researcher`, `writer`, `product-owner`)
- **Task** — what you are working on right now
- **Mode** — how the agent is operating (`reasoning`, `collaborating`, `generating`)

The bootstrap renderer reads this config, resolves the right skills
from the library, and produces a pasteable session starter. Paste it
at the start of every session. Done.

When you switch modes mid-session, paste a mode switch snippet.
When you start a new session, paste the starter again.
The AI never relies on memory — it always has the constraints in context.

## Who it is for

**Engineers** — writing code, infrastructure, or automation with
consistent conventions, TDD discipline, and documented decisions.

**Researchers** — scoping inquiries, structuring arguments, and
producing papers or briefs without unsupported claims or scope drift.

**Writers** — producing documents of any kind with consistent
structure, audience fit, and readability standards.

**Product owners** — defining features, stories, and acceptance
criteria with complete requirements and clear scope.

Non-technical users (Drive path): no GitHub or coding knowledge needed.

## Quick start

### Technical path (repo)

```bash

# Copy the bootstrap template into your project

mkdir -p .constraint-kit
cp path/to/constraint-kit/bootstrap/templates/new-project-repo.yaml \
   .constraint-kit/agent.yaml

# Fill in project, role, task, mode, target

# Then render

python path/to/constraint-kit/bootstrap/render.py .constraint-kit/agent.yaml

# Paste the output as your first message in Gemini, Claude, or Copilot

```

## Non-technical path (Drive)

1. Open the [constraint-kit shared Drive folder](#) ← link your shared folder here
2. Copy the session starter template for your role
3. Fill in your project, task, and context
4. Attach it to a new Gemini or Claude session

## What is in the library

### Roles

| Role | For |
|---|---|
| `engineer` | Software, infrastructure, automation |
| `researcher` | Inquiry, papers, literature reviews |
| `writer` | Documents, guides, content |
| `product-owner` | Features, stories, acceptance criteria |

### Skills

| Skill | Modes | Personas |
|---|---|---|
| `brainstorming` | collaborating, reasoning | any |
| `requirements-gathering` | collaborating, reasoning | any |
| `document-structure` | generating-doc, collaborating | any |
| `argument-construction` | generating-doc, reasoning | researcher, writer |
| `plain-language` | generating-doc | any |
| `decision-records` | generating-doc, generating-structured, reasoning | engineer, researcher, product-owner |
| `research-brief` | collaborating, generating-doc | researcher, writer |
| `test-driven-development` | generating-code | engineer |
| `systematic-debugging` | reasoning, generating-code | engineer |

### Bundles

| Bundle | Skills | For |
|---|---|---|
| `new-feature-design` | brainstorming, requirements-gathering, decision-records | engineer, product-owner |
| `document-drafting` | document-structure, argument-construction, plain-language | researcher, writer |
| `research-inquiry` | research-brief, brainstorming, argument-construction, document-structure | researcher |
| `engineering-decision` | brainstorming, requirements-gathering, decision-records | engineer |
| `structured-output` | requirements-gathering, document-structure, plain-language | product-owner, engineer |

## Community extensions

Domain-specific skills that are too narrow for the core library
live in community extension repositories. See `contrib/extensions.yaml`
and `contrib/README.md` for how to build and list an extension.

## Contributing

Skills, roles, and extension listings are all welcome.
See `docs/HOW_TO_CONTRIBUTE.md`.

## Philosophy

- **Rules on disk, not in memory** — re-injection beats retention
- **Atomic skills** — single-concern constraint documents, not grab-bags
- **Model-agnostic** — plain text works everywhere
- **Self-service** — no curator bottleneck on adoption
- **Honest provenance** — adapted external skills are tracked, not laundered

## License

MIT

## Acknowledgments

constraint-kit was directly inspired by **[obra/superpowers](https://github.com/obra/superpowers)**,
Jesse Tane's agentic skills framework for Claude Code. Superpowers demonstrated
that skills-as-files with mandatory agent consultation is a viable and powerful
pattern for keeping AI agents on-task across sessions.

Two skills in this library — `test-driven-development` and `systematic-debugging`
— are adapted from superpowers with full provenance tracked in their `meta.yaml`
files. The core philosophy of constraint-kit (rules on disk, not in memory;
re-injection beats retention) is a direct extension of what superpowers proved
works in practice.

If you are working with Claude Code specifically, superpowers is the better tool
for that context. constraint-kit is designed for the broader case: any AI surface,
any persona, any kind of knowledge work.
