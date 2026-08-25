# FinAI

FinListics ClientIQ2 for Claude — a RAG-based assistant that answers questions about company and
industry financial performance.

The integration has **two independent pieces**, and both must be installed for it to work:

| Piece | What it is | What it does |
|---|---|---|
| **FinListics AI connector** | A remote MCP server at `https://v2.finlistics-vm.com/mcp` | Supplies the `clientiq2_*` tools that fetch real ClientIQ2 data |
| **FinListics AI skill** | `finlistics-claude-plugins/finlistics-ai/skills/finlistics-ai/` | Teaches Claude the Economist Assistant role: which tool to call, how to format results, what never to invent |

The skill without the connector produces no ClientIQ2 data — it will say the connector isn't enabled
and refuse to substitute general knowledge. The connector without the skill returns raw tool output
with none of the response rules. Install both.

---

## Before you start

- You must be an **Owner** on a **Team** or **Enterprise** plan. Members cannot add connectors or
  organization skills.
- Anthropic connects to the MCP server **from Anthropic's cloud**, not from the user's browser. The
  server must be reachable over the public internet from Anthropic's IP ranges. A server behind a
  VPN, a private network, or an IP allowlist will not connect.

---

## Part 1 — Add the FinListics AI connector

1. Go to **Organization settings → Connectors**.
2. Click **Add**.
3. Hover **Custom**, then select **Web**.
4. In **Remote MCP server URL**, enter:

   ```
   https://api.v2.finlistics-vm.com/mcp
   ```

5. Give it a name users will recognize, e.g. `finlistics-ai`.
6. Open **Advanced settings** and fill in **OAuth Client ID** with 

   ```
   finlistics-ai.claude-code.prod
   ```
7. Click **Add**.

> **Do not reuse the client ID from `.mcp.json`.** That file configures *Claude Code*, which
> authenticates from the user's own machine over a loopback redirect
> (`clientId: finlistics-ai.claude-code.prod`, `callbackPort: 51789`). claude.ai redirects to
> `https://claude.ai/api/mcp/auth_callback` instead, so the Claude Code client will be rejected at
> the authorization step. claude.ai needs either DCR or its own registered client.

> **Editing a connector is not supported.** To change the URL or credentials, remove the connector
> and add it again.

---

## Part 2 — Upload the FinListics AI skill

### 2a. Enable skills for the organization

Go to **Organization settings → Skills** and turn on both:

- **Code execution and file creation**
- **Skills**

Skills depend on code execution. If code execution is off, skills will not be available.

### 2b. Upload the skill as a .md file in claude.ai

Find a `SKILL.md` file in `finlistics-claude-plugins/finlistics-ai/skills/finlistics-ai/` and upload it to claude.ai under **Organization settings → Skills → Upload skill**.

### Skill frontmatter limits

claude.ai enforces limits on the YAML frontmatter in `SKILL.md` that Claude Code does not:

| Field | Limit | Current |
|---|---|---|
| `name` | 64 characters | 13 ✅ |
| `description` | **200 characters** | 197 ✅ |

The `description` was shortened specifically to fit the 200-character ceiling — a longer,
more detailed description will cause the upload to be rejected. 

---

## Part 3 — What each member does once

Both pieces are pushed by the admin, but **each user must authenticate to ClientIQ2 individually**.
OAuth is delegated per user; there is no shared organization token.

1. The skill is already on — confirm under **Customize → Skills**.
2. Connect the connector under personal **Settings → Connectors**, and complete the ClientIQ2 sign-in
   when the consent screen appears.

---

## Verify the install

Ask Claude:

> What are Salesforce's key financial metrics and how do they compare to peers?

A correct response cites ClientIQ2 figures, keeps the 🔴 🟡 🟢 ⚪ performance indicators intact, and
states the as-of period.

If Claude answers from general knowledge, says the connector isn't enabled, or offers "public data as
a fallback", the **connector** is not connected — the skill is loaded and doing exactly what it was
told to do when `clientiq2_*` tools are missing. Recheck Part 1 and the user's OAuth sign-in.

---

## Updating the skill later

There is no in-place edit. To ship a new version:

1. Edit `SKILL.md` in this repository and commit.
2. In **Organization settings → Skills**, remove the old `finlistics-ai` skill and upload the new `.md` file.

---

## Repository layout

```
.claude-plugin/marketplace.json                    Marketplace catalog — stub, not used yet
finlistics-claude-plugins/finlistics-ai/
├── .claude-plugin/plugin.json                     Plugin manifest
├── .mcp.json                                      MCP connector config — Claude Code only
└── skills/finlistics-ai/SKILL.md                  The skill (upload this to claude.ai)
```

> **`.claude-plugin/` is a stub for future work.** The `marketplace.json` catalog it contains is a
> placeholder for distributing this as a Claude Code plugin marketplace later. Nothing in the install
> steps above depends on it — the connector is added in claude.ai and the skill is uploaded manually.

## References

- [Provision and manage skills for your organization](https://support.claude.com/en/articles/13119606-provision-and-manage-skills-for-your-organization)
- [How to create custom skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)
- [Get started with custom connectors using remote MCP](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp)
- [MCP connectors](https://support.claude.com/en/articles/14503689-mcp-connectors)
