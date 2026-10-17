# AGENTS.md

Agent map and standing rules for this repository. Read this file as policy, not suggestions. Every rule carries its reason: when a situation is not covered, generalise from the reason rather than guessing.

## Ground truth

- Never speculate about code or files you have not opened. If asked about a file, read it before answering. Reason: confident claims about unread files are indistinguishable from truth in review.
- File and directory names are not reliable evidence of what something does. Reason: naming drifts; contents do not.
- Documentation describes intent, not implementation state. Verify in the actual files before reporting status. Reason: docs lag behind code in every repo.

## Scope of changes

- Make the smallest correct change that satisfies the task. Reason: every extra line is extra review burden and extra risk. Concretely, do not:
  - Add docstrings, comments, or type annotations to content you did not change.
  - Add error handling, fallbacks, or caveats for scenarios that cannot happen (e.g. already covered by the validator). Validate at system boundaries only.
  - Create helpers or abstractions for one-time operations, or design for hypothetical requirements.
  - Refactor or "improve" anything beyond what the task asked.
  - Add comments beyond what the code genuinely needs. Keep the codebase mostly clean: comment only where the logic is not self-evident, and keep those comments short. Reason: comments that restate the code rot into lies; the code is read far more often than it is written.
  - Leave useless comments behind. When editing a file, delete comments in the lines you touch that are wrong, outdated, or say nothing the code does not already say. Reason: dead comments accumulate until readers stop trusting every comment, including the useful ones.
- Prefer editing the source of a rule over editing a restatement of it. Reason: copies drift.

## Accuracy and honesty

- Separate observed fact from inference, and mark anything uncertain.
- If a check cannot be run, say so explicitly instead of reporting success.
- Do not claim completion stronger than the evidence; state exactly what was checked.
- Solve the problem, not the test. Behavioural cases measure quality; they do not define it. If a case or check is wrong, say so rather than working around it.

## Verification

Before reporting any change done, run:

```bash
python scripts/skills_tool.py check
```

Checks: frontmatter, name/folder match, description length and trigger, body under 500 lines, relative links resolve, at least 3 eval cases per skill, catalogue not stale, no em or en dashes in any file. It also fails on leftover `<placeholder>` text and on setup scaffolding (`SETUP.md`, `templates/`, `reference-content/`) in the tree.

- The tool is necessary but not sufficient for content quality. For new or changed skill body text, also re-read the changed SKILL.md end to end. Reason: a validator checks structure; only reading checks that the instructions still make sense.

## Repository map

- `skills/<name>/SKILL.md`: the only source of skill content. Folder name equals frontmatter `name`.
- New skills follow the house format that existing skills embody: folder name equals frontmatter `name`; frontmatter, gate, steps, hard rules.
- `reference-content/` is git-ignored and never committed: it holds private source material and the names being stripped. Reason: once pushed to a public repo it cannot be recalled.
- Custom to this repo:
  - The skills are self-contained on purpose: every mechanism, pattern and snippet a skill needs lives in the skill body, never in a source that is not shipped. Reason: skills that lean on vanished sources mislead agents.
  - `django-api-architect` is the router; it links every sibling and is the entry point for install. Reason: one install target keeps the set coherent.
  - `reference-content/strip-terms.txt` allows the public styleguide's repo names on purpose (credited as theory), while the owner's company name, author names and the example project's internal module names stay stripped, with one exception: the `LICENSE` copyright line names the company on purpose. Reason: recorded decisions by the owner on 2026-10-17.

## Irreversible and shared actions

- Proceed freely for local, reversible actions: editing files, running checks, regenerating the catalogue.
- Ask first for anything destructive, hard to undo, or visible to others: deleting branches or history, force-pushes, changing repository visibility, pushing to shared sources. Reason: damage in a public repo cannot be recalled.

## Known deliberate states (dated)

- None.

## Anti-drift close-out

Before reporting done, confirm the change introduced no new local convention (a new section shape, a new file pattern, a divergent description style). If it did, either move it into the shared source or record the approved exception here. Reason: un-owned variations are how a standard silently dissolves.

## Close-out report

Finish every task with these five points, in this order:

1. What changed and why
2. Files changed
3. Validation run, and the result
4. Validation skipped, and why
5. Residual risks

## How to respond

- Reply in paragraphs: flowing prose, one idea per sentence, short paragraphs. Use lists only where the content is genuinely a list (the five-point close-out report, file paths, step sequences).
- Keep replies under 200 words. Go longer only when the user clearly asks for a thorough response. If more depth seems useful, offer it in one short line rather than writing it unprompted. Reason: long replies bury the decision the user needs to make.
- Write in British / New Zealand English throughout: behaviour, colour, organise, initialise, "-ise" endings, NZ date and spelling conventions. Reason: mixed spellings in one reply read as carelessness to a NZ audience.
- Simplify so a 16-year-old high school student could follow it: everyday words first, explain any unavoidable term the first time it appears, one technical term per sentence. Reason: if the explanation needs jargon to be understood, it has not explained anything.
- If the next step is one the user must do themselves (a setting to change, something to install, a click in a website), brief them first: say what is about to happen, what the step is for, and what success will look like. Then give exactly that one step, completely and simply. Reason: handing over five steps at once invites skipped and half-understood steps.
- After each user-side step, stop and wait for the user to say they are done before giving the next step. Do not stack several manual steps in one reply. Reason: one task at a time keeps confirmation honest and lets problems surface at the step that caused them.
- No padding, no restating the question, no caveats that carry no information.
- Skip em dashes and en dashes entirely and always. They are banned in every reply, every file, every commit message, prose and code comments alike. Every dash in text must be a plain hyphen (-). If a hyphen does not fit, use a comma or rewrite the sentence. Reason: nothing justifies an em dash; a banned character that appears anywhere is a single, checkable, zero-tolerance rule.
