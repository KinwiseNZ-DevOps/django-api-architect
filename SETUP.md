# Setup checklist

This repo is a scaffold copied from the skills-repo template. Work top to bottom, then delete this file. Nothing below is optional unless marked otherwise.

## 1. Name and identity

- [ ] Update `README.md`, keeping the template's section order and style (it matches every repo made from this template): ASCII banner, title and one-liner, badges (set OWNER, REPO and the skill count), principle in the [!IMPORTANT] callout, intro paragraph, "How they fit together" diagram (delete for a single-skill repo), usage phrases, status and footer links. Remove the `SETUP.md` line from the layout block when you delete `SETUP.md`
- [ ] Update `LICENSE`: replace `<copyright holder>`
- [ ] `AGENTS.md`: the general rules are identical in every repo by design; do not reword them. Adapt only two sections to the new repo: the **Repository map** (canonical sources, generated artefacts, editing rules, each with a reason) and **Known deliberate states** (delete the placeholder line). The verification command `python scripts/skills_tool.py check` is already correct because the template ships the same validator

## 2. Content

- [ ] Build the reference content first (pipeline in `reference-content/README.md`): drop originals into `raw/`, list project-specific names in `strip-terms.txt`, convert each item into a general-purpose file in `sources/`, and fill in `BRIEF.md`
- [ ] Build the skills from `BRIEF.md` and `sources/` only, never from `raw/`
- [ ] Design the skill set first: write the list of skills, their scope boundaries, and which skill owns each nearby topic. Scope discipline beats breadth: prefer curation over accumulation
- [ ] Write the first real skill from `templates/skill-template/SKILL.md`
- [ ] Write its description as a trigger contract: what it does, when to use it, keywords users type, and negative triggers for topics owned by sibling skills
- [ ] If skills share constraints or a "voice", put them in one references file and link it from skills, never copy it
- [ ] Add 3+ behavioural cases per skill to `evals/cases.jsonl` (real queries, expected behaviours, at least one refusal case)
- [ ] Replace the starter cases and delete `skills/example-skill/`

## 3. Register

```bash
python scripts/skills_tool.py catalogue   # refreshes the README table
python scripts/skills_tool.py check       # must end: ok (N skills), with no "ship checks skipped" note
```

## 4. Ship

- [ ] `git init`, commit, add the origin remote, push (repo name per 1)
- [ ] Make the repository **public**: CI minutes are free on public repos and billed on private ones
- [ ] Enable Actions in Settings; the workflow runs on pushes to `main` and PRs
- [ ] Set the GitHub "About" description and add topics (`agent-skills` at minimum)
- [ ] Delete `SETUP.md`
- [ ] Delete `reference-content/` (setup-only; the validator fails if it remains)
- [ ] Delete `templates/` (it is bootstrap scaffolding only; from now on, existing skills are the format reference, and `AGENTS.md` already reflects that)

## 5. Do not

- Do not hand-edit the README catalogue between the markers
- Do not add per-platform manifests until a platform needs one
- Do not import project-specific facts into skills; skills read a project's own architecture at runtime
