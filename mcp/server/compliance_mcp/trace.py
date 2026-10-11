"""v0.3 code-path tracing across app + backend + shared monorepo code (read-only, static, no execution).
Produces identifiable code paths (file:line steps). A found path is evidence, NEVER a functional PASS."""
import re
from pathlib import Path
from .safety import redact, NON_APP_PARTS

JS = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
DEF_RX = re.compile(r"^\s*export\s+(?:default\s+)?(?:const|let|async\s+function|function)\s+(\w+)")
LOCAL_DEF_RX = re.compile(r"^\s*(?:export\s+)?(?:(?:const|let|async\s+function|function)\s+(\w+)\s*(?:=|\()|(?:async\s+)?(?!if\b|for\b|while\b|switch\b|catch\b|return\b)(\w+)\s*\([^)]*\)\s*(?::\s*[^{=]+)?\{)")
CALL_RX = re.compile(r"\b([a-zA-Z_]\w{2,})\s*\(")
REF_RXS = [re.compile(r"""makeFunctionReference<[^>]*>\(\s*['"]([\w/]+):(\w+)['"]"""), re.compile(r"\b(?:api|internal|anyApi)\.([\w.]+)\.(\w+)\b"),
           re.compile(r"""['"]([\w/]+):(\w+)['"]""")]
INVOKE_RX = re.compile(r"""(?:functions\.invoke|invoke\w*|callEdge\w*|edgeFunction\w*)\(\s*['"]([\w-]+)['"]|/functions/v1/([\w-]+)|['"]([a-z0-9]+(?:-[a-z0-9]+)+)['"]""")
class Idx:
    def __init__(self, ctx):
        self.ctx = ctx; self.repo = ctx.repo; self.files = {}
        trees = [ctx.tree] + list(ctx.backend)
        for t in trees:
            for f in t.files:
                if f.suffix not in JS or "_generated" in f.parts: continue
                rel = f.relative_to(t.root).parts
                if any(x in NON_APP_PARTS for x in rel[:-1]) or ".test." in f.name or ".spec." in f.name or f.name.startswith(("jest.", "vitest.")): continue
                self.files[f] = t.text(f).splitlines()
        self.files = {f: L for f, L in self.files.items() if not re.search(r"smoke|replay|fixture|seed|e2e|acceptance", f.name, re.I)}
        from .context import BACKEND_DIRS
        def _is_backend(f):
            try: first = f.relative_to(ctx.root).parts[0]
            except ValueError: return True
            return first in BACKEND_DIRS and first not in ("services",)   # app-root-level convex/, supabase/, server/ are backend
        self.app = {f for f in self.files if ctx.root in f.parents and not _is_backend(f)}
        self.defs = {}
        for f, L in self.files.items():
            for i, l in enumerate(L, 1):
                m = LOCAL_DEF_RX.match(l)
                if m: self.defs.setdefault(m.group(1) or m.group(2), []).append((f, i))
        self.edge = {}
        for f in self.files:
            p = f.parts
            if "functions" in p and f.name in ("index.ts", "index.js") and "supabase" in p: self.edge[p[p.index("functions") + 1]] = f
    def loc(self, f, i):
        try: r = f.relative_to(self.repo)
        except ValueError: r = f
        return f"{r}:{i}"
    def line(self, f, i): return redact(self.files[f][i - 1].strip()[:150])
    def region(self, f, i, maxl=220):
        L = self.files[f]; end = min(len(L), i + maxl)
        for j in range(i, end):
            if j > i and DEF_RX.match(L[j]): end = j; break
        return range(i, end + 1)
    def imports(self, f):
        return {Path(m).stem for m in re.findall(r"""(?:from|import)\s*\(?\s*['"]([^'"]+)['"]""", "\n".join(self.files[f][:80]))}
    def rest_target(self, path):
        for f in self.files:
            if f in self.app: continue
            for i, l in enumerate(self.files[f], 1):
                if path in l and not l.lstrip().startswith(("//", "*")): return f, i
        return None
    def module_of(self, f):
        p = f.parts
        if "convex" in p: return "/".join(p[p.index("convex") + 1:])[: -len(f.suffix)]
        return None
    def backend_def(self, module, name):
        for f, i in self.defs.get(name, []):
            if f in self.app: continue
            mod = self.module_of(f)
            if mod is None or mod == module.replace(".", "/") or module.endswith(mod): return f, i
        return None
    def refs_in(self, f, rng):
        out = []
        for i in rng:
            l = self.files[f][i - 1]
            for rx in REF_RXS:
                for m in rx.finditer(l):
                    out.append(("convex", m.group(1), m.group(2), i))
            for m in re.finditer(r"""['"`](/(?:v\d+|api)/[\w/-]+)""", l):
                out.append(("rest", m.group(1), None, i))
            for m in INVOKE_RX.finditer(l):
                n = m.group(1) or m.group(2) or m.group(3)
                if n in self.edge: out.append(("edge", n, None, i))
        return out

