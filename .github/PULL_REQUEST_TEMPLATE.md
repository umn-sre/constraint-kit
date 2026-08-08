# Pull request

## What

<!-- One or two sentences: what does this PR add or change? -->

## Type

- [ ] Skill (new or changed) — plugin: `constraint-design` / `constraint-dev` / `umn-compliance`
- [ ] Agent (new or changed)
- [ ] Plugin / marketplace manifest
- [ ] Docs / CI / repo maintenance

## Checklist

- [ ] `python3 scripts/validate.py` passes locally
- [ ] Skill/agent frontmatter `name` matches its file or directory name
- [ ] Cross-skill references use plain skill names (plugin noted when
      crossing the plugin boundary)
- [ ] Upstream-adapted content credits its source in the plugin README
- [ ] No `.constraint-kit/` content committed to this repo
