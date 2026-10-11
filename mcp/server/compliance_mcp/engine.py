"""Verdict engine. Statuses: PASS | FAIL | NEEDS_REVIEW | NOT_APPLICABLE | NOT_CHECKED.
Per rule:
 1. platform gate: rule platform target 'absent' -> NOT_APPLICABLE (basis platform-absent).
 2. feature gate (rule.applies_when, all required):
      DECLARED_FALSE -> NOT_APPLICABLE (basis owner-declaration, definite)
      NOT_DETECTED   -> NOT_APPLICABLE (basis not-detected, definite=False: static scan found no signal; not proof)
      UNRESOLVED     -> NEEDS_REVIEW
 3. checks: only checks whose own feature gate is met run. FAIL only from a demonstrated violation.
    PASS only if every check PASSes AND rule is in FULLY_STATIC; PASS level is 'source-config' unless a release
    artifact was scanned. Rules with no applicable check -> NEEDS_REVIEW (manual evidence).
 4. Greenlight disagreement (finding mapped to the rule's check while we say PASS/NOT_APPLICABLE, or Greenlight
    silent on a check it covers while we FAIL) -> NEEDS_REVIEW with both evidences.
 5. any exception in a check -> NOT_CHECKED."""
import hashlib, json, os
from pathlib import Path
from . import __version__
from .checks import CHECKS, CHECK_FEATURE
from .context import AppContext
from .discovery import discover
from .features import detect
from .safety import resolve_project, redact
from . import greenlight as GL
from .trace import trace_all
from . import store_checks

OUTPUT_POLICY = ("HARD RULE: report ONLY the items in `findings`. Each one is verified from code, config, build or store-listing data. "
  "Anything the checker could not verify is dropped: do not mention it, soften it, hedge it, or present it as a possible cause. "
  "Other verdict statuses are internal coverage accounting, not user-facing causes.")

def verified_findings(app):
    """User-facing issues: rule FAILs (demonstrated violation with evidence) + verified store checks. Nothing else."""
    out = [{"check": v["rule_id"], "issue": v["title"], "evidence": v["evidence"], "fix": (v.get("fix") or [None])[0], "official_url": v["official_url"], "source": v.get("verification_level")}
           for v in app.get("verdicts", []) if v["verdict"] == "FAIL" and v.get("evidence") and any(c.get("status") == "FAIL" for c in v.get("checks", []))]
    return out + [f for f in app.get("store_findings", []) if f.get("evidence") and f.get("official_url")]

FAMILY_TRACE = {"account-deletion": "account_deletion", "privacy": "privacy_links", "ai": "ai_boundary", "payments": "billing", "payments-external": "billing",
                "permissions-capabilities": "permissions", "health-data": "health", "health-medical": "privacy_links", "accounts-login": "permissions"}
HUMAN_MEDICAL = {"CUR-APL-1.4.1-DOCTOR", "CUR-APL-1.4.1-CLEARANCE", "CUR-APL-5.1.1ix-ENTITY", "CUR-GPL-HEALTH-DISCLAIMER", "CUR-GPL-HEALTH-CONSULT",
                 "CUR-GPL-HEALTH-MEDDEV", "CUR-GPL-HEALTH-EU-MDR", "CUR-GPL-HEALTH-HW", "CUR-GPL-ORG-ACCOUNT"}
DEL_RULES = {"CUR-APL-5.1.1v-ACCDEL", "CUR-APL-ACCDEL-SUPPORT", "CUR-GPL-ACCDEL"}
DEL_NOTE = {"UI_TO_BACKEND_IDENTITY_DELETION": "code path found from deletion UI to backend identity deletion (functional behaviour still unverified)",
            "UI_TO_BACKEND_DATA_DELETION_ONLY": "deletion UI reaches backend data deletion, but NO login-identity deletion found on that path (account may survive)",
            "UI_ONLY_OR_LOCAL_DELETION": "deletion UI found but no backend deletion call traced (local-only or backend outside repository)",
            "BACKEND_IDENTITY_DELETION_WITHOUT_UI_PATH": "backend can delete the identity, but no in-app UI path to it was traced",
            "NO_DELETION_PATH_FOUND": "no account deletion UI or backend path found in app, backend or shared code"}

DATA = Path(__file__).parent / "data"
FULLY_STATIC = {"CUR-APL-MIC", "CUR-APL-SPEECH", "CUR-APL-UR-IOS13", "CUR-GPL-TAPI-NEW", "CUR-GPL-TAPI-POLICY"}
STATUSES = ("PASS", "FAIL", "NEEDS_REVIEW", "NOT_APPLICABLE", "NOT_CHECKED")
ON = ("DETECTED", "DECLARED_TRUE")

