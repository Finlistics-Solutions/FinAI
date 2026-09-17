#!/usr/bin/env python3
"""Audit a remote MCP server's tools against Anthropic's Connectors Directory
pre-submission criteria.

    https://claude.com/docs/connectors/building/review-criteria

Usage:
    export MCP_TOKEN='<bearer token>'
    python3 scripts/audit-mcp-tools.py
    python3 scripts/audit-mcp-tools.py --url https://api.v2.finlistics-vm.com/mcp --json

Exits non-zero if any tool fails a hard requirement, so it can gate CI.

Getting a token: complete the OAuth flow once in Claude Code
(`claude mcp login finlistics-ai`) and copy the access token, or mint one
against the IdP at https://idp.v2.finlistics-vm.com with scope "mcp:tools".
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_URL = "https://api.v2.finlistics-vm.com/mcp"
PROTOCOL_VERSION = "2025-06-18"
MAX_NAME_LEN = 64

# Phrases that read as instructions to Claude rather than descriptions of the
# tool. The directory rejects descriptions that "tell Claude how to behave".
INJECTION_PATTERNS = [
    "ignore previous", "ignore all previous", "disregard",
    "you must", "you should always", "always call", "never call",
    "do not call", "instead of calling", "before calling any other",
    "system prompt", "override", "regardless of",
]

# Safe/unsafe HTTP verbs appearing together in one tool suggest a catch-all
# tool, which is an automatic rejection.
UNSAFE_METHODS = ["post", "put", "patch", "delete"]
SAFE_METHODS = ["get", "head", "options"]


class Rpc:
    """Minimal MCP streamable-HTTP client."""

    def __init__(self, url, token):
        self.url = url
        self.token = token
        self.session_id = None
        self._id = 0

    def _headers(self):
        h = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        if self.session_id:
            h["Mcp-Session-Id"] = self.session_id
        return h

    def send(self, method, params=None, notify=False):
        payload = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            payload["params"] = params
        if not notify:
            self._id += 1
            payload["id"] = self._id

        req = urllib.request.Request(
            self.url, data=json.dumps(payload).encode(), headers=self._headers(), method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                sid = resp.headers.get("Mcp-Session-Id")
                if sid:
                    self.session_id = sid
                body = resp.read().decode("utf-8", "replace")
                ctype = resp.headers.get("Content-Type", "")
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:400]
            if e.code in (401, 403):
                die(f"{e.code} from the server. Set a valid MCP_TOKEN.\n{detail}")
            die(f"HTTP {e.code} calling {method}\n{detail}")
        except urllib.error.URLError as e:
            die(f"Could not reach {self.url}: {e.reason}")

        if notify:
            return None
        msg = parse_sse(body) if "text/event-stream" in ctype else json.loads(body or "{}")
        if msg is None:
            die(f"No JSON-RPC response for {method}")
        if "error" in msg:
            die(f"{method} returned an error: {json.dumps(msg['error'])}")
        return msg.get("result", {})


def parse_sse(body):
    """Pull the first JSON-RPC message out of an SSE stream."""
    data = []
    for line in body.splitlines():
        if line.startswith("data:"):
            data.append(line[5:].lstrip())
        elif not line.strip() and data:
            break
    if not data:
        return None
    return json.loads("\n".join(data))


def die(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(2)


def list_tools(rpc):
    rpc.send("initialize", {
        "protocolVersion": PROTOCOL_VERSION,
        "capabilities": {},
        "clientInfo": {"name": "directory-audit", "version": "1.0"},
    })
    rpc.send("notifications/initialized", {}, notify=True)

    tools, cursor = [], None
    while True:
        result = rpc.send("tools/list", {"cursor": cursor} if cursor else {})
        tools.extend(result.get("tools", []))
        cursor = result.get("nextCursor")
        if not cursor:
            return tools


def audit(tool):
    """Return (failures, warnings) for one tool definition."""
    fails, warns = [], []
    name = tool.get("name", "")
    desc = (tool.get("description") or "").strip()
    ann = tool.get("annotations") or {}

    if len(name) > MAX_NAME_LEN:
        fails.append(f"name is {len(name)} chars (max {MAX_NAME_LEN})")

    # "Every tool must include a title and the applicable hint."
    if not (ann.get("title") or "").strip():
        fails.append("annotations.title missing")

    read_only = ann.get("readOnlyHint")
    destructive = ann.get("destructiveHint")
    if read_only is not True and destructive is not True:
        fails.append("needs readOnlyHint:true (read) or destructiveHint:true (modifies/deletes)")
    if read_only is True and destructive is True:
        fails.append("readOnlyHint and destructiveHint are both true")

    if not desc:
        fails.append("description missing")
    elif len(desc) < 40:
        warns.append(f"description is only {len(desc)} chars; state what it does and when to call it")

    lowered = f"{desc} {json.dumps(tool.get('inputSchema', {}))}".lower()
    hits = [p for p in INJECTION_PATTERNS if p in lowered]
    if hits:
        fails.append(f"description reads as an instruction to Claude: {', '.join(hits)}")

    # Catch-all detection: one tool spanning safe and unsafe HTTP methods.
    schema_txt = json.dumps(tool.get("inputSchema", {})).lower()
    if "method" in schema_txt:
        has_unsafe = any(m in schema_txt for m in UNSAFE_METHODS)
        has_safe = any(m in schema_txt for m in SAFE_METHODS)
        if has_unsafe and has_safe:
            fails.append("looks like a catch-all tool mixing safe and unsafe methods; split read and write")

    # Freeform query tools must name or link the target API.
    if any(k in schema_txt for k in ("endpoint", "path", "query_string", "querystring", "raw_body")):
        if "http" not in desc.lower():
            warns.append("freeform query tool: description must link or name the target API")

    if ann.get("openWorldHint") is None:
        warns.append("openWorldHint unset; set true if it queries data outside a closed set")

    return fails, warns


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default=os.environ.get("MCP_URL", DEFAULT_URL))
    ap.add_argument("--token", default=os.environ.get("MCP_TOKEN"))
    ap.add_argument("--json", action="store_true", help="emit machine-readable results")
    args = ap.parse_args()

    if not args.token:
        die("no token. Set MCP_TOKEN or pass --token.")

    tools = list_tools(Rpc(args.url, args.token))
    if not tools:
        die("server returned no tools")

    results, n_fail, n_warn = [], 0, 0
    for tool in sorted(tools, key=lambda t: t.get("name", "")):
        fails, warns = audit(tool)
        n_fail += len(fails)
        n_warn += len(warns)
        results.append({"name": tool.get("name"), "failures": fails, "warnings": warns})

    if args.json:
        print(json.dumps({"url": args.url, "tool_count": len(tools), "results": results}, indent=2))
    else:
        print(f"{len(tools)} tools from {args.url}\n")
        for r in results:
            mark = "FAIL" if r["failures"] else ("warn" if r["warnings"] else " ok ")
            print(f"[{mark}] {r['name']}")
            for f in r["failures"]:
                print(f"         ✗ {f}")
            for w in r["warnings"]:
                print(f"         ! {w}")
        print(f"\n{len(tools)} tools, {n_fail} blocking, {n_warn} advisory")

    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
