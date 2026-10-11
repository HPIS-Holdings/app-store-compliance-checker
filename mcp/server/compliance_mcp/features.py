"""Feature gates. Each feature -> {state, evidence, basis}.
state: DETECTED | NOT_DETECTED | UNRESOLVED | DECLARED_TRUE | DECLARED_FALSE.
NOT_DETECTED means 'not found by a static scan' (NOT proof of absence). Declared-only features are UNRESOLVED
unless the owner declares them (in .compliance/features.json or the declared_features argument)."""
import json, re

DECLARED_ONLY = {"physical_goods", "reader_content", "human_health", "eu_distribution", "regulatory_clearance", "regulated_medical_device", "health_research", "external_health_hardware", "personal_account"}
AI_IMPORT = r"""(from\s+['"]|require\(\s*['"]|import\s+['"])(openai|@anthropic-ai/sdk|@google/generative-ai|@google/genai|groq-sdk|@mistralai/mistralai|@ai-sdk/[\w-]+|ai/rsc|replicate|cohere-ai|together-ai)['"/]|^\s*(import|from)\s+(openai|anthropic|google\.generativeai|google\.genai)\b"""
AI_URL = r"api\.openai\.com|api\.anthropic\.com|generativelanguage\.googleapis\.com|api\.groq\.com|api\.x\.ai|api\.mistral\.ai|openrouter\.ai/api|api\.together\.xyz|api\.deepseek\.com|aiplatform\.googleapis\.com"
HEALTH_META = r"\b(health|medical|patient|symptoms?|kidney|ckd\w*|egfr|dialysis|renal|medications?|meds|blood pressure|glucose|diabet\w*|clinical|caregiver|therapy|fertility|pregnan\w*)\b"
HEALTH_CODE = r"\b(kidney|egfr|dialysis|renal|medications?|blood pressure|glucose|insulin|healthkit|health ?connect|medical device|caregiver|heart rate|blood sugar)\b"  # domain terms only; generic words (diagnosed, symptoms, patient) matched game code
REC = r"Audio\.Recording|useAudioRecorder|RecordingPresets|AudioModule\.requestRecordingPermissionsAsync|requestRecordingPermissionsAsync|startRecording\(|Voice\.start|ExpoSpeechRecognitionModule|useSpeechRecognitionEvent|getUserMedia\("
SIGNUP = r"\b(signUp|sign_up|createUserWithEmailAndPassword|createAccount|registerUser|useSignUp|signInWithOtp|signInWithOAuth|signInWithIdToken|signInWithPassword|sendEmailCode|verifyEmailCode|linkAccount|signInAsync|signIn\(\s*['\"](password|anonymous|google|apple|resend|email))"

def F(state, evidence, basis): return {"state": state, "evidence": evidence[:6], "basis": basis}
def _found_or_not(ctx, hits, basis, config_dep=True):
    """config_dep: the feature can be introduced by app config (permissions, entitlements, plugin, app name) that an
    unresolved dynamic app.config.* may contain -> UNRESOLVED instead of NOT_DETECTED in that case."""
    if hits: return F("DETECTED", hits, basis)
    complete = (ctx.complete if config_dep else not ctx.tree.truncated)
    return F("NOT_DETECTED" if complete else "UNRESOLVED", [f"no {basis} signal in static scan" + ("" if complete else f" (coverage incomplete: config {ctx.config_state}, truncated={ctx.tree.truncated})")], basis)

