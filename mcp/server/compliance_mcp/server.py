"""MCP server over stdio (newline-delimited JSON-RPC 2.0), stdlib only. Survives malformed input."""
import json, sys, traceback
from . import engine, __version__
from .discovery import discover
from .safety import resolve_project, PathError
PROTO = "2025-06-18"
_S = lambda **p: {"type": "object", "properties": p, "additionalProperties": False}
TOOLS = [
 {"name": "snapshot_info", "description": "Policy snapshot date, rule counts, rules-file sha256, checker version.", "inputSchema": _S()},
 {"name": "list_rules", "description": "List rules (optional platform / text filter).", "inputSchema": _S(platform={"type": "string", "enum": ["apple", "google"]}, query={"type": "string"})},
 {"name": "get_rule", "description": "Full rule record incl. official URL, verbatim quotes, verified date, applies_when.", "inputSchema": {**_S(rule_id={"type": "string"}), "required": ["rule_id"]}},
 {"name": "list_deprecated", "description": "Deprecated/superseded items (CONFIRMED / UNKNOWN / TEXT_CHANGED_SINCE_BASELINE) with official evidence.", "inputSchema": _S()},
 {"name": "discover_apps", "description": "Find mobile app roots in a local directory (framework, config state, platforms). Read-only.", "inputSchema": {**_S(project_path={"type": "string"}), "required": ["project_path"]}},
 {"name": "check_project", "description": "Check a local project. Returns `findings`: ONLY issues verified from code, config, build or store-listing data, each with evidence, official Apple/Google URL and fix. HARD RULE: report only `findings`; anything not verified is dropped - never soften, hedge or present it as a possible cause. Optional store_data = App Store Connect / listing data (same schema as .compliance/store.json).",
  "inputSchema": {**_S(project_path={"type": "string"}, platforms={"type": "array", "items": {"type": "string", "enum": ["apple", "google"]}},
                      rule_ids={"type": "array", "items": {"type": "string"}}, declared_features={"type": "object", "additionalProperties": {"type": "boolean"}},
                      greenlight={"type": "string", "enum": ["auto", "off"]}, aab={"type": "string"}, apk={"type": "string"}, ipa={"type": "string"}, store_data={"type": "object", "additionalProperties": True}), "required": ["project_path"]}},
]
TN = {t["name"]: t for t in TOOLS}

class ArgError(ValueError): pass
def _validate(name, args):
    sch = TN[name]["inputSchema"]
    if not isinstance(args, dict): raise ArgError("arguments must be an object")
    for k in sch.get("required", []):
        if k not in args: raise ArgError(f"missing required argument: {k}")
    for k, v in args.items():
        if k not in sch["properties"]: raise ArgError(f"unknown argument: {k}")
        t = sch["properties"][k]["type"]
        ok = {"string": isinstance(v, str), "array": isinstance(v, list) and all(isinstance(i, str) for i in v), "object": isinstance(v, dict) and (k == "store_data" or all(isinstance(i, bool) for i in v.values()))}[t]
        if not ok: raise ArgError(f"argument {k} must be {t}")
        enum = sch["properties"][k].get("enum") or sch["properties"][k].get("items", {}).get("enum")
        if enum and any(i not in enum for i in (v if isinstance(v, list) else [v])): raise ArgError(f"argument {k} must be one of {enum}")

