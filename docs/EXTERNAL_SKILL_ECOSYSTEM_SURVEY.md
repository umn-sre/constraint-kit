# External skill ecosystem survey

Scope: how does constraint-kit's skill model compare to what's
happening outside it, and what's actually worth adapting in. This is
not a call to rebuild constraint-kit around someone else's
architecture — it's a comparison to identify specific, adoptable
patterns, the same way `test-driven-development` and
`systematic-debugging` were already adapted from `obra/superpowers`
(see their `provenance` blocks in `skills/*/meta.yaml`).

Reviewed July 2026. Three frameworks, chosen because they represent
three different points on the spectrum: a single opinionated
open-source project, an emerging cross-vendor open standard, and the
IDE-native convention layer your team is already using directly.

## 1. obra/superpowers

The framework constraint-kit already partially derives from. Also an
"agentic skills framework & software development methodology,"
distributed as a plugin across Claude Code, Copilot CLI, Cursor,
Codex, and others — including via the `anothel.superpowers-copilot-agents`
VS Code extension your team has been using directly.

**How it differs structurally:** skills are *discovered and loaded by
the agent at runtime* — the agent reads a skill's name and
description, decides it's relevant mid-conversation, and loads the
full `SKILL.md` itself. There's no separate compile step; nothing is
pre-rendered into a session starter the way `render.py` does it.
Recent versions (v2.0) also separated the skills content into its own
repo (`obra/superpowers-skills`) from the plugin mechanism that loads
them, and skills auto-update on session start.

**What's worth adapting:**

- **Description-writing discipline.** Superpowers' own
  `writing-skills` skill states a hard rule, backed by their own
  testing: a skill's `description` field should describe *only the
  triggering condition* ("use when X"), never summarize what the
  skill does. They found that when a description also summarizes the
  workflow, agents sometimes follow the shortened description instead
  of reading the full skill — in their example, a description
  mentioning "one review" caused an agent to skip a second review step
  that the full skill clearly required. Several constraint-kit skill
  descriptions (including the two just added,
  `security-compliance` and `token-budget`) currently describe *what
  the skill does* rather than *when to trigger it*. Worth a pass
  across the library — not urgent, but a real, tested finding, not a
  style preference.
- **Content/mechanism separation.** Superpowers splitting skill
  content from the loading mechanism so each can version
  independently is a pattern constraint-kit already has a version of,
  via the `extension:` field (external skill manifests resolved
  separately from the core library) — worth knowing this validates
  that direction rather than treating it as a gap.

