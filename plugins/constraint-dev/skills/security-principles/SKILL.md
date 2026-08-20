---
name: security-principles
description: Use when code touches credentials, tokens, auth, or sensitive data, when a design needs security judgment, or when a review flags a possible security issue - enforces secrets-handling discipline (vault-first, least privilege, nothing leaks through logs or commits), applies core security principles from design through review, and classifies findings by real risk instead of reflex.
---

# Security Principles

Secrets that end up in source control, logs, or shell history don't get
un-leaked by rotating them later — the exposure already happened. This
skill enforces the handling discipline that prevents that class of
mistake before it ships, and carries a small set of security principles
through design, implementation, and review so security is a property of
the work, not an afterthought bolted on at the end.

**Announce at start:** "I'm using the security-principles skill."

## Core principles

Apply these as defaults in any design or implementation decision:

1. **Defense in depth** — never rely on a single control. Validation
   *and* parameterized queries; authn *and* authz; encryption *and*
   access scoping. If one layer fails, another should still hold.
2. **Zero trust** — verify every access explicitly; never trust a
   caller because of where the request came from. Assume breach when
   deciding what a component may reach.
3. **Least privilege** — the narrowest scope that satisfies the task:
   read-only where read-only suffices, one service's path instead of a
   shared catch-all, short-lived tokens over long-lived keys.
4. **Security by design** — raise security requirements during
   `brainstorming` and `writing-plans`, not after implementation. A
   design doc for anything touching auth, personal data, or money gets
   a short threat sketch: what's the asset, who'd attack it, where are
   the trust boundaries.
5. **Secure defaults, fail closed** — the out-of-the-box configuration
   is the safe one; on error, deny.
6. **Risk-based, not reflex-based** — prioritize by likelihood × impact
   (see Classifying findings), so critical issues get urgency and minor
   ones don't cry wolf.
7. **Compliance as floor, not ceiling** — meeting a framework is the
   baseline, not the goal; and conversely, "the framework doesn't
   require it" never justifies skipping an obvious control.

## Secrets discipline

The non-negotiable core, active any time code reads, writes, passes,
or logs anything that grants access to a system.

**Retrieval — secrets-manager-first, no exceptions**

- Credentials come from the secrets manager (Vault, AWS Secrets
  Manager, Azure Key Vault, …) at runtime — never hardcoded as
  literals, never committed as `.env` files with real values, never
  pasted into a checked-in config.
- No secrets manager in this environment (e.g. local dev)? Use a
  documented local-only mechanism — an untracked `.env.local` covered
  by `.gitignore`, or an explicit placeholder — and say so out loud.
  Never silently hardcode a real value "just for now"; "just for now"
  is how secrets end up in git history.
- Prefer OIDC/OAuth short-lived tokens over long-lived static
  credentials wherever the target supports them. A token that expires
  in an hour is a smaller blast radius than a key that's valid until
  someone remembers to rotate it.

**Scoping**

- Request the narrowest permission that satisfies the task; follow the
  project's established secrets-path conventions rather than
  improvising a new pattern for one task's convenience.
- If a task seems to need broader access than expected, flag it
  explicitly before proceeding — that's a design smell worth a second
  look, not a silent workaround.

**Logging and errors — nothing sensitive reaches output**

- Never log a credential, token, or secret value — not at debug level,
  not truncated to "just the first few characters." Log that an auth
  step happened and whether it succeeded, not what was used to do it.
- Exception messages and stack traces get the same treatment: a
  connection string in a traceback is a leak even if nobody meant to
  print it.
- Test fixtures and examples use obviously-fake values
  (`example-token-not-real`, `test@example.com`) — never a real
  credential (even expired), never a real value with two characters
  changed.

**Before committing**

- Scan the diff for anything that looks like a credential: API keys,
  private key blocks, bearer tokens, connection strings with embedded
  passwords. If it looks like a secret and you're not sure, treat it
  as one until proven otherwise.

## Implementation guardrails

Beyond secrets, when the task touches these areas, the defaults are:

- **Input** — validate and parameterize at every trust boundary
  (queries, shell commands, templates, deserialization); OWASP Top 10
  is the checklist for anything web-facing.
- **Data** — encrypt in transit (TLS) always; encrypt at rest and
  minimize collection when data is personal, health, or payment
  related. Know which fields are sensitive before writing the schema.
- **Dependencies** — new dependencies get a maintenance/vulnerability
  sanity check; keep scanning (SCA/SAST) wired into CI when the
  project has it, and flag when it doesn't but should.
- **Auth** — authenticate then authorize on every path, including
  "internal" ones; no shared accounts; MFA and SSO assumptions belong
  in the design, not retrofitted.

These are guardrails, not a substitute for a security review of
genuinely security-critical code — say so when the task warrants a
human specialist.

## Classifying findings

When you find or suspect a security issue, classify it before reacting
— severity drives response, and inflation erodes trust:

| Severity | Meaning | Response |
|---|---|---|
| Critical | Exploitable now: exposed secret, injection on a live path, authz bypass | Stop the task; fix or escalate immediately. An already-committed secret is compromised — rotation, not deletion, is the fix |
| High | Exploitable under realistic conditions, or sensitive data at material risk | Fix within the current task before proceeding |
| Medium | Weakness needing specific circumstances; hardening gap | Log it in the plan or ledger; fix in a scheduled task |
| Low | Defense-in-depth improvement, style-level | Note it; don't derail the task |

Judge likelihood × impact in the *project's* context — an internal
tool and an internet-facing service with payment data are different
worlds. The project's compliance obligations (GDPR, HIPAA, PCI-DSS,
SOC2, …) belong in `docs/PROJECT.md` Constraints — recorded
at intake or the moment they're discovered — and raise the impact of
anything touching regulated data.

## Red flags

- A credential hardcoded "temporarily" with a `# TODO: move to Vault`
- Logging any part of a secret at any log level
- Requesting broader scope because one token is easier than two
- Committing a `.env` with real values, even to a private repo
- A real credential in a test fixture or doc example
- Silent fallback to a hardcoded value when the secrets manager is down
- Deleting a committed secret from the tip and calling it handled —
  it's in history; rotate it
- Treating every finding as critical — or dismissing one because
  "it's just an internal tool" without checking what it can reach
- Skipping a control because the compliance framework doesn't
  explicitly require it

## Transitions

- Security-relevant design decisions with non-obvious tradeoffs →
  record an ADR per the `brainstorming` skill's criteria (both skills'
  home plugins apply: brainstorming is in constraint-design).
- Surrounding code not written yet → `test-driven-development`; write
  the abuse-case tests (bad input, missing auth, expired token) at the
  same seams as the happy-path tests.
- Findings during review → report through the `requesting-code-review`
  / reviewer flow with the severity classification above.