class RuleError(Exception): pass

def rules_path(): return Path(os.environ.get("COMPLIANCE_RULES_FILE") or DATA / "current-rules.jsonl")
def load_rules(path=None):
    p = Path(path) if path else rules_path()
    if not p.exists(): raise RuleError(f"rules file not found: {p}")
    rules = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    for r in rules:
        if "applies_when" not in r: raise RuleError(f"rule {r.get('rule_id')} lacks applies_when (old rules file?)")
    return rules
def snapshot_info(path=None):
    p = Path(path) if path else rules_path(); rules = load_rules(p)
    meta = {}
    try: meta = json.loads((DATA / "snapshot.json").read_text())
    except Exception: pass
    return {"checker_version": __version__, "rules_file": str(p), "rules_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            "snapshot": meta.get("snapshot", rules[0].get("verified_date") if rules else None), "rule_count": len(rules),
            "by_platform": {k: sum(1 for r in rules if r["platform"] == k) for k in ("apple", "google")}, **{k: v for k, v in meta.items() if k not in ("snapshot",)}}

def _na(r, basis, ev, definite):
    return {"verdict": "NOT_APPLICABLE", "reason": f"not applicable: {basis}", "evidence": ev or [basis], "applicability": {"basis": basis, "definite": definite, "evidence": ev}}

def _annotate(v, r, ctx, feats, trace):
    cat = r.get("evidence_category", "JUDGMENT")
    unres = [k for k, x in feats.items() if k in r["applies_when"] and x["state"] == "UNRESOLVED" and "declare" not in x["evidence"][0]]
    dyn_check = any(c.get("status") == "NEEDS_REVIEW" and any("unresolved" in e for e in c["evidence"]) for c in v.get("checks", []))
    if v["verdict"] == "NEEDS_REVIEW" and (unres or dyn_check) and not ctx.config_resolved: cat = "UNRESOLVED_CONFIG"
    v["evidence_category"] = cat; v["family"] = r.get("family")
    v["next_evidence_action"] = ("Resolve config without executing app.config: run `npx expo config --json` in a trusted environment and attach the output; " if cat == "UNRESOLVED_CONFIG" else "") + r.get("next_evidence_action", "")
    t = FAMILY_TRACE.get(r.get("family"))
    if trace and t and v["verdict"] != "NOT_APPLICABLE":
        v["code_paths"] = {t: trace[t]}; v["evidence_type"] = "code-path"
        if r["rule_id"] in DEL_RULES:
            c = trace["account_deletion"]["classification"]; v["reason"] += f"; {DEL_NOTE[c]}"; v["code_path_classification"] = c
    else: v["evidence_type"] = "config" if any(c.get("level") == "source-config" for c in v.get("checks", [])) else ("declaration" if cat == "STORE" else "keyword/none")
    if r["rule_id"] in HUMAN_MEDICAL and v["verdict"] != "NOT_APPLICABLE" and feats.get("veterinary", {}).get("state") == "DETECTED" and feats["healthkit"]["state"] != "DETECTED":
        v["verdict"], v["evidence_category"] = "NEEDS_REVIEW", "JUDGMENT"
        v["reason"] = "veterinary app: applicability of this human-medical rule is a policy judgment (general privacy/misleading-content rules still apply)"
        v["next_evidence_action"] = "Owner/policy reviewer decides whether the app makes human-health claims; if not, declare human_health=false."
    if r["rule_id"] in HUMAN_MEDICAL and feats.get("human_health", {}).get("state") == "DECLARED_FALSE":
        v.update(verdict="NOT_APPLICABLE", reason="owner declared human_health=false", applicability={"basis": "owner-declaration", "definite": True, "evidence": ["human_health=false"]})
    return v

def evaluate_rule(r, ctx, feats, gl_by_check, artifact, trace=None):
    return _annotate(_evaluate_rule(r, ctx, feats, gl_by_check, artifact), r, ctx, feats, trace)

