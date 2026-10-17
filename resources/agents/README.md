# Optional agent profiles

Agent profiles are optional. Store host-native definitions in a folder named for the host, then under `shared/` or `skill-specific/`. Each host may have at most two profiles: one skill-specific main workflow profile and one optional helper. Put planning, implementation, debugging, and review modes in sections of the main profile. If no profiles are supplied for a host, the installer creates no agent folders in the target project.

```text
resources/agents/<host>/shared/shared-<role>.agent.md
resources/agents/<host>/skill-specific/<skill-slug>-<role>.agent.md
```

Use `shared/` for a reusable helper that should be present in every skills repo, such as a code style reviewer. Keep its name in the `shared-` namespace and maintain the same definition across repos. Use `skill-specific/` for the main workflow profile and any repo-specific helper. Prefix the file name and every host-visible name or ID with the owning skill slug and role, such as `django-api-architect-workflow`.

Supported host destinations are:

| Host folder | Install destination |
|---|---|
| `claude-code` | `.claude/agents/` |
| `github-copilot` | `.github/agents/` |
| `codex` | `agents/codex/` |

To install, run `python scripts/install_agents.py --host <folder> --target <project-directory>`. Only the hosts above are supported: `--host` accepts one of those folder names and `--target` names the project that receives the profiles. Supply host-native files. The installer copies without replacing existing files. If a target already has a different file with the same name, it reports the conflict and makes no changes.

Codex role briefs are prompt files rather than host-discovered agent profiles. When Codex briefs are installed, the installer adds a marked routing block to the target's `AGENTS.md`, preserving its other contents. Codex can read the matching brief and delegate with native subagents when available, or follow the brief directly.