def _resolve(ix, kind, mod, name):
    if kind == "convex": return ix.backend_def(mod, name)
    if kind == "edge": return (ix.edge[mod], 1) if mod in ix.edge else None
    if kind == "rest": return ix.rest_target(mod)

def _follow(ix, start, ops_rx, ident_rx, depth=3):
    """From a backend def, follow internal/api refs + scheduler calls; collect matching op lines."""
    seen, steps, ops, ident = set(), [], [], []
    stack = [(start, 0)]
    while stack:
        (f, i), d = stack.pop()
        if (f, i) in seen or d > depth: continue
        seen.add((f, i)); rng = range(i, min(len(ix.files[f]), i + 3) + 1) if not DEF_RX.match(ix.files[f][i - 1]) and not LOCAL_DEF_RX.match(ix.files[f][i - 1]) and i > 1 else ix.region(f, i) if not (f.name.startswith("index.") and "functions" in f.parts) else range(1, len(ix.files[f]) + 1)
        steps.append(f"{ix.loc(f, i)} {ix.line(f, i)[:90]}")
        for j in rng:
            l = ix.files[f][j - 1]
            if ops_rx.search(l): ops.append(f"{ix.loc(f, j)} {ix.line(f, j)[:110]}")
            if ident_rx.search(l): ident.append(f"{ix.loc(f, j)} {ix.line(f, j)[:110]}")
        for kind, mod, name, j in ix.refs_in(f, rng):
            t = _resolve(ix, kind, mod, name)
            if t: stack.append((t, d + 1))
        for m in CALL_RX.finditer(" ".join(ix.files[f][j - 1] for j in rng)):
            for (g, k) in ix.defs.get(m.group(1), [])[:2]:
                if g not in ix.app and not (g == f and k in rng) and (g == f or g.stem in ix.imports(f)): stack.append(((g, k), d + 1))
    return steps, ops, ident

def _enclosing(ix, f, i):
    for k in range(i, 0, -1):
        if LOCAL_DEF_RX.match(ix.files[f][k - 1]): return k
    return max(1, i - 10)

def _client_chain(ix, f, i, depth=3):
    """From a UI line: the enclosing handler/function, then up to `depth` hops through local helper functions,
    collecting backend references (Convex function refs, Supabase edge-function invokes). Returns [(file, ref, path)]."""
    hits, seen = [], set()
    stack = [((f, _enclosing(ix, f, i)), 0, [f"{ix.loc(f, i)}"])]
    while stack:
        (g, k), d, path = stack.pop()
        if (g, k) in seen or d > depth: continue
        seen.add((g, k)); rng = ix.region(g, k, 60)
        hits += [(g, r, path) for r in ix.refs_in(g, rng)]
        text = " ".join(ix.files[g][j - 1] for j in rng)
        for m in CALL_RX.finditer(text):
            for (h, q) in ix.defs.get(m.group(1), [])[:3]:
                if h in ix.app and (h, q) not in seen: stack.append(((h, q), d + 1, path + [f"{ix.loc(h, q)} {m.group(1)}()"]))
        for tok in set(re.findall(r"\b[a-zA-Z_]\w{3,}\b", text)):   # same-file consts, e.g. useMutation(ref) -> ref = makeFunctionReference(...)
            for (h, q) in ix.defs.get(tok, [])[:2]:
                if h == g and (h, q) not in seen and q not in rng: stack.append(((h, q), d + 1, path + [f"{ix.loc(h, q)} {tok}"]))
    return hits