**What's deliberately not being adopted:** superpowers' skills are
often phrased as non-negotiable ("YOU MUST USE IT... this is not
negotiable"). constraint-kit's `recommended` tier explicitly asks the
agent to confirm with the user before applying — see the "Ask the
user to confirm before applying a recommended skill" line in
`session-prompt.j2`'s rendered output. That's a deliberate difference
in philosophy, not an oversight, and it's worth keeping for
environments (like production SRE work) where a human checkpoint on
recommended-but-not-required behavior matters. Flagging it here so
it's a documented decision rather than something that looks
unfinished next to superpowers' harder line.

## 2. Agent Skills open standard (agentskills.io / anthropics/skills)

Originally Anthropic's own skill format for Claude, now published as
an open, cross-vendor standard adopted by Claude Code, Codex CLI,
Gemini CLI, GitHub Copilot, and Cursor. The core unit is the same
name — a `SKILL.md` file — but the format is a single file with YAML
frontmatter (`name`, `description`, plus optional fields) directly
followed by markdown instructions, rather than constraint-kit's
separate `meta.yaml` + `SKILL.md` pair.

**How it differs structurally:** "progressive disclosure" — the
agent's system prompt gets every installed skill's `name` and
`description` up front (cheap, small), and only loads the full
`SKILL.md` body into context when a task actually matches. Large
skills are told to split extra detail into `references/`, `scripts/`,
or `assets/` subdirectories so the core file stays lean. This is the
same instinct behind constraint-kit's atomic single-concern skills,
approached from the opposite direction — Agent Skills keeps one file
lean by deferring content, constraint-kit keeps things lean by
keeping each skill narrow to begin with.

**What's worth adapting:**

- **The `references/`/`scripts/`/`assets/` subfolder convention** for
  any constraint-kit skill that grows past what fits comfortably in
  one `SKILL.md`. None currently need it, but it's a ready-made
  pattern instead of improvising one when the first skill does.
- **Naming convention discipline**: verb-ing + noun pattern
  (`analyzing-marketing-campaign`), lowercase-and-hyphens, under 64
  characters for the name and under 1,024 for the description. Close
  to what constraint-kit already does, worth confirming the schema
  validator enforces the length ceilings explicitly rather than
  implicitly.
- **Portability angle**: because the standard is now supported across
  Claude Code, Copilot, Cursor, and others, a constraint-kit skill
  that also shipped as a standards-compliant `SKILL.md` (frontmatter
  version) could theoretically be dropped into any of those tools
  directly. This is a bigger architectural question than a quick
  adoption — flagging it as a real option for a future story, not
  something to fold into this one.

## 3. GitHub Copilot / Cursor native conventions

The layer your team is already using directly, via
`.github/copilot-instructions.md`, `.github/prompts/`, and
`.cursorrules`-style files — not third-party frameworks, but the
IDE/tool vendors' own built-in customization mechanisms. Worth
surveying because this is genuinely what "using Superpowers directly"
resolves to underneath: the `superpowers-copilot-agents` extension
converts superpowers' skills into native Copilot agents that live in
this same layer.

**How it differs structurally:** no separate compile or resolution
step at all — these are files the tool reads directly from a known
path in the repo. No role/mode/persona model, no required-vs-
recommended distinction, no registry. Whatever's in the file applies,
full stop, whenever the tool is active in that repo.

**What's worth adapting:** honestly, not much in the other direction —
this layer is *less* structured than constraint-kit, not more. Its
value is reach: it's already installed, requires no separate render
step, and is exactly where your team has been gravitating for
convenience. The comparison mainly clarifies *why* that gravitation
happens (zero-friction, no separate compile step) and what's traded
away by using it instead of constraint-kit's model (no
required/recommended distinction, no per-role tailoring, no
validation gate). That tradeoff is exactly the subject of the
Superpowers-vs-curated-skills assessment — see next.

## Summary table

| | constraint-kit | obra/superpowers | Agent Skills standard | Copilot/Cursor native |
|---|---|---|---|---|
| Skill file | `meta.yaml` + `SKILL.md` | `SKILL.md` w/ frontmatter | `SKILL.md` w/ frontmatter | `.github/copilot-instructions.md` etc. |
| Loading | Pre-compiled by `render.py`, injected up front | Agent discovers & loads at runtime | Agent discovers & loads at runtime (progressive disclosure) | Always active, no discovery step |
| Required vs. recommended | Yes, explicit, human confirms recommended | No — matching skills are mandatory | No such distinction | No such distinction |
| Per-role tailoring | Yes (role/mode/persona) | Partial (persona-agnostic skill set) | No | No |
| Validation gate | Yes (`validate.py`, CI-enforced) | Skill-behavior eval harness (`superpowers-evals`) | Schema-level only | None |
| Cross-tool portable | No (constraint-kit specific) | Partial (own plugin per tool) | Yes (by design) | No (per-tool) |

The takeaway: constraint-kit's structure (role/mode targeting,
required/recommended, CI-enforced validation) is more rigorous than
any of the three surveyed frameworks — that rigor is a deliberate fit
for an SRE/infra environment with production consequences, not
something to trade away for portability. The concrete, low-risk
adoptions from this survey are the description-writing discipline
from superpowers and the `references/` subfolder convention from the
Agent Skills standard — both additive, neither requires an
architecture change.
