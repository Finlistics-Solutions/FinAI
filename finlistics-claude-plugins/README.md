
# FinListics Claude Plugins
## Reviewed by Claude Code

Plugin marketplace for FinListics ClientIQ integrations with Claude.

## Contents

```
.claude-plugin/marketplace.json     Marketplace catalog
finlistics-ai/                      FinListics AI plugin
├── .claude-plugin/plugin.json      Plugin manifest
├── .mcp.json                       FinListics AI MCP connector (OAuth)
└── agents/finlistics-analyst.md    Financial research subagent
```

## Install (Claude Code)

```
/plugin marketplace add <this-repo-url>
/plugin install finlistics-ai@finlistics
```

The FinListics AI connector authenticates via OAuth on first use; sign in with
your ClientIQ2 account when the browser window opens.

## Before first release

- [ ] Replace `REPLACE_WITH_CLAUDE_CODE_CLIENT_ID` in `finlistics-ai/.mcp.json`
      with the OAuth client id registered in the FinListics IdentityProvider for
      Claude Code (public client, PKCE, loopback redirect URI). If the client
      pins a fixed redirect port, add `"callbackPort": <port>` next to it.
- [ ] Verify the subagent's `tools` reference (`mcp__finlistics-ai`) matches the
      server name Claude Code assigns to the plugin's MCP server after install
      (`/plugin` > installed plugin > tools list).
- [ ] Run `claude plugin validate .` from the repository root.
- [ ] Test the full flow from a clean machine: marketplace add, install, OAuth
      sign-in, one research question routed to the finlistics-analyst subagent.

## Versioning

Bump `version` in `finlistics-ai/.claude-plugin/plugin.json` on every release;
installed clients pick up updates from that field.
