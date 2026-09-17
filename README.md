# FinListics AI for Claude

Company and industry financial research powered by FinListics ClientIQ2 — company profiles, KPI
diagnostics, peer comparisons, financial metric history, and value narratives, sourced from
ClientIQ2 rather than generated.

This repository is a **Claude plugin marketplace**. The `finlistics-ai` plugin bundles two pieces
that only work together:

| Piece | What it is | What it does |
|---|---|---|
| **Connector** | A remote MCP server at `https://api.v2.finlistics-vm.com/mcp` | Supplies the `clientiq2_*` tools that fetch real ClientIQ2 data |
| **Skill** | [`skills/finlistics-ai/SKILL.md`](finlistics-claude-plugins/finlistics-ai/skills/finlistics-ai/SKILL.md) | Teaches Claude the Economist Assistant role: which tool to call, how to format results, what never to invent |

Installing the plugin installs both. The skill alone produces no ClientIQ2 data — it will say the
connector isn't enabled and refuse to substitute general knowledge. The connector alone returns raw
tool output with none of the response rules.

---

## Install

Works in Claude on the web, the Chat tab in Claude Desktop, Claude Cowork, and Claude Code.
Requires a paid Claude plan (Pro, Max, Team, or Enterprise) and a FinListics ClientIQ2 subscription.

### In Claude (web, Desktop, Cowork)

1. Open **Customize → Plugins** in the left sidebar.
2. Click **Browse plugins**, then add a marketplace from a GitHub repository:
   `Finlistics-Solutions/FinAI`
3. Install **finlistics-ai**.
4. Complete the ClientIQ2 sign-in when the consent screen appears.

### In Claude Code

```shell
/plugin marketplace add Finlistics-Solutions/FinAI
/plugin install finlistics-ai@finlistics
```

Authenticate on first use, or run `claude mcp login finlistics-ai`.

> **Each user authenticates individually.** OAuth is delegated per user; there is no shared
> organization token. The connector returns only what that account is entitled to see.

---

## Verify the install

Ask Claude:

> What are Salesforce's key financial metrics and how do they compare to peers?

A correct response cites ClientIQ2 figures, keeps the 🔴 🟡 🟢 ⚪ performance indicators intact, and
states the as-of period.

If Claude answers from general knowledge, says the connector isn't enabled, or offers "public data
as a fallback", the **connector** is not connected — the skill is loaded and doing exactly what it
was told to do when `clientiq2_*` tools are missing. Recheck the sign-in step.

---

## Repository layout

```
.claude-plugin/marketplace.json                    Marketplace catalog
.pre-commit-config.yaml                            Validation hooks
.github/workflows/validate.yml                     Same hooks in CI
docs/directory-submission.md                       Connectors Directory submission pack
scripts/audit-mcp-tools.py                         Tool-annotation audit against directory criteria
finlistics-claude-plugins/finlistics-ai/
├── .claude-plugin/plugin.json                     Plugin manifest
├── .mcp.json                                      Connector configuration
└── skills/finlistics-ai/SKILL.md                  The skill
```

---

## Development

Install [pre-commit](https://pre-commit.com) once per clone:

```shell
pre-commit install          # or: uvx pre-commit install
```

[`.pre-commit-config.yaml`](.pre-commit-config.yaml) runs JSON and YAML parsing, whitespace and
line-ending hygiene, `claude plugin validate` on both the marketplace and the plugin, and three
project-specific checks:

| Hook | Why |
|---|---|
| `skill-frontmatter` | `claude plugin validate` exits 0 on a missing frontmatter warning and has no `--strict` flag. Also enforces claude.ai's 200-character `description` ceiling, which the CLI doesn't know about. |
| `no-spa-mcp-endpoint` | The apex host serves the ClientIQ2 web app and answers `200 text/html` for any path, so an MCP client pointed at it fails silently instead of erroring. |
| `forbid-ds-store` | macOS metadata was previously committed into `skills/`. |

The same hooks run in CI via [.github/workflows/validate.yml](.github/workflows/validate.yml).
Run them by hand with `pre-commit run --all-files`; bypass with `git commit --no-verify`.

To test changes without installing:

```shell
claude --plugin-dir ./finlistics-claude-plugins/finlistics-ai
```

### Before submitting to the directory

Audit the live server's tool annotations — every tool needs a `title` and the applicable
`readOnlyHint` or `destructiveHint`, or the submission is rejected:

```shell
export MCP_TOKEN='<access token with scope mcp:tools>'
python3 scripts/audit-mcp-tools.py
```

See [docs/directory-submission.md](docs/directory-submission.md) for the full submission checklist,
listing copy, and privacy policy draft.

---

## Organization-managed alternative

Team and Enterprise owners who want to push the connector and skill to members directly, rather
than having each member install the plugin, can distribute through **Organization settings →
Plugins**. Members still authenticate to ClientIQ2 individually.

The older manual path — adding the connector under **Organization settings → Connectors** and
uploading `SKILL.md` under **Organization settings → Skills** — still works but is not recommended:
it requires an Owner, splits the two pieces apart, and has no in-place update. Reinstalling the
plugin is a single step.

---

## References

- [Use plugins in Claude](https://support.claude.com/en/articles/13837440-use-plugins-in-claude)
- [Manage plugins for your organization](https://support.claude.com/en/articles/13837433-manage-plugins-for-your-organization)
- [Submitting to the Connectors Directory](https://claude.com/docs/connectors/building/submission)
- [Submitting your plugin](https://claude.com/docs/plugins/submit)
- [Plugin marketplaces (Claude Code)](https://code.claude.com/docs/en/plugin-marketplaces)
