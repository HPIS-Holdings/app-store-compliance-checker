"""Acceptance tests for CHECKER-HARDENING-001.
Run: python -m unittest discover -s tests -v   (real-MCP-client tests need `pip install "mcp>=1.10,<2"`)."""
import asyncio, json, os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
HERE = Path(__file__).parent; SRV = HERE.parent; sys.path.insert(0, str(SRV))
from compliance_mcp import engine
from compliance_mcp.safety import redact, resolve_project, PathError
from compliance_mcp.discovery import discover
FX = HERE / "fixtures"
HEALTH_AI_SUBS = ("1.4.1", "HEALTH", "5.1.3", "HK", "HC-", "5.1.1ix", "ORG-ACCOUNT", "5.1.2i-AI", "AI-REPORT", "3.1.1-IAP", "3.1.2", "SUBS", "PAYMENTS", "PBL", "2.1-IAP")
_cache = {}
def run(name, **kw):
    key = (name, json.dumps(kw, sort_keys=True))
    if key not in _cache: _cache[key] = engine.check_project(str(FX / name), greenlight=kw.pop("greenlight", "off"), **kw)
    return _cache[key]
def V(name, **kw):
    a = run(name, **kw)["apps"][0]; return {v["rule_id"]: v for v in a["verdicts"]}, a

class Invariants(unittest.TestCase):
    """Every finding has evidence + official rule ref; missing evidence never PASS / definite NA."""
    def test_all_fixtures(self):
        for fx in sorted(p.name for p in FX.iterdir()):
            res = run(fx)
            for a in res["apps"]:
                for v in a["verdicts"]:
                    with self.subTest(fx=fx, rule=v["rule_id"]):
                        self.assertTrue(v.get("evidence"), "evidence missing"); self.assertTrue(v["official_url"].startswith("https://"))
                        self.assertIn(v["verdict"], engine.STATUSES)
                        if v["verdict"] == "PASS":
                            self.assertTrue(v["checks"] and all(c["status"] == "PASS" for c in v["checks"])); self.assertIn(v["verification_level"], ("source-config", "release-artifact"))
                        if v["verdict"] == "NOT_APPLICABLE" and v["applicability"].get("definite"):
                            self.assertIn(v["applicability"]["basis"].split(" ")[0], ("owner", "iOS", "Android"))
                        if v["verdict"] == "FAIL": self.assertTrue(any(c["status"] == "FAIL" for c in v["checks"]))

class Clean(unittest.TestCase):
    def test_irrelevant_apps_get_no_health_ai_subscription_violations(self):
        for fx in ("simple-clean", "game", "wallpaper", "monorepo"):
            v, a = V(fx)
            self.assertEqual(a["counts"]["FAIL"], 0, fx)
            for rid, x in v.items():
                if any(k in rid for k in HEALTH_AI_SUBS) and "HEALTH-DECL" not in rid:  # Health apps declaration applies to ALL apps
                    with self.subTest(fx=fx, rule=rid): self.assertEqual(x["verdict"], "NOT_APPLICABLE"); self.assertFalse(x["applicability"]["definite"])
    def test_game_health_points_not_health(self):
        v, a = V("game"); self.assertEqual(a["features"]["health"]["state"], "NOT_DETECTED"); self.assertEqual(a["features"]["microphone"]["state"], "NOT_DETECTED")
    def test_static_pass_is_labelled(self):
        v, _ = V("simple-clean"); self.assertEqual(v["CUR-GPL-TAPI-NEW"]["verdict"], "PASS"); self.assertEqual(v["CUR-GPL-TAPI-NEW"]["verification_level"], "source-config")