DEL_UI = re.compile(r"(delete|erase|close|remove|wipe)\s*(my\s*|your\s*|remote\s*|cloud\s*)?(account|profile|workspace|all (my |your )?data|everything|user data)|delete(My)?Account|deleteRemoteWorkspace|delete_account|requestAccountDeletion|deleteUserData", re.I)
DEL_OPS = re.compile(r"DELETE FROM|ctx\.db\.delete\(|\.delete\(\)|auth\.admin\.deleteUser|deleteUser\(|DELETE FROM|\.remove\(")
IDENT = re.compile(r"auth\.admin\.deleteUser|deleteUser\(|authAccounts|authSessions|authRefreshTokens|db\.delete\(\s*(args\.)?user(Id)?\b|db\.delete\(\s*user\._id|from\(['\"](users|profiles|accounts)['\"]\)\s*\.delete|delete from (auth\.)?(users|app_user|accounts?|players?|profiles)\b|\.delete\(\s*identity", re.I)

def account_deletion(ix):
    seeds = [(f, i) for f in ix.app for i, l in enumerate(ix.files[f], 1) if DEL_UI.search(l)]
    chains = []
    for f, i in sorted(seeds, key=lambda x: not re.search(r'account', ix.files[x[0]][x[1]-1], re.I))[:16]:
        entry = _client_chain(ix, f, i)
        for (g, (kind, mod, name, j), path) in entry[:20]:
            if kind == "rest" and not re.search(r"DELETE|delete|remove|erase", " ".join(ix.files[g][max(0, j - 2):j + 1])): continue
            t = _resolve(ix, kind, mod, name)
            if not t: continue
            steps, ops, ident = _follow(ix, t, DEL_OPS, IDENT)
            if not ops and not ident: continue   # backend entry unrelated to deletion (e.g. a shared function-name map)
            chains.append({"ui": f"{ix.loc(f, i)} {ix.line(f, i)[:100]}", "client_path": path, "client_call": f"{ix.loc(g, j)} {ix.line(g, j)[:100]}",
                           "backend": steps[:6], "delete_ops": ops[:6], "identity_deletion": ident[:4]})
    uniq = {}
    for c in sorted(chains, key=lambda c: -len(c["identity_deletion"])): uniq.setdefault(c["backend"][0], c)
    chains = list(uniq.values())
    any_ident = [f"{ix.loc(f, i)} {ix.line(f, i)[:100]}" for f in ix.files if f not in ix.app for i, l in enumerate(ix.files[f], 1) if IDENT.search(l)][:5]
    if any(c["identity_deletion"] for c in chains): cls = "UI_TO_BACKEND_IDENTITY_DELETION"
    elif chains: cls = "UI_TO_BACKEND_DATA_DELETION_ONLY"
    elif seeds: cls = "UI_ONLY_OR_LOCAL_DELETION"
    elif any_ident: cls = "BACKEND_IDENTITY_DELETION_WITHOUT_UI_PATH"
    else: cls = "NO_DELETION_PATH_FOUND"
    return {"classification": cls, "chains_with_identity_deletion": sum(1 for c in chains if c["identity_deletion"]),
            "chains_data_only": sum(1 for c in chains if not c["identity_deletion"]), "ui_seeds": [f"{ix.loc(f, i)} {ix.line(f, i)[:100]}" for f, i in seeds[:6]], "chains": chains[:4], "backend_identity_deletion_anywhere": any_ident}

URL_RX = re.compile(r"https?://[^\s'\"`)<>]+")
def privacy_links(ix):
    out = []
    for f in ix.app:
        for i, l in enumerate(ix.files[f], 1):
            for u in URL_RX.findall(l):
                if re.search(r"privacy|terms|eula|legal", u, re.I):
                    out.append({"url": u, "at": ix.loc(f, i), "opened_via": bool(re.search(r"openURL|openBrowserAsync|href|Link|WebBrowser", l)),
                                "placeholder": bool(re.search(r"example\.(com|org)|localhost|placeholder|your-?domain|TODO", u, re.I))})
    screens = [ix.loc(f, 1) for f in ix.app if re.search(r"privacy|legal|terms", f.name, re.I)]
    mentions = [f"{ix.loc(f, i)} {ix.line(f, i)[:90]}" for f in ix.app for i, l in enumerate(ix.files[f], 1) if re.search(r"privacy", l, re.I)][:5]
    nav = [f"{ix.loc(f, i)} {ix.line(f, i)[:90]}" for f in ix.app for i, l in enumerate(ix.files[f], 1) if re.search(r"""(push|navigate|href|replace)\W{1,3}['"`]?/?(\(\w+\)/)?(privacy|legal)""", l, re.I)][:5]
    cls = "EXTERNAL_PRIVACY_URL" if out else "IN_APP_PRIVACY_SCREEN" if screens or nav else "PRIVACY_TEXT_ONLY" if mentions else "NO_PRIVACY_POLICY_PATH_FOUND"
    return {"classification": cls, "urls": out[:10], "in_app_screens": screens[:6], "navigation_to_privacy": nav, "privacy_mentions": mentions, "app_config_privacy_keys": [k for k in ("privacyPolicyUrl", "privacy") if k in ix.ctx.expo]}

