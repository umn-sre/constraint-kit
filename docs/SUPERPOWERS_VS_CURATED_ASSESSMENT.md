# Superpowers vs. curated constraint-kit skills: where each fits

The team has shifted toward using Superpowers directly through the
`anothel.superpowers-copilot-agents` VS Code extension rather than
exclusively through constraint-kit's curated skill library. This is
an honest look at where that's the right call and where curated
constraint-kit skills still earn their keep — not a case for one
replacing the other.

## Why "just use superpowers skills directly" doesn't fully work

The short version: constraint-kit and superpowers are two different
delivery mechanisms, not two competing skill libraries with
overlapping content. A raw superpowers skill doesn't drop into
constraint-kit's pipeline unmodified.

1. **Different activation models.** Superpowers skills are discovered
   *at runtime* by a live harness component watching a skills
   directory. constraint-kit has no such component — `render.py` is a
   one-shot compile step producing static text. A raw superpowers
   `SKILL.md` dropped into `skills/` isn't "discovered" by anything;
   it's invisible until it's wired into a role's skill lists and
   passes `validate.py`. That wiring *is* the adaptation work, not
   overhead on top of it.
2. **Different schema.** Superpowers uses one file with YAML
   frontmatter. constraint-kit splits `meta.yaml` (role/mode/persona
   targeting) from `SKILL.md` (the Purpose/Anti-Patterns/Transition
   structure `validate.py` enforces). Content copied over as-is fails
   validation on shape, independent of whether the guidance itself is
   good.
3. **Dangling cross-references.** Superpowers skills reference other
   superpowers skills by id, assume its subagent dispatch model and
   bootstrap hooks — none of which exist in constraint-kit. Copied
   verbatim, those references point at nothing.
4. **Trust and drift.** Superpowers skills auto-update on session
   start from a live upstream repo. Anthropic's own Agent Skills
   guidance is explicit that skills should be audited before trusting
   them, since a skill can direct an agent well beyond its stated
   purpose. For a team handling Vault credentials and production
   infrastructure, pointing directly at an auto-updating upstream
   means session constraints can change without review. Adapting a
   pinned, reviewed snapshot — tracked via the `provenance` block
   already in `test-driven-development` and `systematic-debugging` —
   is a deliberate control, not paperwork for its own sake.
5. **No role/mode targeting.** Superpowers doesn't know about
   `engineer`/`researcher`/`writer`/`product-owner` personas or
   distinguish `reasoning` from `generating-code`. That targeting,
   and the required-vs-recommended distinction with human confirmation
   on the latter, is curation work upstream doesn't do.

## Where direct Superpowers use is the right call

- **Generic development workflow**, not tied to org-specific policy:
  brainstorming structure, plan-writing format, subagent dispatch
  patterns, general debugging technique. These don't need
  constraint-kit's per-role targeting or Vault-specific compliance
  rules — they're useful as-is, and superpowers actively maintains
  and improves them.
- **Individual, fast-moving coding sessions** in VS Code where the
  overhead of a render step doesn't pay for itself — a quick script,
  a one-off fix, exploratory work with no compliance surface.
- **Staying current with upstream improvements** without waiting for
  someone to notice and re-adapt. Superpowers auto-updates; a
  constraint-kit adaptation is a snapshot that goes stale until
  someone deliberately re-syncs it.

## Where curated constraint-kit skills still add value

- **Org-specific compliance content that doesn't exist upstream at
  all** — `security-compliance`'s Vault-first retrieval and KV v2
  scoping conventions, or anything tied to UMN OIT's actual
  infrastructure. No external framework can provide this; it has to
  be curated in-house regardless of what else is adopted directly.
- **Non-engineer roles and the Drive path.** Superpowers is a coding-
  agent framework — `researcher`, `writer`, and `product-owner`
  personas, and anyone using the no-code Drive path with Gemini or
  Claude, aren't served by a VS Code extension at all.
- **CI-enforced validation.** `validate.py` runs in
  `.github/workflows/validate.yml` on every push touching
  `skills/`, `schema/`, `bundles/`, or `registry.yaml` — a gate
  superpowers content sitting outside constraint-kit doesn't pass
  through.
- **Cross-session continuity via `session_history`** and the
  `token-budget` skill's checkpointing guidance — specific to
  constraint-kit's re-injection model, since superpowers' runtime-
  discovery approach doesn't have an equivalent "static handoff note
  between sessions" concept in the same form.
- **The required/recommended distinction with human confirmation** —
  a deliberate fit for production SRE work, not present in
  superpowers' mandatory-trigger model (see the external skill
  ecosystem survey for the direct comparison).

## Recommendation

Not an either/or. The two serve different layers:

- Let Superpowers (via `superpowers-copilot-agents`) handle **generic
  development workflow** directly, in VS Code, where its runtime
  discovery and auto-updates are a genuine advantage over a static
  compile step.
- Keep curating constraint-kit skills for **anything org-specific,
  compliance-relevant, non-engineer, or Drive-path** — the content
  that either doesn't exist upstream or needs a validation gate and
  role targeting that upstream doesn't provide.
- When something in Superpowers is close to org-specific need (as
  `test-driven-development` and `systematic-debugging` already were),
  adapt it deliberately with a `provenance` block rather than either
  reinventing it from scratch or pointing straight at the live
  upstream.

In short: Superpowers directly for the general case, constraint-kit
for the parts that are actually specific to this team.