def _evaluate_rule(r, ctx, feats, gl_by_check, artifact):
    base = {"rule_id": r["rule_id"], "platform": r["platform"], "title": r["title"], "publisher_section_id": r["publisher_section_id"],
            "official_url": r["official_url"], "official_quote": (r.get("official_quotes") or [None])[0], "normative_strength": r["normative_strength"],
            "applies_when": r["applies_when"]}
    plat = ctx.platforms.get("ios" if r["platform"] == "apple" else "android", "unknown")
    if plat == "absent":
        return {**base, **_na(r, f"{'iOS' if r['platform']=='apple' else 'Android'} target absent ({ctx.framework})", [f"platforms: {ctx.platforms}"], True), "checks": [], "fix": [], "verification_level": "static"}
    gate = {k: feats[k] for k in r["applies_when"]}
    off = {k: v for k, v in gate.items() if v["state"] == "DECLARED_FALSE"}
    if off: return {**base, **_na(r, "owner declared feature absent: " + ", ".join(off), [e for v in off.values() for e in v["evidence"]], True), "checks": [], "fix": [], "verification_level": "declaration"}
    nd = {k: v for k, v in gate.items() if v["state"] == "NOT_DETECTED"}
    if nd: return {**base, **_na(r, "feature not detected by static scan: " + ", ".join(nd), [e for v in nd.values() for e in v["evidence"]], False), "checks": [], "fix": [], "verification_level": "static-inferred"}
    unres = {k: v for k, v in gate.items() if v["state"] == "UNRESOLVED"}
    results = []
    for c in r["static_checks"]:
        need = CHECK_FEATURE.get(c)
        if need and feats[need]["state"] not in ON: continue
        try: results += CHECKS[c](ctx, feats) if c in CHECKS else [{"check": c, "status": "NOT_CHECKED", "evidence": [f"no implementation for check {c}"], "fix": None, "level": None}]
        except Exception as e: results.append({"check": c, "status": "NOT_CHECKED", "evidence": [redact(f"check error: {e!r}")], "fix": None, "level": None})
    gate_ev = {k: {"state": v["state"], "evidence": v["evidence"][:3]} for k, v in gate.items()}
    st = [x["status"] for x in results]
    if unres: v, why = "NEEDS_REVIEW", "applicability unresolved: " + ", ".join(unres)
    elif not results: v, why = "NEEDS_REVIEW", "no automated check for this rule; manual evidence required (store listing, console forms, runtime behaviour)"
    elif "NOT_CHECKED" in st: v, why = "NOT_CHECKED", "a check could not run"
    elif "FAIL" in st: v, why = "FAIL", "demonstrated violation in static config"
    elif all(s == "PASS" for s in st) and r["rule_id"] in FULLY_STATIC: v, why = "PASS", "all checks passed with positive evidence"
    else: v, why = "NEEDS_REVIEW", "evidence incomplete; human confirmation required"
    gl = [f for x in results for f in gl_by_check.get(x["check"], [])]
    if gl_by_check is not None and gl_by_check.get("_status") == "ok":
        sev = [f for f in gl if f.get("severity") in ("CRITICAL", "HIGH", "WARN")]
        if v == "PASS" and sev: v, why = "NEEDS_REVIEW", "scanner disagreement: Greenlight reports a finding for this check"
        if v == "FAIL" and not gl and any(x["check"] in GL.COVERS and x["status"] == "FAIL" for x in results):
            v, why = "NEEDS_REVIEW", "scanner disagreement: Greenlight (which covers this check) reports nothing"
    level = "release-artifact" if artifact and v == "PASS" else ("source-config" if v in ("PASS", "FAIL") else ("derived-vendor-default" if any(x.get("level") == "derived-vendor-default" for x in results) else "static"))
    ev_all = [e for x in results for e in x["evidence"]]
    return {**base, "verdict": v, "reason": why, "applicability": {"basis": "gate met" if not unres else "unresolved", "features": gate_ev},
            "verification_level": level, "evidence": ev_all or [why], "checks": results, "greenlight": gl,
            "fix": [x["fix"] for x in results if x.get("fix") and x["status"] in ("FAIL", "NEEDS_REVIEW")]}