AI_CALL = re.compile(r"api\.openai\.com|api\.anthropic\.com|generativelanguage\.googleapis\.com|aiplatform\.googleapis\.com|api\.groq\.com|api\.x\.ai|api\.mistral\.ai|openrouter\.ai|new OpenAI\(|new Anthropic\(|messages\.create\(|responses\.create\(|chat\.completions\.create|generateContent")
CONSENT_GATE = re.compile(r"\b\w*[cC]onsent\w*(Accepted|Given|Granted|Version|Required)\b|\b(accept|record|require)\w*Consent\w*\(|\bhasAiConsent\b")
CONSENT = re.compile(r"\b\w*(consent|optIn|opt_in|aiAccepted|aiEnabled|disclos|acknowledg)\w*\b", re.I)
HEALTH_T = re.compile(r"\b(egfr|creatinine|potassium|blood pressure|medication|dialysis|lab|symptom|diagnos\w*|glucose|weight|kidney)\b", re.I)
def ai_boundary(ix):
    sites = []
    for f in ix.files:
        for i, l in enumerate(ix.files[f], 1):
            if AI_CALL.search(l):
                d = fn = None
                for k in range(i, 0, -1):
                    m = DEF_RX.match(ix.files[f][k - 1]); n = LOCAL_DEF_RX.match(ix.files[f][k - 1])
                    if n and not fn and not re.match(r"\s*(const|let)\s+\w+\s*=\s*[^(a]", ix.files[f][k - 1]): fn = (n.group(1) or n.group(2), k)
                    if m: d = (m.group(1), k); break
                sites.append((f, i, d, fn))
    out = []
    gates = [f"{ix.loc(g, j)} {ix.line(g, j)[:90]}" for g in ix.app for j, l in enumerate(ix.files[g], 1) if CONSENT_GATE.search(l)][:6]
    for f, i, d, fn in sites[:30]:
        entry = {"provider_call": f"{ix.loc(f, i)} {ix.line(f, i)[:110]}", "side": "app" if f in ix.app else "backend", "enclosing_function": f"{fn[0]} @ {ix.loc(f, fn[1])}" if fn else None,
                 "enclosing_export": f"{d[0]} @ {ix.loc(f, d[1])}" if d else None, "note": "nearest preceding definitions (static); confirm the real call chain by reading", "client_refs": [], "consent_identifiers_in_callers": [], "app_consent_gate_candidates": gates}
        name = d[0] if d else None; edge = next((n for n, p in ix.edge.items() if p == f), None)
        for g in ix.app:
            for j, l in enumerate(ix.files[g], 1):
                if (name and re.search(rf"[.:]{name}\b", l)) or (edge and edge in l):
                    entry["client_refs"].append(f"{ix.loc(g, j)} {ix.line(g, j)[:90]}")
                    entry["consent_identifiers_in_callers"] += sorted({m.group(0) for x in ix.files[g] for m in CONSENT.finditer(x)})[:6]
        rng = ix.region(f, d[1]) if d else range(max(1, i - 40), i + 1)
        entry["health_terms_in_request_scope"] = sorted({m.group(0).lower() for j in rng for m in HEALTH_T.finditer(ix.files[f][j - 1])})[:8]
        entry["client_refs"] = entry["client_refs"][:4]; entry["consent_identifiers_in_callers"] = sorted(set(entry["consent_identifiers_in_callers"]))[:8]
        out.append(entry)
    dedup = {}
    for e in out: dedup.setdefault(e["enclosing_export"] or e["provider_call"], e)
    return list(dedup.values())[:10]

