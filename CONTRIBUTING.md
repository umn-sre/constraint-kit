# Contributing to constraint-kit

constraint-kit is a plugin marketplace: two plugins (`constraint-design`,
`constraint-dev`) containing standard-format skills and agents. No custom
schemas, no build step.

## Layout

```text
.claude-plugin/marketplace.json      # marketplace manifest
plugins/<plugin>/plugin.json         # plugin manifest
plugins/<plugin>/skills/<name>/SKILL.md
plugins/<plugin>/agents/<name>.agent.md
scripts/validate.py                  # CI structure check
```

## Adding or changing a skill

1. Skills are directories under `plugins/<plugin>/skills/<name>/` with a
   `SKILL.md` whose frontmatter has `name` (matching the directory) and
   `description`. Supporting reference files live beside it and are
   linked relatively.
2. Write the `description` for the *triggering model*: start with "Use
   when …" so the assistant knows when to load it.
3. Skills that produce artifacts write them to the target repo's
   `.constraint-kit/` folder — never to arbitrary locations.
4. Cross-skill references use plain skill names (no vendor prefixes). If
   the referenced skill lives in the other plugin, say so.
5. If a skill is adapted from an upstream collection (obra/superpowers,
   mattpocock/skills), keep the adaptation minimal and note the source in
   the plugin README's Credits section.

## Adding or changing an agent

Agents are `plugins/<plugin>/agents/<name>.agent.md` with `name` and
`description` frontmatter. Keep them short: operating rules plus the
skills they follow. Behavior belongs in skills; agents select and
sequence them.

## Adding a plugin

A plugin is a bundle: a coherent set of skills and agents for one phase
of work. Add `plugins/<name>/` with `plugin.json` (see an existing one),
and register it in `.claude-plugin/marketplace.json`. Prefer extending an
existing plugin over adding a third unless the workflow phase is genuinely
distinct.

## Before opening a PR

```bash
python3 scripts/validate.py
```

CI runs the same check. Keep PRs focused: one skill/agent/plugin concern
per PR.
