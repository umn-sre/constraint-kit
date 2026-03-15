# Skill: Markdown Compliance

## Purpose

Markdown that is structurally inconsistent is harder to read and breaks
rendering in some contexts. SKILL.md files in particular must pass
mdcompliance checks before a PR can merge — the CI gate enforces this.
Applying these rules during authoring avoids late-stage friction.

## When This Skill Is Active

When writing or reviewing any `.md` file in constraint-kit — SKILL.md,
role files converted to markdown, docs, README, or CHANGELOG.

## Agent Behavior

### Before generating any Markdown

Confirm the output will follow these rules. Do not produce non-compliant
Markdown and expect the author to fix it.

### Required structure for SKILL.md files

```

# Skill: [Name]           ← H1, title case, no trailing punctuation

## Purpose                ← H2, required section

[content]

## When This Skill Is Active   ← H2, required section

[content]

## Agent Behavior         ← H2, required section

[content]

## Anti-Patterns          ← H2, required section

[content]

## Transition             ← H2, required section

[content]

```

### Heading rules

- One blank line before and after every heading
- Heading levels must not skip — H1 → H2 → H3, never H1 → H3
- Use ATX style (`##`) not setext style (underline with `---`)
- No trailing punctuation in headings: `.,;:!?` are not allowed
- No bold or italic used as a heading substitute

### Blank line rules

- One blank line before and after fenced code blocks (` ``` `)
- One blank line before and after block quotes (`>`)
- No more than one consecutive blank line anywhere

### List rules

- Unordered list marker must be consistent throughout the file (use `-`)
- Ordered lists must use sequential numbering (`1.` `2.` `3.`), not all `1.`
- List continuation lines indented 2 spaces

### Other rules

- No trailing spaces on any line
- File must end with exactly one newline
- Lines should not exceed 100 characters (URLs exempt)
- No horizontal rules (`---` / `***` / `___`) as document separators

### Running compliance locally

```bash

# Check a single skill file

python bootstrap/mdcompliance.py skills/my-skill/SKILL.md --check

# Auto-fix a single skill file

python bootstrap/mdcompliance.py skills/my-skill/SKILL.md

# Check all skills

python bootstrap/mdcompliance.py skills/ --check

# Auto-fix all skills

python bootstrap/mdcompliance.py skills/

```

Configuration is read from `.markdownlintrc` at the repo root.
The `--check` flag reports without modifying files — use it to
verify before fixing.

## Anti-Patterns

- Do NOT skip heading levels (`##` directly under `#` is fine;
  `###` directly under `#` is not)
- Do NOT use `**Bold text**` on its own line as a section label —
  use a proper `##` heading instead
- Do NOT use `---` as a visual separator — it generates an MD035
  violation and is auto-removed by mdcompliance
- Do NOT leave trailing spaces — they are invisible and cause
  unnecessary diff noise
- Do NOT forget the blank line after a fenced code block — this
  is the most common violation in SKILL.md files

## Transition

After markdown compliance is confirmed, the file is ready for
the schema validator (`python bootstrap/validate.py`) which checks
structural content (required sections, valid field values) rather
than formatting.