class Negative(unittest.TestCase):
    def test_health_bad_expected_fails(self):
        v, a = V("health-bad")
        for rid in ("CUR-APL-MIC", "CUR-APL-SPEECH", "CUR-APL-HK-USAGE", "CUR-APL-UR-IOS13", "CUR-GPL-TAPI-NEW", "CUR-GPL-TAPI-EXISTING", "CUR-GPL-TAPI-POLICY", "CUR-APL-5.1.1ii-CONSENT"):
            with self.subTest(rule=rid): self.assertEqual(v[rid]["verdict"], "FAIL")
        self.assertEqual(a["counts"]["FAIL"], 8)
    def test_healthkit_sharing_rules_do_not_fail_from_other_checks(self):
        v, _ = V("health-bad")
        for rid in ("CUR-APL-HK-3P", "CUR-APL-5.1.2vi-HEALTHKIT"): self.assertEqual(v[rid]["verdict"], "NEEDS_REVIEW", rid)
        v, _ = V("ai-client")   # AI present, HealthKit absent -> HK rules NA, not FAIL
        for rid in ("CUR-APL-HK-USAGE", "CUR-APL-HK-3P", "CUR-GPL-HC-LIMITED", "CUR-GPL-HC-USECASE"): self.assertEqual(v[rid]["verdict"], "NOT_APPLICABLE", rid)
    def test_missing_keywords_never_fail(self):
        v, _ = V("subscription")
        for rid in ("CUR-APL-3.1.1-IAP", "CUR-APL-3.1.2c-INFO", "CUR-GPL-SUBS"): self.assertEqual(v[rid]["verdict"], "NEEDS_REVIEW", rid)
        v, _ = V("ai-client")
        for rid in ("CUR-APL-5.1.2i-AI", "CUR-GPL-AI-REPORT"): self.assertEqual(v[rid]["verdict"], "NEEDS_REVIEW", rid)
        self.assertTrue(any("not found by keyword" in e for e in v["CUR-APL-5.1.2i-AI"]["evidence"]))
    def test_exact_alarm_never_auto_fail(self):
        for fx in ("alarm-app", "reminder-exact"):
            v, _ = V(fx); self.assertEqual(v["CUR-GPL-EXACT-ALARM"]["verdict"], "NEEDS_REVIEW", fx)
        v, _ = V("alarm-app"); self.assertTrue(any("alarm/calendar signal in app metadata" in e for e in v["CUR-GPL-EXACT-ALARM"]["evidence"]))
        v, _ = V("reminder-exact"); self.assertTrue(any("no alarm/calendar signal" in e for e in v["CUR-GPL-EXACT-ALARM"]["evidence"]))

class Health(unittest.TestCase):
    def test_health_good(self):
        v, a = V("health-good"); self.assertEqual(a["counts"]["FAIL"], 0)
        self.assertEqual(v["CUR-APL-MIC"]["verdict"], "PASS"); self.assertEqual(v["CUR-APL-HK-USAGE"]["verdict"], "NEEDS_REVIEW")
        self.assertEqual(v["CUR-GPL-HEALTH-DISCLAIMER"]["verdict"], "NEEDS_REVIEW")
    def test_declared_false_is_definite_na(self):
        v, _ = V("health-good", declared={"regulated_medical_device": False})
        self.assertEqual(v["CUR-GPL-HEALTH-MEDDEV"]["verdict"], "NOT_APPLICABLE"); self.assertTrue(v["CUR-GPL-HEALTH-MEDDEV"]["applicability"]["definite"])
        v, _ = V("health-good"); self.assertEqual(v["CUR-GPL-HEALTH-MEDDEV"]["verdict"], "NEEDS_REVIEW")

class AI(unittest.TestCase):
    def test_backend_only_ai_detected(self):
        v, a = V("backend-ai"); self.assertEqual(a["features"]["ai"]["state"], "DETECTED"); self.assertTrue(any("[backend convex]" in e for e in a["features"]["ai"]["evidence"]))
        self.assertEqual(v["CUR-APL-5.1.2i-AI"]["verdict"], "NEEDS_REVIEW")
    def test_secret_redacted(self):
        blob = json.dumps(run("ai-client")); self.assertNotIn("sk-proj-abcdefghijklmnopqrstuvwxyz0123456789", blob)
        self.assertEqual(redact('OPENAI_API_KEY = "sk-proj-abcdefghijklmnopqrstuvwxyz0123"'), 'OPENAI_API_KEY = "[REDACTED]"')
        self.assertIn("[REDACTED:revenuecat-key]", redact("const k = appl_AbCdEfGhIjKlMnOpQrSt;"))

