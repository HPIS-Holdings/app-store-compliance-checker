"""Markdown report rendering.
HARD RULE: the report lists ONLY verified issues (engine.verified_findings): rule FAILs backed by evidence and verified
store checks. Anything the checker could not verify is dropped - not softened, hedged or shown as a possible cause.
Full per-rule verdicts stay in the JSON output for internal coverage accounting only."""
from .engine import OUTPUT_POLICY

def markdown(res):
    s = res["snapshot"]; L = [f"# Store compliance check: {res['project']}", "",
        f"- Checker v{s['checker_version']} | rules snapshot {s['snapshot']} ({s['rule_count']} rules: {s['by_platform']}) | rules sha256 {s['rules_sha256'][:16]}",
        f"- Monorepo: {res.get('monorepo')} | apps: {len(res['apps'])}", f"- Output rule: {OUTPUT_POLICY}", ""]
    if not res["apps"]: L.append(f"**{res.get('summary')}**")
    for a in res["apps"]:
        L += [f"## App `{a.get('app_path', a['app_root'])}` ({a['framework']})", f"- Platforms: {a['platforms']}"]
        fs = a.get("findings", [])
        L += ["", f"### Verified issues ({len(fs)})"]
        if not fs: L.append("- No verified issues found.")
        for f in fs:
            ev = "; ".join(f.get("evidence", [])[:3])[:400]
            L.append(f"- **{f['check']}** {f['issue']} - Evidence: {ev}. Source: {f['official_url']}")
            if f.get("fix"): L.append(f"  - Fix: {str(f['fix'])[:300]}")
        ps = [v for v in a.get("verdicts", []) if v["verdict"] == "PASS"]
        if ps:
            L += ["", f"### Verified as meeting the rule ({len(ps)})"]
            L += [f"- **{v['rule_id']}** {v['title']} [level: {v.get('verification_level')}]. Rule: {v['official_url']}" for v in ps]
        L.append("")
    L += ["## Limits"] + [f"- {x}" for x in res["limits"]]
    return "\n".join(L) + "\n"
