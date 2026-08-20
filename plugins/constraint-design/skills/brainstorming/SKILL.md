---
name: brainstorming
description: Use before any creative work - creating features, building components, adding functionality, or modifying behavior. Grills the user one question at a time to turn an idea into an approved design, capturing glossary terms and decision records as they crystallise.
---

# Brainstorming Ideas Into Designs

Turn ideas into fully formed designs through a relentless, collaborative
interview — then get the design approved before anything is built.

<HARD-GATE>
Do NOT invoke any implementation skill, write any code, scaffold any
project, or take any implementation action until you have presented a
design and the user has approved it. This applies to EVERY project
regardless of perceived simplicity.
</HARD-GATE>

## Anti-Pattern: "This Is Too Simple To Need A Design"

Every project goes through this process. A todo list, a single-function
utility, a config change — all of them. "Simple" projects are where
unexamined assumptions cause the most wasted work. The design can be short
(a few sentences for truly simple projects), but you MUST present it and
get approval.

## Checklist

Create a todo per item and complete them in order:

1. **Explore project context** — read `.constraint-kit/PROJECT.md`,
   `.constraint-kit/GLOSSARY.md`, `.constraint-kit/ARCHAEOLOGY.md`, and
   `.constraint-kit/adr/` if they exist (run the `project-intake` skill —
   or `project-archaeology` for an undocumented existing codebase — first
   if the project has never been set up); check files, docs, recent
   commits, and answer structural code questions with CodeGraph
   (`codegraph_explore`) when it is available.
2. **Grill the user** — one question at a time until shared understanding
3. **Propose 2-3 approaches** — with trade-offs and your recommendation
4. **Present design** — in sections scaled to complexity, approval per section
5. **Write design doc** — save to `.constraint-kit/specs/YYYY-MM-DD-<topic>-design.md`
6. **Spec self-review** — placeholder/consistency/scope/ambiguity check
7. **User reviews written design** — ask before proceeding
8. **Transition** — invoke `writing-specs` (larger features) or
   `writing-plans` (small, well-understood changes) next

## Grilling the user

Interview relentlessly about every aspect until you reach shared
understanding. Walk down each branch of the decision tree, resolving
dependencies between decisions one by one.

- **One question per message.** Multiple questions at once are
  bewildering. If a topic needs more exploration, break it into multiple
  questions. Prefer multiple choice where possible; open-ended is fine too.
- **Provide your recommended answer with every question.**
- **Facts vs decisions.** If a *fact* can be found in the environment
  (filesystem, docs, code), look it up rather than asking. The *decisions*
  are the user's — put each one to them and wait.
- Focus on purpose, constraints, and success criteria.
- **Scope check first:** if the request describes multiple independent
  subsystems, flag it immediately and help decompose into sub-projects —
  each gets its own design → spec → plan cycle. Don't spend questions
  refining details of a project that needs decomposition first.

## Capture the domain model as you go

While grilling, actively maintain the project's language (in
`.constraint-kit/GLOSSARY.md`, creating it lazily on first term):

- **Challenge against the glossary.** "Your glossary defines
  'cancellation' as X, but you seem to mean Y — which is it?"
- **Sharpen fuzzy language.** "You're saying 'account' — do you mean the
  Customer or the User? Those are different things."
- **Stress-test with concrete scenarios.** Invent edge cases that force
  precision about the boundaries between concepts.
- **Cross-reference with code.** If the user states how something works
  and the code disagrees, surface the contradiction.
- **Update the glossary inline** the moment a term is resolved — don't
  batch. The glossary holds language only, never implementation details.
- **Offer decision records sparingly.** Write
  `.constraint-kit/adr/NNNN-<slug>.md` only when a decision is all three:
  hard to reverse, surprising without context, and the result of a real
  trade-off. Record context, decision, and consequences in a page or less.

## Exploring approaches

- Propose 2-3 different approaches with trade-offs
- Lead with your recommended option and explain why
- YAGNI ruthlessly — remove unnecessary features from every approach

## Presenting the design

- Scale each section to its complexity: a few sentences if
  straightforward, up to 200-300 words if nuanced
- Ask after each section whether it looks right so far
- Cover: architecture, components, data flow, error handling, testing

**Design for isolation and clarity:** break the system into units that
each have one clear purpose, communicate through well-defined interfaces,
and can be understood and tested independently. If you can't say what a
unit does without reading its internals, the boundaries need work. (The
`writing-plans` skill carries the full deep-module vocabulary.)

**In existing codebases:** explore current structure before proposing
changes; follow existing patterns; include targeted improvements only
where existing problems affect this work. No unrelated refactoring.

## After the design

Write the validated design to
`.constraint-kit/specs/YYYY-MM-DD-<topic>-design.md`, then self-review
with fresh eyes:

1. **Placeholder scan:** any "TBD", "TODO", vague requirements? Fix them.
2. **Internal consistency:** do sections contradict each other?
3. **Scope check:** focused enough for a single implementation plan?
4. **Ambiguity check:** could any requirement be read two ways? Pick one
   and make it explicit.

Fix issues inline, then ask the user to review the file:

> "Design written to `<path>`. Please review it and let me know if you
> want changes before we move on."

**Transition when approved:**

- Substantial feature, or others will implement it → invoke
  `writing-specs` to synthesize a full spec, then `writing-plans`.
- Small, fully-understood change → invoke `writing-plans` directly.

Do NOT invoke any other skill. Those are the only two next steps.
