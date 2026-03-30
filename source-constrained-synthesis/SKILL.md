# Skill: Source-Constrained Synthesis

## Purpose

Constrain AI synthesis to only provided notes and sources. Enforce
epistemic closure so the AI never fills factual gaps from training
knowledge. Make every gap explicit before writing begins.

## When This Skill Is Active

Any session producing a paper, brief, or report where the output
must be derived exclusively from materials the user has provided —
notes, source documents, or citations marked as available. Use when
citation traceability is required or when the user has flagged that
the AI must not extrapolate beyond provided materials.

## Agent Behavior

- Before outlining, produce an explicit epistemic inventory: list
  confirmed facts, available sources, and claims flagged as uncertain
  or unsourced in the provided notes.
- Assert only what appears in the provided notes or in a source
  marked `available: true`. For sources marked `available: false`,
  cite the reference only for facts also stated in the notes.
- Flag every unsourced or uncertain claim identified in the notes.
  Do not present them as established facts.
- For each section of the proposed outline, list the facts and
  sources that support it. Flag every section lacking sufficient
  cited material before proceeding.
- Ask the user to resolve each gap — by providing material, accepting
  a caveat, or scoping the section out — before writing begins.
- When a contested figure or self-reported statistic is cited, note
  the limitation explicitly in the text.
- Label author conclusions as such and distinguish them from cited
  findings.

## Anti-Patterns

- Asserting a fact not present in the provided notes or an available
  source.
- Using training knowledge to fill a gap rather than flagging it.
- Proceeding to the writing phase with unresolved gaps that affect
  the central argument.
- Citing a reference but asserting facts not stated in the provided
  text of that reference.
- Using "it is generally understood that..." or equivalent phrases
  to introduce unsourced claims.
- Stringing together multiple unsourced assertions to build a
  plausible-sounding argument.

## Transition

Do not begin the outline until the epistemic inventory is complete
and the user has acknowledged it. Do not begin writing until every
gap flagged in the outline phase is resolved or explicitly scoped
out by the user.
