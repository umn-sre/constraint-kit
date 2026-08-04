# AGENTS.md — working on the constraint-kit repo

This repository is a plugin marketplace for GitHub Copilot and Claude
Code. It ships markdown skills, markdown agents, and JSON manifests —
there is no application code and no build step.

## Ground rules

- Structure is contract: `plugins/<plugin>/skills/<name>/SKILL.md` with
  `name` + `description` frontmatter, `plugins/<plugin>/agents/*.agent.md`,
  `plugin.json` per plugin, `.claude-plugin/marketplace.json` at the root.
- After any structural change, run `python3 scripts/validate.py` and fix
  every reported problem before claiming the work done.
- Skill `name` frontmatter must match its directory name. Marketplace
  entries must match the directories under `plugins/`.
- Cross-skill references use plain skill names; note the plugin when the
  reference crosses the plugin boundary.
- Skills instruct assistants to write artifacts into the *consuming*
  repo's `.constraint-kit/` folder. Never commit `.constraint-kit/`
  content to this repo.
- Upstream-adapted skills (obra/superpowers, mattpocock/skills) should
  stay close to their sources; keep local patches minimal and credit the
  source in the plugin README.