def call(name, a):
    if name == "snapshot_info": return engine.snapshot_info()
    if name == "list_rules":
        q = (a.get("query") or "").lower()
        return [{"rule_id": r["rule_id"], "platform": r["platform"], "title": r["title"], "normative_strength": r["normative_strength"], "applies_when": r["applies_when"]}
                for r in engine.load_rules() if (not a.get("platform") or r["platform"] == a["platform"]) and (not q or q in json.dumps(r).lower())]
    if name == "get_rule":
        for r in engine.load_rules():
            if r["rule_id"] == a["rule_id"]: return r
        raise ArgError(f"unknown rule_id: {a['rule_id']}")
    if name == "list_deprecated":
        return [json.loads(l) for l in (engine.DATA / "deprecated-exclusions.jsonl").read_text().splitlines() if l.strip()]
    if name == "discover_apps":
        d = discover(resolve_project(a["project_path"])); d["apps"] = [{**x, "path": str(x["path"])} for x in d["apps"]]; return d
    if name == "check_project":
        return user_facing(engine.check_project(a["project_path"], a.get("platforms"), a.get("rule_ids"), a.get("declared_features"), a.get("greenlight", "auto"), a.get("aab"), a.get("apk"), a.get("ipa"), store_data=a.get("store_data")))

def user_facing(res):
    """Rule 1 enforced at the MCP boundary: drop every unverified verdict (NEEDS_REVIEW / NOT_CHECKED / NOT_APPLICABLE)
    and its evidence/fix text. Only verified FAIL/PASS verdicts and `findings` leave the server; counts remain for coverage accounting."""
    for a in res.get("apps", []):
        a["verdicts"] = [v for v in a.get("verdicts", []) if v["verdict"] in ("FAIL", "PASS")]
        for k in ("trace", "dynamic_config_literals", "features"): a.pop(k, None)
        a["coverage"] = {**{k: v for k, v in a.get("coverage", {}).items() if k != "greenlight_unmapped"}, "unverified_rules_dropped": sum(v for k, v in a.get("counts", {}).items() if k in ("NEEDS_REVIEW", "NOT_CHECKED"))}
    return res

def handle(msg):
    if not isinstance(msg, dict): return {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "invalid request: expected a JSON object"}}
    m, mid, params = msg.get("method"), msg.get("id"), msg.get("params")
    is_notif = "id" not in msg
    ok = lambda res: {"jsonrpc": "2.0", "id": mid, "result": res}
    err = lambda c, t: None if is_notif else {"jsonrpc": "2.0", "id": mid, "error": {"code": c, "message": t}}
    if not isinstance(m, str): return err(-32600, "invalid request: missing method")
    if params is not None and not isinstance(params, dict): return err(-32602, "params must be an object")
    params = params or {}
    if m.startswith("notifications/"): return None
    if m == "initialize":
        return ok({"protocolVersion": params.get("protocolVersion") if isinstance(params.get("protocolVersion"), str) else PROTO,
                   "capabilities": {"tools": {"listChanged": False}}, "serverInfo": {"name": "mobile-compliance-checker", "version": __version__}})
    if m == "ping": return ok({})
    if m == "tools/list": return ok({"tools": TOOLS})
    if m == "tools/call":
        name = params.get("name")
        if name not in TN: return err(-32602, f"unknown tool: {name}")
        args = params.get("arguments") if params.get("arguments") is not None else {}
        try:
            _validate(name, args)
            res = call(name, args)
            return ok({"content": [{"type": "text", "text": json.dumps(res, ensure_ascii=False)}], "isError": False})
        except (ArgError, PathError, engine.RuleError, FileNotFoundError) as e:
            return ok({"content": [{"type": "text", "text": f"error: {e}"}], "isError": True})
        except Exception as e:
            print(traceback.format_exc(), file=sys.stderr)
            return ok({"content": [{"type": "text", "text": f"internal error: {e!r}"}], "isError": True})
    return err(-32601, f"method not found: {m}")

def main():
    for line in sys.stdin:
        if not line.strip(): continue
        try: msg = json.loads(line)
        except (json.JSONDecodeError, RecursionError): resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}}
        else:
            try: resp = handle(msg)
            except Exception as e: resp = {"jsonrpc": "2.0", "id": msg.get("id") if isinstance(msg, dict) else None, "error": {"code": -32603, "message": f"internal error: {e!r}"}}
        if resp is not None: sys.stdout.write(json.dumps(resp) + "\n"); sys.stdout.flush()
def entry(): main()
if __name__ == "__main__": main()