def detect(ctx):
    f = {}; perms = ctx.android_permissions(); meta = " ".join(str(ctx.expo.get(k, "")) for k in ("name", "slug", "description"))
    hk = ctx.has_dep("react-native-health", "@kingstinct/react-native-healthkit", "react-native-healthkit", "expo-health-kit")
    ent = (ctx.expo.get("ios") or {}).get("entitlements") or {}
    if ent.get("com.apple.developer.healthkit"): hk.append("ios.entitlements com.apple.developer.healthkit")
    f["healthkit"] = _found_or_not(ctx, [f"dependency/entitlement: {x}" for x in hk], "HealthKit")
    hc = ctx.has_dep("react-native-health-connect", "expo-health-connect") + [f"permission {p}" for p in perms if p.startswith("android.permission.health.") or p.startswith("health.")]
    f["health_connect"] = _found_or_not(ctx, hc, "Health Connect")
    h = []
    if re.search(HEALTH_META, meta, re.I): h.append(f"app name/slug/description: {meta[:100]}")
    if hk or hc: h.append("health integration present")
    if not h:
        code = ctx.tree.grep(HEALTH_CODE, limit=120, exts={'.js', '.jsx', '.ts', '.tsx'}); files = {x.split(":", 1)[0] for x in code}
        terms = {m.lower() for x in code for m in re.findall(HEALTH_CODE, x.split(": ", 1)[-1], re.I)}
        if len(files) >= 5 and len(terms) >= 2: h = code[:3] + [f"health terms in {len(files)} source files (heuristic)"]
    f["health"] = _found_or_not(ctx, h, "health/medical")
    vet = []
    if re.search(r"\b(vet|veterinar\w*|pets?|cats?|dogs?|feline|canine|renalcat\w*)\b", meta, re.I): vet.append(f"app name/slug/description: {meta[:100]}")
    if re.search(r"\b(vet|pets?|cats?|dogs?|feline|canine)\b", ctx.repo.name.replace("-", " "), re.I): vet.append(f"repository name: {ctx.repo.name}")
    vh = ctx.tree.grep(r"\bveterinar\w*|\bfeline\b|\bcanine\b|\byour (cat|dog|pet)\b", exts=(".ts", ".tsx", ".js", ".jsx"), limit=10)
    if len({h[0] for h in vh}) >= 2: vet += [f"{h[0]}:{h[1]} veterinary term" for h in vh[:3]]
    f["veterinary"] = _found_or_not(ctx, vet, "veterinary/pet subject") if vet or ctx.complete else F("UNRESOLVED", ["app metadata unresolved"], "veterinary/pet subject")
    ai = ctx.grep_all(AI_IMPORT, limit=4) + ctx.grep_all(AI_URL, limit=4)
    ai += [f"dependency {d}" for d in ctx.has_dep("openai", "@anthropic-ai/sdk", "@google/generative-ai", "@google/genai", "groq-sdk", "@mistralai/mistralai", "ai")]
    f["ai"] = _found_or_not(ctx, ai, "third-party AI provider", config_dep=False)
    if ai: f["ai"]["where"] = "backend" if all(x.startswith("[backend") for x in ai if not x.startswith("dependency")) and not any(x.startswith("dependency") for x in ai) else "app"
    iap = ctx.has_dep("react-native-purchases", "react-native-purchases-ui", "react-native-iap", "expo-iap", "expo-in-app-purchases", "@revenuecat/purchases-capacitor")
    iap_code = [] if iap else ctx.tree.grep(r"restore ?purchases|restorePurchases|requestPurchase|purchasePackage|purchaseProduct|in-?app purchase|\bpaywall\b", limit=3, exts={'.js', '.jsx', '.ts', '.tsx'})
    f["iap"] = _found_or_not(ctx, [f"dependency {x}" for x in iap] + [f"permission {p}" for p in perms if p.endswith("BILLING")] + iap_code, "in-app purchase", config_dep=False)
    acc = [f"dependency {x}" for x in ctx.has_dep("@clerk/clerk-expo", "@react-native-firebase/auth", "@convex-dev/auth", "aws-amplify", "@supabase/auth-js", "better-auth", "@auth0/auth0-react-native", "react-native-auth0", "expo-apple-authentication", "@invertase/react-native-apple-authentication")]
    acc += ctx.grep_all(SIGNUP, limit=4)
    f["accounts"] = _found_or_not(ctx, acc, "account creation", config_dep=False)
    rec = ctx.tree.grep(REC, limit=4) + ([f"permission RECORD_AUDIO ({perms['RECORD_AUDIO']})"] if "RECORD_AUDIO" in perms else []) + [f"dependency {d}" for d in ctx.has_dep("@react-native-voice/voice", "expo-speech-recognition", "react-native-audio-recorder-player", "@siteed/expo-audio-studio")]
    f["microphone"] = _found_or_not(ctx, rec, "microphone recording")
    f["speech"] = _found_or_not(ctx, [f"dependency {d}" for d in ctx.has_dep("@react-native-voice/voice", "expo-speech-recognition")], "Apple speech recognition", config_dep=False)
    tr = ctx.has_dep("react-native-fbsdk-next", "react-native-google-mobile-ads", "react-native-appsflyer", "react-native-adjust", "react-native-branch", "@singular-apps/react-native-singular", "expo-ads-admob")
    f["tracking"] = _found_or_not(ctx, [f"dependency {x}" for x in tr], "tracking/ads SDK", config_dep=False)
    sl = [f"dependency {x}" for x in ctx.has_dep("@react-native-google-signin/google-signin", "react-native-fbsdk-next", "@invertase/react-native-google-signin")]
    sl += ctx.tree.grep(r"expo-auth-session/providers/(google|facebook)|oauth_(google|facebook|github)|strategy:\s*['\"]oauth_", limit=3)
    f["social_login"] = _found_or_not(ctx, sl, "third-party login", config_dep=False)
    ea = [f"permission {p} ({perms[p]})" for p in ("USE_EXACT_ALARM", "SCHEDULE_EXACT_ALARM") if p in perms]
    f["exact_alarm"] = _found_or_not(ctx, ea, "exact alarm permission")
    if ea and re.search(r"\b(alarm|clock|timer|calendar)\b", meta, re.I): f["exact_alarm"]["alarm_or_calendar_signal"] = meta[:100]
    fgs = [f"permission {p}" for p in perms if p.startswith("FOREGROUND_SERVICE")]
    f["foreground_service"] = _found_or_not(ctx, fgs, "foreground service")
    ep = ctx.tree.grep(r"checkout\.stripe\.com|buy\.stripe\.com|paddle\.com/checkout|lemonsqueezy\.com/checkout|Linking\.openURL\([^)]*(checkout|pricing|subscribe)", limit=3)
    f["external_purchase"] = _found_or_not(ctx, ep, "external purchase link", config_dep=False)
    # COMPLIANCE-OPERATIONS-004 gates (feature signals only; no new tracing). Absence => non-definite NOT_APPLICABLE.
    code_exts = {'.js', '.jsx', '.ts', '.tsx'}
    ads = ctx.has_dep("react-native-google-mobile-ads", "expo-ads-admob", "react-native-applovin-max", "react-native-unity-ads", "react-native-fbads", "@react-native-admob/admob", "react-native-ironsource-mediation")
    f["ads"] = _found_or_not(ctx, [f"dependency {x}" for x in ads], "ad SDK", config_dep=False)
    ugc = ctx.tree.grep(r"\b(createPost|publishPost|submitPost|addComment|postComment|submitComment|createComment|sendChatMessage|createThread|uploadPost|reportPost|blockUser)\b", limit=4, exts=code_exts)
    f["ugc"] = _found_or_not(ctx, ugc, "user-generated content", config_dep=False)
    kids = [f"app name/slug/description: {meta[:100]}"] if re.search(r"\b(kids?|children|toddlers?|preschool\w*|nursery)\b", meta, re.I) else []
    f["kids_audience"] = _found_or_not(ctx, kids, "child audience")
    lb = ctx.tree.grep(r"(?i)loot[ _-]?box|\bgacha\b|mystery[ _-]?box|\brandom(ized)?[ _-]?(reward|item)s?\b", limit=3, exts=code_exts)
    f["loot_boxes"] = _found_or_not(ctx, lb, "randomized paid items", config_dep=False)
    rmg = ctx.tree.grep(r"\b(real[- ]money (game|gaming|contest)|sportsbook|place (a )?bet|wager(ing)?|online casino)\b", limit=3, exts=code_exts)
    f["real_money_gaming"] = _found_or_not(ctx, rmg, "real-money gaming", config_dep=False)
    rel = [f"app name/slug/description: {meta[:100]}"] if re.search(r"\b(religio\w*|hindu\w*|sanatan\w*|islam\w*|quran|bible|christian\w*|church|mosque|temple|prayers?|puja|gita|occult\w*|astrolog\w*|tarot)\b", meta + " " + ctx.repo.name.replace("-", " "), re.I) else []
    f["religious_content"] = _found_or_not(ctx, rel, "religious/spiritual content")
    f["native_code"] = F("DETECTED", [f"framework {ctx.framework} ships native libraries"], "framework") if ctx.framework in ("expo-managed", "expo-bare", "react-native", "flutter") else F("UNRESOLVED", ["native code not determined"], "framework")
    for k in DECLARED_ONLY: f[k] = F("UNRESOLVED", [f"'{k}' cannot be detected statically; declare it in .compliance/features.json"], "declaration-only")
    decl = dict(ctx.declared)
    try: decl = {**json.loads((ctx.root / ".compliance" / "features.json").read_text()), **decl}
    except Exception: pass
    for k, v in decl.items():
        if isinstance(v, bool): f[k] = F("DECLARED_TRUE" if v else "DECLARED_FALSE", [f"declared by owner: {k}={v}"], "owner-declaration")
    return f
