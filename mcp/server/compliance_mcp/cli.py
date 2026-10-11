"""mcc - mobile store compliance checker CLI.
  mcc check <path> [--format md|json] [--out FILE] [--platform apple|google] [--rule ID] [--declare k=true|false]
                   [--greenlight auto|off] [--aab F] [--apk F] [--ipa F] [--fail-on-review]
  mcc discover <path>      app roots / frameworks / config state (JSON)
  mcc rules [--platform]   list rules      mcc snapshot   policy snapshot info
Exit codes: 0 no verified issue | 1 at least one verified issue (FAIL or store finding) | 2 bad input | 3 internal error | 4 NEEDS_REVIEW present with --fail-on-review"""
import argparse, json, sys
from . import engine, report
from .discovery import discover
from .safety import resolve_project, PathError

def _decl(items):
    d = {}
    for it in items or []:
        k, _, v = it.partition("=")
        if v.lower() not in ("true", "false"): raise PathError(f"--declare expects key=true|false, got {it!r}")
        d[k] = v.lower() == "true"
    return d

def main(argv=None):
    ap = argparse.ArgumentParser(prog="mcc", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    c = sp.add_parser("check"); c.add_argument("path"); c.add_argument("--format", choices=["md", "json"], default="md"); c.add_argument("--out")
    c.add_argument("--platform", action="append", choices=["apple", "google"]); c.add_argument("--rule", action="append"); c.add_argument("--declare", action="append")
    c.add_argument("--greenlight", choices=["auto", "off"], default="auto"); c.add_argument("--aab"); c.add_argument("--apk"); c.add_argument("--ipa")
    c.add_argument("--fail-on-review", action="store_true")
    d = sp.add_parser("discover"); d.add_argument("path")
    r = sp.add_parser("rules"); r.add_argument("--platform", choices=["apple", "google"])
    sp.add_parser("snapshot")
    try: a = ap.parse_args(argv)
    except SystemExit as e: return 2 if e.code else 0
    try:
        if a.cmd == "snapshot": print(json.dumps(engine.snapshot_info(), indent=1)); return 0
        if a.cmd == "rules":
            for x in engine.load_rules():
                if not a.platform or x["platform"] == a.platform: print(f"{x['rule_id']:30} {x['platform']:6} {x['normative_strength']:8} {x['title']}")
            return 0
        if a.cmd == "discover":
            res = discover(resolve_project(a.path)); res["apps"] = [{**x, "path": str(x["path"])} for x in res["apps"]]
            print(json.dumps(res, indent=1)); return 0
        res = engine.check_project(a.path, a.platform, a.rule, _decl(a.declare), a.greenlight, a.aab, a.apk, a.ipa)
        text = json.dumps(res, indent=1) if a.format == "json" else report.markdown(res)
        if a.out: open(a.out, "w").write(text)
        else: sys.stdout.write(text)
        t = res.get("totals", {})
        if t.get("FAIL") or t.get("VERIFIED_FINDINGS"): return 1
        if a.fail_on_review and t.get("NEEDS_REVIEW"): return 4
        return 0
    except (PathError, engine.RuleError, FileNotFoundError) as e: print(f"error: {e}", file=sys.stderr); return 2
    except Exception as e: print(f"internal error: {e!r}", file=sys.stderr); return 3

def entry(): sys.exit(main())
if __name__ == "__main__": entry()
