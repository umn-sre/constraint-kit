# Skill: Incident Causal Synthesis

## Purpose

Constrain post-mortem synthesis to provided incident evidence.
Eliminate inference from general IT or domain knowledge. Make every
gap in the causal chain explicit before the report is written.
Derive the on-call playbook strictly from confirmed report findings.

## When This Skill Is Active

Any session producing a post-mortem report, incident analysis, or
derived on-call playbook where the AI must not go beyond the supplied
timeline, logs, observations, and cited references. Use when the
output will be used for blameless post-mortem review, audit, or
operational documentation where factual accuracy is critical.

## Agent Behavior

- Before constructing the causal chain, produce an explicit epistemic
  inventory: confirmed facts with their evidence sources, open
  questions flagged in the inputs, and sources marked unavailable.
- Assert only what is supported by provided timeline entries, log
  excerpts, DNS or system output, or cited references marked
  available. Do not draw on general IT, networking, or security
  knowledge to fill causal gaps.
- Construct the causal chain step by step, citing the evidence
  source at each link. Flag every link that lacks direct evidence.
- Ask the user to resolve each flagged gap — by providing evidence,
  confirming as an engineer assessment, or scoping the link out —
  before proceeding to the report phase.
- Produce the incident report in two tiers: executive summary
  (plain language, impact and actions) and technical detail (full
  causal chain with citations, evidence table, action items with
  owners and acceptance criteria).
- Derive the on-call playbook strictly from Phase 3 findings.
  Every detection signal, triage step, escalation threshold, and
  recovery check must trace to a named finding. Include no
  generic best-practice content not grounded in the incident.
- Note which action items, when deployed, will make manual
  playbook steps obsolete.

## Anti-Patterns

- Asserting a root cause not supported by provided evidence.
- Using general IT or domain knowledge to bridge a gap in the
  causal chain.
- Proceeding to the report phase with an unresolved causal link
  that affects the central finding.
- Writing playbook steps not traceable to a specific named finding
  from the technical report.
- Conflating a SERVFAIL with a CAA policy conflict, a reachability
  failure with a DNSSEC misconfiguration, or any other pair of
  superficially similar but distinct failure modes without evidence.
- Presenting an engineer's hypothesis as a confirmed finding.

## Transition

Phase 2 (causal analysis) must not proceed to Phase 3 (report)
until the user has explicitly confirmed or scoped out every flagged
gap in the causal chain. Phase 3 must be complete — both audience
tiers written — before Phase 4 (playbook) begins. The playbook
must not introduce steps that cannot be traced to a Phase 3 finding.
