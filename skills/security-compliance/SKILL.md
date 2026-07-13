# Skill: Security Compliance

## Purpose

Secrets that end up in source control, logs, or shell history don't
get un-leaked by rotating them later — the exposure already happened.
This skill enforces the handling discipline that prevents that class
of mistake before it ships: credentials come from a secrets manager,
never from a literal in code; access is scoped to what the task
needs, not broadened for convenience; and nothing that looks like a
credential ever reaches a log line, an error message, or a commit.

**Scope note:** this skill is about secrets and credential handling
specifically — not a general application-security skill. Injection
attacks, dependency vulnerabilities, auth/authz design, and other
appsec concerns are out of scope here and belong in their own skills
if the team wants to add them later. Keeping this atomic is
deliberate — see the constraint-kit philosophy on single-concern
skills.

## When This Skill Is Active

Any time code touches credentials, tokens, API keys, connection
strings, or anything else that grants access to a system — reading
them, writing them, passing them between processes, or logging
anything near them.

## Agent Behavior

**Retrieval — Vault-first, no exceptions**

- Credentials are read from the secrets manager (e.g. HashiCorp
  Vault) at runtime, never hardcoded as string literals, never
  committed as `.env` files with real values, never pasted into a
  config file that gets checked in.
- If a secrets manager isn't available in the current environment
  (e.g. local dev without Vault access), use a documented local-only
  mechanism — an untracked `.env.local` excluded via `.gitignore`, or
  an explicit placeholder the developer fills in — and say so out
  loud rather than silently hardcoding a real value "just for now."
  "Just for now" is how secrets end up in git history.
- Prefer OIDC/SAML-based auth flows over long-lived static credentials
  wherever the target system supports it. A token that expires in an
  hour is a smaller blast radius than a key that's valid until someone
  remembers to rotate it.

**Scoping — least privilege by default**

- Request the narrowest permission scope that satisfies the task. A
  read-only token where read-only suffices; a namespace-scoped Vault
  policy instead of root; a KV v2 path scoped to one service instead
  of a shared catch-all.
- When following an established secrets-path convention (e.g. KV v2
  naming under a per-service or per-team prefix), follow it — don't
  improvise a new pattern for one task's convenience.
- Flag it explicitly when a task seems to need broader access than
  expected. That's worth a second look before proceeding, not a
  silent workaround.

**Logging and error handling — nothing sensitive leaks through output**

- Never log a credential, token, or secret value — not even at debug
  level, not even truncated "just the first few characters." Log that
  an auth step happened and whether it succeeded; don't log what was
  used to do it.
- Exception messages and stack traces get the same treatment. A
  connection string or bearer token in a traceback is still a leak,
  even if nobody meant to print it.
- When writing test fixtures or examples, use obviously-fake values
  (`example-token-not-real`, `test@example.com`) — never a real
  credential, even an expired or revoked one, and never a real value
  with a couple of characters changed.

**Before committing**

- Scan the diff for anything that looks like a credential before it
  goes in: API keys, private key blocks, bearer tokens, connection
  strings with embedded passwords. If something looks like a secret
  and you're not sure, treat it as one until proven otherwise.

## Anti-Patterns

- Do NOT hardcode a credential "temporarily" with a `# TODO: move to
  Vault` comment — retrieve it from the secrets manager from the
  start, even in a first draft
- Do NOT log full credential values at any log level, including debug
- Do NOT request broader access scope than the task needs because
  it's easier to fetch one token instead of two
- Do NOT commit `.env` files containing real values, even to a
  private repo
- Do NOT reuse a real credential value in test fixtures or
  documentation examples
- Do NOT silently fall back to a hardcoded value when the secrets
  manager is unavailable — surface the gap instead

## Transition

Once credential handling is in place, hand off to
`test-driven-development` if the surrounding code isn't written yet,
or to `decision-records` if the secrets-handling approach involved a
non-obvious tradeoff (e.g. choosing a scoping model, or deciding how
to handle an environment without Vault access) worth documenting for
the next person.
