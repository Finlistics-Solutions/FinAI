# Connectors Directory submission pack

Working notes and drafts for submitting the FinListics AI connector at
[claude.ai/admin-settings/directory/submissions/new](https://claude.ai/admin-settings/directory/submissions/new).

Requirements referenced from [Submitting to the Connectors Directory](https://claude.com/docs/connectors/building/submission)
and the [pre-submission checklist](https://claude.com/docs/connectors/building/review-criteria).

> Everything below is a **draft for review**, not approved copy. The privacy policy in
> particular states facts about data handling that only FinListics can confirm.

---

## 1. Tool annotations

Audit the live server before submitting:

```bash
export MCP_TOKEN='<access token with scope mcp:tools>'
python3 scripts/audit-mcp-tools.py
```

Every tool needs `annotations.title` plus the applicable hint. All thirteen `clientiq2_*` tools
read data, so `readOnlyHint: true` applies to each — that is also what lets Claude call them
without a per-call confirmation prompt. Longest tool name is 48 characters, within the 64 limit.

| Tool | `title` | `readOnlyHint` |
|---|---|---|
| `clientiq2_search_industries` | Search industries | `true` |
| `clientiq2_company_knowledge` | Get company financial profile | `true` |
| `clientiq2_company_ranking` | Rank companies in an industry | `true` |
| `clientiq2_industry_profile` | Get industry profile | `true` |
| `clientiq2_industry_strategic_framework` | Get industry goals and strategies | `true` |
| `clientiq2_industry_environmental_factors` | Get industry risks and disruptors | `true` |
| `clientiq2_industry_geographic_regions` | List geographic regions | `true` |
| `clientiq2_industry_metrics_annual_history` | Get industry metric history | `true` |
| `clientiq2_business_functions` | List business functions | `true` |
| `clientiq2_business_function_diagnostic_questions` | Get diagnostic questions | `true` |
| `clientiq2_financial_impact_solutions` | Get financial impact solutions | `true` |
| `clientiq2_finance_domain_knowledge` | Search ClientIQ2 knowledge base | `true` |
| `clientiq2_custom_chart` | Render a custom chart | see below |

Set `openWorldHint: true` on all of them — they query ClientIQ2's dataset rather than a
closed enumeration.

**`clientiq2_custom_chart` is a judgment call.** It neither reads nor destroys customer data;
it renders an image. If the render is transient, mark it `readOnlyHint: true`. If it persists a
stored asset, use `readOnlyHint: false` with `destructiveHint: false` and say so in the
description. Don't leave both hints unset — that fails review.

Two rejection triggers to check while you're in the tool definitions:

- **Descriptions must describe, not instruct.** Anything shaped like "always call this first"
  or "ignore X" is read as a prompt-injection pattern. Behavioural rules belong in `SKILL.md`,
  which is exactly where they already are.
- **No catch-all tools.** A single tool taking a `method` parameter spanning GET and POST is an
  automatic rejection. The current thirteen are all purpose-built, so this should be clean.

---

## 2. Privacy policy

Remote connectors supply an **HTTPS privacy policy URL** in the portal. (The README section and
`privacy_policies` manifest array described in the docs apply to *local* connectors packaged as
MCPB — not to this one.) Missing or incomplete policies are an immediate rejection.

Suggested location: `https://finlistics.com/legal/claude-connector-privacy`

The policy must cover five areas. Draft below — **every bracketed claim needs confirmation from
whoever owns the server, and the whole thing needs a legal read. I'm not a lawyer.**

---

### FinListics AI for Claude — Privacy Policy

*Last updated: [DATE]*

This policy covers the FinListics AI connector, which lets Claude retrieve ClientIQ2 data on
behalf of an authenticated FinListics user. It supplements the [FinListics Privacy Policy](https://finlistics.com/privacy).

**What we collect.** When you connect FinListics AI to Claude, you authenticate through the
FinListics identity provider (`idp.v2.finlistics-vm.com`) using OAuth 2.0. We receive:

- Your FinListics account identifier and the OAuth scopes you grant (`mcp:tools`, `offline_access`)
- The query parameters Claude sends with each tool call — company names, industry identifiers,
  metric selections, date ranges, and similar lookup arguments
- Standard request metadata: timestamp, IP address, and user agent

We do **not** receive your Claude conversation history, files you upload to Claude, or any part
of the conversation other than the arguments of the specific tool call. [Confirm.]

**How we use it.** Query parameters are used to resolve and return the requested ClientIQ2 data.
Request metadata is used for authentication, rate limiting, abuse prevention, and service
reliability. [Confirm whether query content is used for analytics or product improvement — if it
is, say so explicitly here.]

**Where it is stored.** Requests are served from [REGION] on infrastructure operated by
[PROVIDER]. Access tokens are held by your Claude client; FinListics stores [describe
server-side token or session storage]. [Confirm.]

**Third-party sharing.** FinListics does not sell connector data or share it with third parties
for advertising. Data is shared only with infrastructure subprocessors necessary to operate the
service, listed at [SUBPROCESSOR PAGE URL]. Anthropic receives only the tool responses your
queries return, as part of the Claude conversation. [Confirm.]

**Retention.** Request logs are retained for [N days/months] and then deleted. Refresh tokens
remain valid until you disconnect the connector in Claude or revoke access in your FinListics
account. ClientIQ2 account data is governed by your existing FinListics agreement. [Confirm.]

**Your choices.** Disconnect at any time from **Customize → Connectors** in Claude, which
invalidates the connector's access. To request deletion of connector request logs, contact us.

**Contact.** [PRIVACY CONTACT EMAIL] — FinListics Solutions, [POSTAL ADDRESS].

---

## 3. Remaining submission assets

| Item | Limit / spec | Status |
|---|---|---|
| Server URL | HTTPS, streamable HTTP or SSE | `https://api.v2.finlistics-vm.com/mcp` ✅ |
| URL model | Universal URL (one for everyone) | ✅ one host for all tenants — confirm |
| Server name | ≤100 chars | draft below (19) |
| Tagline | ≤55 chars | draft below (51) |
| Description | ≤2,000 chars | draft below (915) |
| Categories | 1–5 | Sales, Finance, Productivity — pick from the portal's list |
| Documentation URL | public by publish date; help-center article or blog post is enough | **to write** |
| Privacy policy URL | HTTPS, covers the five areas above | **to publish** |
| Support contact | — | **to decide** |
| Icon | required; portal states the exact spec | **to supply** |
| URL slug | permanent once published | suggest `finlistics-ai` |
| Test credentials | fully populated account, end-to-end steps | **to prepare** |
| Allowed link URIs | optional but recommended | see below |

### Draft listing copy

**Name:** `FinListics ClientIQ`

**Tagline:** `Company and industry financial research for sellers`

**Description:**

> FinListics ClientIQ brings company and industry financial intelligence into Claude for
> enterprise B2B sales teams.
>
> Ask about any company in the ClientIQ2 dataset and get its financial profile, metric history,
> peer benchmarks, business goals, and opportunities for improvement — each figure sourced from
> ClientIQ2 rather than generated. Diagnose where a prospect underperforms its industry, quantify
> the impact of a one percent change with Power of One, and pull the financial impact solutions
> mapped to the KPIs you want to move.
>
> Industry coverage includes profiles, goals and strategies, external forces and risks, and
> annual metric history by geographic region, with quartile benchmarks for peer comparison.
>
> Every tool is read-only. Each user authenticates to their own FinListics account, so the
> connector returns only the data that account is entitled to see. A FinListics ClientIQ2
> subscription is required.

### Allowed link URIs

Tool results return ClientIQ2 deep links and chart image URLs, which the skill renders directly.
Declaring the origins suppresses a confirmation prompt on every link:

- `https://v2.finlistics-vm.com` — the ClientIQ2 web app
- `https://api.v2.finlistics-vm.com` — chart and image responses, if served from the API host

Confirm whether chart images come from a third host (CDN or bucket). Each origin must be one
FinListics owns; subdomains are not implied, so list every one. Entries you don't own are
removed during review.

### Test credentials

Reviewers run a functional test of every tool, so the account must have data behind all thirteen.
Prepare:

- Username and password for a populated ClientIQ2 account, with any SSO or MFA steps spelled out
- A named example company that returns full `MetricsAnnualHistory` and `RecommendedPeers`
- A named example industry with region coverage
- A note that `clientiq2_company_ranking` needs the global region UID
  `8fda83cc-845a-4b91-b819-e44f602e666a` when no region is given

Before submitting, exercise every tool yourself through the
[MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) or as a custom connector in
Claude — the portal asks you to confirm you have.

---

## 4. Order of operations

1. Fix tool annotations on the server; rerun `scripts/audit-mcp-tools.py` until it exits 0
2. Publish the privacy policy and the public documentation page
3. Submit the **connector** to the Connectors Directory
4. Once listed, submit the **plugin** (skill + connector) at
   [claude.ai/admin-settings/directory/submissions/plugins/new](https://claude.ai/admin-settings/directory/submissions/plugins/new)

Plugins whose MCP servers already appear in the Connectors Directory draw fewer user warnings and
are likelier to reach Anthropic Verified, which is why the connector goes first.