class Discovery(unittest.TestCase):
    def test_frameworks(self):
        exp = {"simple-clean": "expo-managed", "rn-bare": "react-native", "native-android": "android-native", "flutter-app": "flutter", "dynamic-config": "expo-managed"}
        for fx, fw in exp.items(): self.assertEqual(discover(FX / fx)["apps"][0]["framework"], fw, fx)
    def test_monorepo(self):
        d = discover(FX / "monorepo"); self.assertTrue(d["monorepo"]); self.assertEqual([str(Path(a["path"]).relative_to(FX / "monorepo")) for a in d["apps"]], ["apps/mobile"])
    def test_dynamic_config_unresolved_not_missing(self):
        v, a = V("dynamic-config"); self.assertEqual(a["config"]["state"], "dynamic-unresolved")
        self.assertEqual(v["CUR-APL-MIC"]["verdict"], "NEEDS_REVIEW"); self.assertEqual(a["counts"]["FAIL"], 0)
        self.assertEqual(a["features"]["exact_alarm"]["state"], "UNRESOLVED")
    def test_unsupported_stack_not_checked(self):
        a = run("flutter-app")["apps"][0]; self.assertEqual(a["counts"]["NOT_CHECKED"], len(engine.load_rules()))
    def test_paths_safe(self):
        with self.assertRaises(PathError): resolve_project("/")
        with self.assertRaises(PathError): resolve_project("/does/not/exist")
        with self.assertRaises(PathError): resolve_project(str(FX / "simple-clean" / "app.json"))
        with self.assertRaises(PathError): resolve_project(str(FX / "simple-clean"), allowed_roots=["/nonexistent-root"])
        with tempfile.TemporaryDirectory() as t:
            shutil.copytree(FX / "simple-clean", Path(t) / "app"); os.symlink("/etc", Path(t) / "app" / "app" / "etc-link")
            secret = Path(tempfile.mkdtemp()) / "leak.ts"; secret.write_text("export const x = 'patient diagnosis kidney';"); os.symlink(secret, Path(t) / "app" / "app" / "leak.ts")
            a = engine.check_project(str(Path(t) / "app"), greenlight="off")["apps"][0]
            self.assertEqual(a["coverage"]["skipped_escaping_symlinks"], 1); self.assertNotIn("leak.ts", json.dumps(a))

class Greenlight(unittest.TestCase):
    @unittest.skipUnless(__import__("compliance_mcp.greenlight", fromlist=["x"]).locate(), "greenlight not installed")
    def test_offline_json_and_disagreement(self):
        res = engine.check_project(str(FX / "health-good"), greenlight="auto"); a = res["apps"][0]
        self.assertEqual(a["coverage"]["greenlight"]["status"], "ok"); self.assertIn("0.2.0", a["coverage"]["greenlight"]["version"])
        self.assertNotIn("PASS", [v["verdict"] for v in a["verdicts"] if v.get("greenlight")])

class CLI(unittest.TestCase):
    def cli(self, *args):
        return subprocess.run([sys.executable, "-m", "compliance_mcp.cli", *args], capture_output=True, text=True, cwd="/", env={**os.environ, "PYTHONPATH": str(SRV)})
    def test_exit_codes(self):
        self.assertEqual(self.cli("check", str(FX / "health-bad"), "--greenlight", "off").returncode, 1)
        self.assertEqual(self.cli("check", str(FX / "simple-clean"), "--greenlight", "off").returncode, 0)
        self.assertEqual(self.cli("check", str(FX / "simple-clean"), "--greenlight", "off", "--fail-on-review").returncode, 4)
        self.assertEqual(self.cli("check", "/no/such/dir").returncode, 2)
        self.assertEqual(self.cli("check", str(FX / "simple-clean"), "--declare", "bad").returncode, 2)
        self.assertEqual(self.cli("bogus").returncode, 2)
    def test_report_has_snapshot_and_limits(self):
        out = self.cli("check", str(FX / "health-bad"), "--greenlight", "off").stdout
        self.assertIn("rules snapshot 2026-10-10", out); self.assertIn("## Limits", out); self.assertIn("https://developer.apple.com", out)