PURCHASE = re.compile(r"purchasePackage|purchaseProduct|requestPurchase|requestSubscription|purchaseStoreProduct|presentPaywall|RevenueCatUI|<Paywall\b")
RESTORE = re.compile(r"restorePurchases|restoreTransactions|getAvailablePurchases|Restore purchases", re.I)
EXT = re.compile(r"(openURL|openBrowserAsync|openAuthSessionAsync|window\.location|href)\W[^;]{0,80}(checkout|stripe|billing|portal|pricing|subscribe|upgrade)|checkout\.stripe\.com|buy\.stripe\.com|billing\.stripe\.com|checkoutUrl", re.I)
WEBGATE = re.compile(r"Platform\.OS\s*[!=]==?\s*['\"]web['\"]|isWeb\b|Platform\.select\(", re.I)
STRIPE_BE = re.compile(r"checkout\.sessions\.create|billingPortal\.sessions\.create|stripe\.\w+\.create|export const create\w*Checkout\w*\s*=|polar\.checkouts|lemonsqueezy|paddle", re.I)
def billing(ix):
    res = {"native_purchase_calls": [], "restore_calls": [], "external_checkout": [], "backend_checkout_creation": []}
    for f in ix.app:
        L = ix.files[f]
        for i, l in enumerate(L, 1):
            if PURCHASE.search(l): res["native_purchase_calls"].append(f"{ix.loc(f, i)} {ix.line(f, i)[:100]}")
            if RESTORE.search(l): res["restore_calls"].append(f"{ix.loc(f, i)} {ix.line(f, i)[:100]}")
            near = " ".join(L[max(0, i - 9): i - 1])
            if EXT.search(l) or (re.search(r"openURL\(|openBrowserAsync\(|openAuthSessionAsync\(", l) and re.search(r"checkout|purchase|billing|payment|subscribe", near, re.I) and not re.search(r"privacy|terms|legal|support|mailto|manage", l + " " + " ".join(L[max(0, i - 4): i - 1]), re.I)):
                ctxl = " ".join(L[max(0, i - 15): i + 3])
                res["external_checkout"].append({"at": f"{ix.loc(f, i)} {ix.line(f, i)[:110]}", "web_only_file": ".web." in f.name,
                                                 "platform_gate_nearby": bool(WEBGATE.search(ctxl)), "native_file": ".native." in f.name or ".ios." in f.name or ".android." in f.name})
    for f in ix.files:
        if f in ix.app: continue
        for i, l in enumerate(ix.files[f], 1):
            if STRIPE_BE.search(l): res["backend_checkout_creation"].append(f"{ix.loc(f, i)} {ix.line(f, i)[:100]}")
    for k in res: res[k] = res[k][:8]
    ungated = [e for e in res["external_checkout"] if not e["web_only_file"] and not e["platform_gate_nearby"]]
    res["classification"] = ("EXTERNAL_CHECKOUT_REACHABLE_IN_NATIVE" if ungated else "EXTERNAL_CHECKOUT_WEB_GATED" if res["external_checkout"] else
                             "NATIVE_IAP_ONLY" if res["native_purchase_calls"] else
                             "PURCHASE_UI_WITHOUT_STORE_SDK_CALL" if res["restore_calls"] else "NO_PURCHASE_PATH_FOUND")
    return res

PERM_REQ = re.compile(r"request\w*Permissions?Async|use\w*Permissions\(|PermissionsAndroid\.request|requestPermission\(|requestAuthorization\(|requestTrackingPermissionsAsync")
def permissions(ix):
    reqs = [f"{ix.loc(f, i)} {ix.line(f, i)[:100]}" for f in ix.app for i, l in enumerate(ix.files[f], 1) if PERM_REQ.search(l)]
    return {"declared_android": sorted(ix.ctx.android_permissions()), "declared_ios_purpose_strings": sorted(k for k in ix.ctx.plist() if "UsageDescription" in k),
            "runtime_requests": reqs[:12]}

HK_API = re.compile(r"requestAuthorization|queryQuantitySamples|saveQuantitySample|queryCategorySamples|getMostRecentQuantitySample|readRecords|insertRecords|requestPermission\(|initHealthKit|getSdkStatus")
def health(ix):
    calls = [f"{ix.loc(f, i)} {ix.line(f, i)[:100]}" for f in ix.app for i, l in enumerate(ix.files[f], 1)
             if HK_API.search(l) and re.search(r"healthkit|health-connect|react-native-health", " ".join(ix.files[f][:40]), re.I)]
    return {"health_api_calls": calls[:10]}

def trace_all(ctx):
    ix = Idx(ctx)
    return {"files_indexed": len(ix.files), "account_deletion": account_deletion(ix), "privacy_links": privacy_links(ix), "ai_boundary": ai_boundary(ix),
            "billing": billing(ix), "permissions": permissions(ix), "health": health(ix)}
