# Optional agent profiles

Agent profiles are optional. Store host-native definitions in a folder named for the host, then under `shared/` or `skill-specific/`. The installer looks for `*.agent.md` files in these folders. If none are supplied for a host, it reports that there is nothing to install and creates no agent folders in the target project.

```text
resources/agents/<host>/shared/shared-<role>.agent.md
resources/agents/<host>/skill-specific/<skill-slug>-<role>.agent.md
```

Use `shared/` for reusable agents that should be present in every skills repo, such as a code style reviewer. Keep their names in the `shared-` namespace and maintain the same definition across repos. Use `skill-specific/` for agents that carry one skill's workflow. Prefix the file name and every host-visible name or ID with the owning skill slug and role, such as `django-api-architect-debugger`.

Supported host destinations are:

| Host folder | Install destination |
|---|---|
| `claude-code` | `.claude/agents/` |
| `github-copilot` | `.github/agents/` |
| `codex` | `agents/codex/` |

Other hosts can use `--host <folder>` and `--destination <native-agent-folder>` when running `scripts/install_agents.py`. Supply host-native files. The installer copies without replacing existing files. If a target already has a different file with the same name, it reports the conflict and makes no changes.

Codex role briefs are prompt files rather than host-discovered agent profiles. When Codex briefs are installed, the installer adds a marked routing block to the target's `AGENTS.md`, preserving its other contents. Codex can read the matching brief and delegate with native subagents when available, or follow the brief directly.