def _server_cmd():
    b = shutil.which("mcc-mcp")
    return ([b], {}) if b else ([sys.executable, "-m", "compliance_mcp.server"], {"PYTHONPATH": str(SRV)})

class MCPRaw(unittest.TestCase):
    def test_malformed_input_survives(self):
        cmd, env = _server_cmd()
        lines = ["{not json", "[1,2,3]", "42", json.dumps({"jsonrpc": "2.0", "id": 1}), json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": "x"}),
                 json.dumps({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "nope"}}),
                 json.dumps({"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "check_project", "arguments": {"project_path": 5}}}),
                 json.dumps({"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "check_project", "arguments": {"project_path": "/", "evil": 1}}}),
                 json.dumps({"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {"name": "check_project", "arguments": {"project_path": "/"}}}),
                 json.dumps({"jsonrpc": "2.0", "method": "unknown/notification"}), json.dumps({"jsonrpc": "2.0", "id": 7, "method": "nope"}),
                 "[" * 100000, json.dumps({"jsonrpc": "2.0", "id": 8, "method": "ping"})]
        p = subprocess.run(cmd, input="\n".join(lines) + "\n", capture_output=True, text=True, cwd="/", env={**os.environ, **env}, timeout=60)
        r = [json.loads(l) for l in p.stdout.splitlines()]
        codes = [x.get("error", {}).get("code") if "error" in x else ("isError" if x["result"].get("isError") else "ok") for x in r]
        self.assertEqual(codes, [-32700, -32600, -32600, -32600, -32602, -32602, "isError", "isError", "isError", -32601, -32700, "ok"])

try: from mcp import ClientSession as _CS; import mcp  # noqa  (a bare namespace dir named 'mcp' on sys.path must not count)
except ImportError: mcp = None
@unittest.skipUnless(mcp, "real MCP client (pip install 'mcp<2') not available")
class MCPRealClient(unittest.TestCase):
    def test_real_client_session(self):
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        cmd, env = _server_cmd()
        async def go():
            params = StdioServerParameters(command=cmd[0], args=cmd[1:], env={**os.environ, **env}, cwd="/")
            async with stdio_client(params) as (r, w):
                async with ClientSession(r, w) as s:
                    init = await s.initialize(); tools = await s.list_tools()
                    snap = await s.call_tool("snapshot_info", {})
                    chk = await s.call_tool("check_project", {"project_path": str(FX / "health-bad"), "greenlight": "off", "rule_ids": ["CUR-APL-MIC"]})
                    bad = await s.call_tool("get_rule", {"rule_id": "NOPE"})
                    bad2 = await s.call_tool("check_project", {"project_path": "/does/not/exist"})
                    ping = await s.send_ping()
                    return init, tools, snap, chk, bad, bad2
        init, tools, snap, chk, bad, bad2 = asyncio.run(go())
        self.assertEqual(init.serverInfo.name, "mobile-compliance-checker")
        self.assertEqual({t.name for t in tools.tools}, {"snapshot_info", "list_rules", "get_rule", "list_deprecated", "discover_apps", "check_project"})
        from collections import Counter
        self.assertEqual(json.loads(snap.content[0].text)["by_platform"], dict(Counter(r["platform"] for r in engine.load_rules())))
        self.assertEqual(json.loads(chk.content[0].text)["apps"][0]["verdicts"][0]["verdict"], "FAIL")
        self.assertTrue(bad.isError); self.assertTrue(bad2.isError)

def _tmp_app(name, deps=None, code=None, features=None):
    d = Path(tempfile.mkdtemp(prefix="cops004-")); (d / "app.json").write_text(json.dumps({"expo": {"name": name, "slug": name.lower().replace(" ", "-"), "ios": {"bundleIdentifier": "x.y"}, "android": {"package": "x.y"}}}))
    (d / "package.json").write_text(json.dumps({"name": "t", "dependencies": {"expo": "~54.0.0", "react-native": "0.81.0", **(deps or {})}}))
    (d / "App.tsx").write_text(code or "export default function App() { return null; }\n")
    if features: (d / ".compliance").mkdir(); (d / ".compliance" / "features.json").write_text(json.dumps(features))
    return d

class CoverageGates004(unittest.TestCase):
    """New verified rule families (COMPLIANCE-OPERATIONS-004): gated, never FAIL/PASS without evidence."""
    def vv(self, d):
        r = engine.check_project(str(d), greenlight="off"); shutil.rmtree(d, ignore_errors=True)
        return {v["rule_id"]: v for v in r["apps"][0]["verdicts"]}
    NEW = ("CUR-APL-1.2-UGC", "CUR-GPL-UGC", "CUR-APL-1.1.1-RELIGION", "CUR-GPL-HATE-RELIGION", "CUR-APL-1.3-KIDS", "CUR-APL-5.1.4-KIDS", "CUR-GPL-FAMILIES",
           "CUR-APL-2.5.18-ADS", "CUR-GPL-ADS-RATING", "CUR-APL-3.1.1-LOOTBOX", "CUR-GPL-LOOTBOX", "CUR-APL-3.1.3e-GOODS", "CUR-GPL-PHYSICAL-GOODS",
           "CUR-APL-3.1.3a-READER", "CUR-APL-5.3.3-RMG", "CUR-GPL-RMG", "CUR-APL-4.7-CHATBOT", "CUR-GPL-SENSITIVE-SECURE")
    def test_plain_app_new_rules_not_applicable_nondefinite(self):
        v = self.vv(_tmp_app("Tile Notes"))
        for r in self.NEW:
            self.assertEqual(v[r]["verdict"], "NOT_APPLICABLE", r); self.assertFalse(v[r]["applicability"]["definite"], r)
    def test_signals_trigger_needs_review_not_fail(self):
        code = "export function A(){ createPost(); blockUser(); openLootBox(); }\n"
        v = self.vv(_tmp_app("Kids Bible Stories", deps={"react-native-google-mobile-ads": "^15.0.0"}, code=code))
        for r in ("CUR-APL-1.2-UGC", "CUR-GPL-UGC", "CUR-APL-1.1.1-RELIGION", "CUR-GPL-HATE-RELIGION", "CUR-APL-1.3-KIDS", "CUR-APL-5.1.4-KIDS",
                  "CUR-GPL-FAMILIES", "CUR-APL-2.5.18-ADS", "CUR-GPL-ADS-RATING", "CUR-APL-3.1.1-LOOTBOX", "CUR-GPL-LOOTBOX"):
            self.assertEqual(v[r]["verdict"], "NEEDS_REVIEW", r)
    def test_physical_goods_exception_requires_declaration(self):
        code = "import { Linking } from 'react-native'; export const go = () => Linking.openURL('https://buy.stripe.com/abc');\n"
        v = self.vv(_tmp_app("Shop", code=code))
        self.assertEqual(v["CUR-APL-3.1.3e-GOODS"]["verdict"], "NEEDS_REVIEW"); self.assertIn("unresolved", v["CUR-APL-3.1.3e-GOODS"]["reason"])
        v = self.vv(_tmp_app("Shop", code=code, features={"physical_goods": False, "reader_content": False}))
        for r in ("CUR-APL-3.1.3e-GOODS", "CUR-GPL-PHYSICAL-GOODS", "CUR-APL-3.1.3a-READER"):
            self.assertEqual(v[r]["verdict"], "NOT_APPLICABLE"); self.assertTrue(v[r]["applicability"]["definite"])
    def test_every_new_rule_has_verified_quote_and_url(self):
        rules = {r["rule_id"]: r for r in engine.load_rules()}
        for r in self.NEW:
            self.assertTrue(rules[r]["official_quotes"] and rules[r]["official_url"].startswith("https://"), r)
            self.assertEqual(rules[r]["verified_date"], "2026-10-10")

if __name__ == "__main__": unittest.main()

class GreenlightIsolation(unittest.TestCase):
    def test_refuses_without_unshare(self):
        from unittest import mock
        from compliance_mcp import greenlight as G
        with mock.patch.object(G, "locate", return_value="/bin/true"), mock.patch.object(G.shutil, "which", return_value=None), \
             mock.patch.object(G.subprocess, "run", return_value=mock.Mock(stdout="greenlight 0.2.0", returncode=0)):
            self.assertEqual(G.run(str(FX / "simple-clean"))["status"], "refused-no-network-isolation")

class V03CodePaths(unittest.TestCase):
    def test_deletion_data_only_is_flagged_not_failed(self):
        v, a = V("deletion-data-only"); d = a["trace"]["account_deletion"]
        self.assertEqual(d["classification"], "UI_TO_BACKEND_DATA_DELETION_ONLY")
        self.assertTrue(any("convex/workspaces.ts:4" in o for o in d["chains"][0]["delete_ops"]))
        self.assertEqual(v["CUR-APL-5.1.1v-ACCDEL"]["verdict"], "NEEDS_REVIEW"); self.assertIn("NO login-identity deletion", v["CUR-APL-5.1.1v-ACCDEL"]["reason"])
        self.assertEqual(v["CUR-APL-5.1.1v-ACCDEL"]["evidence_type"], "code-path")
    def test_deletion_identity_chain_multi_hop_not_pass(self):
        v, a = V("deletion-identity"); d = a["trace"]["account_deletion"]
        self.assertEqual(d["classification"], "UI_TO_BACKEND_IDENTITY_DELETION")
        c = [c for c in d["chains"] if c["identity_deletion"]][0]
        self.assertIn("supabase/functions/delete-account/index.ts:4", c["identity_deletion"][0])
        self.assertEqual(v["CUR-APL-5.1.1v-ACCDEL"]["verdict"], "NEEDS_REVIEW")   # code path != functional PASS
    def test_external_checkout_gating(self):
        v, a = V("checkout-native"); self.assertEqual(a["trace"]["billing"]["classification"], "EXTERNAL_CHECKOUT_REACHABLE_IN_NATIVE")
        self.assertEqual(a["features"]["iap"]["state"], "DETECTED"); self.assertEqual(v["CUR-APL-3.1.1-IAP"]["verdict"], "NEEDS_REVIEW")
        _, a = V("checkout-indirect"); self.assertEqual(a["trace"]["billing"]["classification"], "EXTERNAL_CHECKOUT_REACHABLE_IN_NATIVE")
        _, a = V("checkout-webgated"); self.assertEqual(a["trace"]["billing"]["classification"], "EXTERNAL_CHECKOUT_WEB_GATED")
        self.assertTrue(a["trace"]["billing"]["native_purchase_calls"])
    def test_vet_human_medical_is_judgment_general_rules_kept(self):
        v, a = V("vet-app"); self.assertEqual(a["features"]["veterinary"]["state"], "DETECTED")
        self.assertEqual(v["CUR-GPL-HEALTH-DISCLAIMER"]["evidence_category"], "JUDGMENT"); self.assertIn("veterinary", v["CUR-GPL-HEALTH-DISCLAIMER"]["reason"])
        self.assertEqual(v["CUR-GPL-HEALTH-MISINFO"]["verdict"], "NEEDS_REVIEW"); self.assertNotIn("veterinary", v["CUR-GPL-HEALTH-MISINFO"]["reason"])
        self.assertEqual(v["CUR-APL-5.1.1i-PRIVACY"]["verdict"], "NEEDS_REVIEW")
        v, _ = V("vet-app", declared={"human_health": False}); self.assertEqual(v["CUR-GPL-HEALTH-DISCLAIMER"]["verdict"], "NOT_APPLICABLE")
    def test_dynamic_literal_read_not_executed(self):
        v, a = V("dynamic-literal"); m = v["CUR-APL-MIC"]
        self.assertEqual(m["verdict"], "NEEDS_REVIEW"); self.assertTrue(any("literal NSMicrophoneUsageDescription found in app.config.ts:4" in e for e in m["evidence"]))
        self.assertTrue(any("NSCameraUsageDescription" in x for x in a["dynamic_config_literals"]["env_dependent_keys"]))
        self.assertEqual(m["evidence_category"], "UNRESOLVED_CONFIG")
    def test_derived_vendor_default_never_pass(self):
        v, a = V("derived-default"); t = v["CUR-GPL-TAPI-NEW"]
        self.assertEqual(a["derived_config"]["targetSdkVersion"], 36); self.assertEqual(t["verdict"], "NEEDS_REVIEW")
        self.assertEqual(t["verification_level"], "derived-vendor-default"); self.assertEqual(t["evidence_category"], "ARTIFACT")
    def test_ai_boundary_chain(self):
        v, a = V("ai-boundary"); b = a["trace"]["ai_boundary"][0]
        self.assertEqual(b["side"], "backend"); self.assertTrue(b["enclosing_export"].startswith("askCoach @ convex/coach.ts:2"))
        self.assertTrue(any("coach.tsx" in r for r in b["client_refs"])); self.assertIn("aiConsentGiven", b["consent_identifiers_in_callers"])
        self.assertIn("glucose", b["health_terms_in_request_scope"]); self.assertEqual(v["CUR-APL-5.1.2i-AI"]["verdict"], "NEEDS_REVIEW")
    def test_taxonomy_hc_limited_not_spam(self):
        r = {x["rule_id"]: x for x in engine.load_rules()}
        self.assertEqual(r["CUR-GPL-HC-LIMITED"]["family"], "health-data"); self.assertEqual(r["CUR-GPL-LIMITED"]["family"], "content-integrity")
        self.assertTrue(all(x.get("evidence_category") in ("SOURCE", "ARTIFACT", "STORE", "JUDGMENT") for x in r.values()))

def _store_app(store=None, deps=None, ios=None, eas=None, files=None):
    d = Path(tempfile.mkdtemp(prefix="vstore-"))
    (d / "app.json").write_text(json.dumps({"expo": {"name": "Note Box", "slug": "note-box", "ios": {"bundleIdentifier": "x.y", **(ios if ios is not None else {"config": {"usesNonExemptEncryption": False}})}, "android": {"package": "x.y"}}}))
    (d / "package.json").write_text(json.dumps({"name": "t", "dependencies": {"expo": "~54.0.0", "react-native": "0.81.0", **(deps or {})}}))
    (d / "App.tsx").write_text("export default function App() { return null; }\n")
    if store is not None: (d / ".compliance").mkdir(); (d / ".compliance" / "store.json").write_text(json.dumps(store))
    if eas: (d / "eas.json").write_text(json.dumps(eas))
    for k, v in (files or {}).items(): p = d / k; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(v if isinstance(v, bytes) else v.encode())
    return d
def _findings(d, **kw):
    try: return {f["check"]: f for f in engine.check_project(str(d), greenlight="off", **kw)["findings"]}
    finally: shutil.rmtree(d, ignore_errors=True)

class VerifiedOnly(unittest.TestCase):
    """Rule 1: only verified issues are user-facing; missing data -> nothing emitted."""
    def test_no_data_emits_nothing(self):
        self.assertEqual(_findings(_store_app()), {})
    def test_findings_have_evidence_and_apple_url(self):
        d = _store_app(store={"age_rating": {"questionnaire_completed": False}}, ios={})
        for f in _findings(d).values():
            self.assertTrue(f["evidence"]); self.assertTrue(f["official_url"].startswith("https://developer.apple.com/"))
    def test_report_drops_unverified(self):
        out = report_md("subscription")
        self.assertNotIn("NEEDS_REVIEW", out); self.assertNotIn("NOT_APPLICABLE", out); self.assertIn("No verified issues found", out)
        self.assertIn("CUR-APL-MIC", report_md("health-bad"))
    def test_mcp_boundary_drops_unverified(self):
        from compliance_mcp.server import call
        r = call("check_project", {"project_path": str(FX / "subscription"), "greenlight": "off"})
        self.assertTrue(all(v["verdict"] in ("FAIL", "PASS") for a in r["apps"] for v in a["verdicts"])); self.assertIn("HARD RULE", r["output_policy"])
def report_md(fx):
    from compliance_mcp import report
    return report.markdown(engine.check_project(str(FX / fx), greenlight="off"))

class NewAppleChecks(unittest.TestCase):
    def test_a_sdk_without_privacy_manifest(self):
        f = _findings(_store_app(deps={"@react-native-firebase/messaging": "^21"}, files={"node_modules/@react-native-firebase/messaging/package.json": "{}"}))
        self.assertIn("sdk_missing_privacy_manifest", f)
        f = _findings(_store_app(deps={"@react-native-firebase/messaging": "^21"}, files={"node_modules/@react-native-firebase/messaging/ios/PrivacyInfo.xcprivacy": "<plist/>"}))
        self.assertNotIn("sdk_missing_privacy_manifest", f)
        self.assertNotIn("sdk_missing_privacy_manifest", _findings(_store_app(deps={"@react-native-firebase/messaging": "^21"})))  # not installed -> unverifiable
    def test_b_old_xcode_image_and_ipa(self):
        self.assertIn("build_sdk_too_old", _findings(_store_app(eas={"build": {"production": {"ios": {"image": "macos-sequoia-15.3-xcode-16.2"}}}})))
        self.assertNotIn("build_sdk_too_old", _findings(_store_app(eas={"build": {"production": {"ios": {"image": "latest"}}}})))
        import plistlib, zipfile
        d = _store_app(); ipa = d / "a.ipa"
        with zipfile.ZipFile(ipa, "w") as z: z.writestr("Payload/A.app/Info.plist", plistlib.dumps({"DTXcode": "1620", "DTSDKName": "iphoneos18.2", "MinimumOSVersion": "12.4", "ITSAppUsesNonExemptEncryption": False}))
        f = {x["check"] for x in engine.check_project(str(d), greenlight="off", ipa=str(ipa))["findings"]}; shutil.rmtree(d, ignore_errors=True)
        self.assertTrue({"build_sdk_too_old", "deployment_target_below_ios13"} <= f)
    def test_c_missing_encryption_key(self):
        self.assertIn("missing_encryption_declaration", _findings(_store_app(ios={})))
        self.assertNotIn("missing_encryption_declaration", _findings(_store_app(ios={"infoPlist": {"ITSAppUsesNonExemptEncryption": False}})))
    def test_d_subscription_without_terms(self):
        subs = [{"product_id": "pro.monthly", "type": "auto_renewable"}]
        self.assertIn("subscription_missing_terms_link", _findings(_store_app(store={"in_app_purchases": subs, "listing": {"description": "Great app."}})))
        self.assertNotIn("subscription_missing_terms_link", _findings(_store_app(store={"in_app_purchases": subs, "listing": {"terms_of_use_url": "https://x.y/terms"}})))
        self.assertNotIn("subscription_missing_terms_link", _findings(_store_app(store={"in_app_purchases": subs})))  # no listing data
    def test_f_age_rating(self):
        self.assertIn("age_rating_unanswered", _findings(_store_app(store={"age_rating": {"questionnaire_completed": False}})))
        self.assertNotIn("age_rating_unanswered", _findings(_store_app(store={"age_rating": {"questionnaire_completed": True}})))
    def test_g_iphone_screenshot_in_ipad_slot(self):
        png = lambda w, h: b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + struct_pack(w, h) + b"\x08\x02\x00\x00\x00"
        f = _findings(_store_app(store={"screenshots": [{"slot": "ipad_13", "path": "shots/1.png"}]}, files={"shots/1.png": png(1320, 2868)}))
        self.assertIn("iphone_screenshot_in_ipad_slot", f)
        self.assertNotIn("iphone_screenshot_in_ipad_slot", _findings(_store_app(store={"screenshots": [{"slot": "ipad_13", "width": 2064, "height": 2752}]})))
def struct_pack(w, h):
    import struct; return struct.pack(">II", w, h)