def check_app(app_root, repo_root=None, framework="expo-managed", platforms=None, rules=None, platforms_filter=None, rule_ids=None,
              declared=None, greenlight="auto", aab=None, apk=None, ipa=None, store_data=None):
    rules = rules or load_rules()
    ctx = AppContext(app_root, repo_root, framework, platforms, declared)
    feats = detect(ctx)
    glr = {"status": "disabled", "findings": []}
    if greenlight != "off": glr = GL.run(app_root, aab, apk, ipa)
    by = {"_status": glr["status"]}
    for f in glr["findings"]:
        if f["maps_to"]: by.setdefault(f["maps_to"], []).append(f)
    try: trace = trace_all(ctx)
    except Exception as e: trace = None; ctx.coverage["trace_error"] = redact(repr(e))
    if trace and feats.get("iap", {}).get("state") == "NOT_DETECTED" and trace["billing"]["classification"].startswith("EXTERNAL_CHECKOUT"):
        feats["iap"] = {"state": "DETECTED", "evidence": ["code path: " + e["at"] for e in trace["billing"]["external_checkout"][:3]], "label": "paid digital content / purchase flow"}
    out = []
    for r in rules:
        if platforms_filter and r["platform"] not in platforms_filter: continue
        if rule_ids and r["rule_id"] not in rule_ids: continue
        out.append(evaluate_rule(r, ctx, feats, by, bool(aab or apk or ipa), trace))
    counts = {s: sum(1 for x in out if x["verdict"] == s) for s in STATUSES}
    counts["NOT_APPLICABLE_definite"] = sum(1 for x in out if x["verdict"] == "NOT_APPLICABLE" and x["applicability"].get("definite"))
    counts["by_evidence_category"] = {c: sum(1 for x in out if x["verdict"] == "NEEDS_REVIEW" and x["evidence_category"] == c) for c in ("SOURCE", "UNRESOLVED_CONFIG", "ARTIFACT", "STORE", "JUDGMENT")}
    sf = store_checks.run_all(ctx, store_data, ipa)
    res = {"app_root": str(app_root), "framework": framework, "platforms": ctx.platforms, "trace": trace, "derived_config": ctx.derived, "dynamic_config_literals": ctx.dynamic_literals, "features": {k: {"state": v["state"], "evidence": v["evidence"][:3]} for k, v in feats.items()},
            "coverage": {**ctx.coverage, "greenlight": {k: v for k, v in glr.items() if k != "findings"}, "greenlight_findings": len(glr["findings"]),
                         "greenlight_unmapped": [f for f in glr["findings"] if not f["maps_to"]]},
            "counts": counts, "verdicts": out, "store_findings": sf}
    res["findings"] = verified_findings(res); return res

def check_project(project_path, platforms=None, rule_ids=None, declared=None, greenlight="auto", aab=None, apk=None, ipa=None, rules=None, store_data=None):
    root = resolve_project(project_path)
    rules = rules or load_rules()
    disc = discover(root)
    apps = []
    if not disc["apps"]:
        # a directory that is itself an Expo/RN app without a recognized marker is still checked conservatively
        return {"project": str(root), "snapshot": snapshot_info(), "monorepo": False, "apps": [], "summary": "no mobile app root found",
                "findings": [], "output_policy": OUTPUT_POLICY, "limits": LIMITS}
    for a in disc["apps"]:
        if not a["supported"]:
            apps.append({"app_root": str(a["path"]), "framework": a["framework"], "platforms": a["platforms"], "counts": {"NOT_CHECKED": len(rules)},
                         "coverage": {"note": f"framework {a['framework']} not supported by checker v{__version__}; all rules NOT_CHECKED"}, "verdicts": []}); continue
        res = check_app(a["path"], root, a["framework"], a["platforms"], rules, platforms, rule_ids, declared, greenlight, aab, apk, ipa, store_data)
        res["app_path"] = str(Path(a["path"]).relative_to(root)) or "."
        res["versions"] = a["versions"]; res["config"] = a["config"]; apps.append(res)
    tot = {s: sum(x["counts"].get(s, 0) for x in apps) for s in STATUSES}
    tot["VERIFIED_FINDINGS"] = sum(len(x.get("findings", [])) for x in apps)
    return {"project": str(root), "snapshot": snapshot_info(), "monorepo": disc["monorepo"], "apps": apps, "totals": tot,
            "findings": [{**f, "app_path": x.get("app_path")} for x in apps for f in x.get("findings", [])], "output_policy": OUTPUT_POLICY, "limits": LIMITS}

LIMITS = [
 "Static source/config scan only unless --aab/--apk/--ipa is given (then Greenlight inspects the artifact). PASS without an artifact is labelled verification_level=source-config.",
 "app.config.js/ts is never executed; values that only exist there are not verifiable and produce no finding.",
 "Library-contributed Android permissions are only checked when an artifact is given.",
 "App Store Connect / store-listing data is only used when supplied in .compliance/store.json; checks without their data emit nothing.",
 "Excluded by design (not verifiable from code/config/build/listing data): lookalike / terminated-developer 4.3 flags, reply-vs-resubmit rejection loops, subscription-attachment backend glitches.",
 "Rules gated on a feature run only when the feature is detected or declared in .compliance/features.json.",
 "Only Expo (managed/bare) and React Native app roots are checked; Flutter, native and Capacitor roots are listed but not checked.",
]
