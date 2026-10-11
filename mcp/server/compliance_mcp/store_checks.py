"""Verified-only Apple submission checks.

HARD RULE (output policy): every function here returns ONLY issues it can verify from code, config, build artifact or
store-listing / App Store Connect data supplied by the owner. If the data a check needs is missing or unresolved, the
check returns [] - it never emits a "possible cause", a hedge or a softened guess.

Each finding: {check, issue, evidence[], fix, official_url, source}.
Store/ASC data is read from <app>/.compliance/store.json (or passed as store_data); see README for the schema.
Excluded by design (cannot be verified from repo/config/build/listing data): lookalike / terminated-developer 4.3
flags, reply-vs-resubmit rejection loops, subscription-attachment backend glitches. Also left out: "IAP available in
only one territory" - no official Apple page states this as a requirement (checked 2026-10-11)."""
import json, plistlib, re, struct, zipfile
from pathlib import Path
from .safety import redact

URL_SDK = "https://developer.apple.com/support/third-party-SDK-requirements/"
URL_UPCOMING = "https://developer.apple.com/news/upcoming-requirements/"
URL_ENCRYPTION = "https://developer.apple.com/documentation/bundleresources/information-property-list/itsappusesnonexemptencryption"
URL_EXPORT = "https://developer.apple.com/help/app-store-connect/manage-app-information/overview-of-export-compliance"
URL_SUBS = "https://developer.apple.com/app-store/subscriptions/"
URL_AGE = "https://developer.apple.com/help/app-store-connect/manage-app-information/set-an-app-age-rating"
URL_SHOTS = "https://developer.apple.com/help/app-store-connect/reference/screenshot-specifications"

def F(check, issue, evidence, fix, url, source):
    return {"check": check, "issue": issue, "evidence": [redact(str(e)) for e in evidence], "fix": fix, "official_url": url, "source": source}

def load_store_data(root, store_data=None):
    if isinstance(store_data, dict): return store_data
    p = Path(root) / ".compliance" / "store.json"
    try: return json.loads(p.read_text())
    except Exception: return None

# (a) Apple-listed SDKs lacking their own privacy manifest (upload error ITMS-91061)
def _has_xcprivacy(d, limit=20000):
    n = 0
    for p in d.rglob("*"):
        n += 1
        if p.suffix == ".xcprivacy": return True
        if n > limit: return None  # too large to prove absence -> unverifiable
    return False
def sdk_missing_privacy_manifest(ctx, store=None, ipa=None):
    from .tables import listed_sdk_pairs
    out = []
    roots = [ctx.root, ctx.repo]
    for dep, sdk in listed_sdk_pairs(ctx):
        d = next((r / "node_modules" / dep for r in roots if (r / "node_modules" / dep).is_dir()), None)
        if d is None: continue  # package not installed here -> cannot verify
        if _has_xcprivacy(d) is False:
            out.append(F("sdk_missing_privacy_manifest", f"{dep} (Apple-listed SDK {sdk}) ships no PrivacyInfo.xcprivacy",
                         [f"installed package {d.relative_to(ctx.repo) if d.is_relative_to(ctx.repo) else d}: no .xcprivacy file inside"],
                         f"Upgrade {dep} to a version that includes its own privacy manifest (otherwise upload fails with ITMS-91061).", URL_SDK, "installed dependency"))
    pods = ctx.root / "ios" / "Pods"
    if pods.is_dir():
        from .tables import validated_sdk_names
        for sdk in validated_sdk_names():
            d = pods / sdk
            if d.is_dir() and _has_xcprivacy(d) is False:
                out.append(F("sdk_missing_privacy_manifest", f"Pod {sdk} (Apple-listed SDK) ships no PrivacyInfo.xcprivacy", [f"ios/Pods/{sdk}: no .xcprivacy file inside"],
                             f"Update the {sdk} pod to a version that includes its privacy manifest (ITMS-91061).", URL_SDK, "installed pod"))
    return out

# (b) build SDK / Xcode and minimum iOS version
def _ipa_plist(ipa):
    try:
        with zipfile.ZipFile(ipa) as z:
            n = next((x for x in z.namelist() if re.fullmatch(r"Payload/[^/]+\.app/Info\.plist", x)), None)
            return plistlib.loads(z.read(n)) if n else None
    except Exception: return None
def _major(v):
    m = re.match(r"\s*(\d+)", str(v)); return int(m.group(1)) if m else None
def build_requirements(ctx, store=None, ipa=None):
    out = []
    pl = _ipa_plist(ipa) if ipa else None
    if pl:
        x = pl.get("DTXcode"); sdk = pl.get("DTSDKName", ""); mo = pl.get("MinimumOSVersion")
        xm = int(str(x)[:-2]) if x and str(x).isdigit() and len(str(x)) >= 3 else None
        sm = _major(re.sub(r"^[a-z]+", "", sdk)) if sdk else None
        if (xm is not None and xm < 26) or (sm is not None and sm < 26):
            out.append(F("build_sdk_too_old", "Build made with an Xcode / iOS SDK older than Xcode 26 / iOS 26",
                         [f".ipa Info.plist DTXcode={x}, DTSDKName={sdk}"], "Rebuild with Xcode 26 or later (iOS 26 SDK); required for uploads since April 28, 2026.", URL_UPCOMING, "build artifact"))
        if mo and _major(mo) is not None and _major(mo) < 13:
            out.append(F("deployment_target_below_ios13", "Minimum iOS version is below iOS 13", [f".ipa Info.plist MinimumOSVersion={mo}"],
                         "Raise the deployment target to iOS 13 or later; required for uploads since September 9, 2026.", URL_UPCOMING, "build artifact"))
        return out
    try: e = json.loads((ctx.root / "eas.json").read_text())
    except Exception: e = None
    for prof, v in ((e or {}).get("build") or {}).items():
        img = (v.get("ios") or {}).get("image") if isinstance(v, dict) else None
        m = re.search(r"xcode-(\d+)", str(img or ""))
        if m and int(m.group(1)) < 26:
            out.append(F("build_sdk_too_old", f"EAS build profile '{prof}' uses an Xcode older than 26", [f"eas.json build.{prof}.ios.image={img}"],
                         "Use an EAS image with Xcode 26 or later (or 'latest'); required for uploads since April 28, 2026.", URL_UPCOMING, "config"))
    # config-level deployment target < 13 is reported by rule CUR-APL-UR-IOS13 (FAIL); not duplicated here
    return out

# (c) ITSAppUsesNonExemptEncryption missing (TestFlight shows "Missing Compliance")
def encryption_key(ctx, store=None, ipa=None):
    if ctx.platforms.get("ios") == "absent": return []
    pl = _ipa_plist(ipa) if ipa else None
    if pl is not None:
        if "ITSAppUsesNonExemptEncryption" in pl: return []
        ev, src = ["built .ipa Info.plist has no ITSAppUsesNonExemptEncryption key"], "build artifact"
    else:
        ios = ctx.expo.get("ios") or {}
        if "ITSAppUsesNonExemptEncryption" in (ios.get("infoPlist") or {}) or "usesNonExemptEncryption" in (ios.get("config") or {}): return []
        plists = [f for f in ctx.tree.files if f.name == "Info.plist" and "ios" in f.parts]
        if any("<key>ITSAppUsesNonExemptEncryption</key>" in ctx.tree.text(f) for f in plists): return []
        if not ctx.config_resolved: return []  # generated Info.plist unknown -> cannot verify
        if ctx.framework != "expo-managed" and not plists: return []
        ev = ["app.json ios.infoPlist / ios.config has no ITSAppUsesNonExemptEncryption"] if ctx.framework == "expo-managed" else [f"{ctx.tree.rel(f)} has no ITSAppUsesNonExemptEncryption" for f in plists]
        src = "config"
    return [F("missing_encryption_declaration", "ITSAppUsesNonExemptEncryption is not set, so every TestFlight build shows 'Missing Compliance'", ev,
              "Add ITSAppUsesNonExemptEncryption to Info.plist (Expo: ios.config.usesNonExemptEncryption or ios.infoPlist), set to false only if the app uses no non-exempt encryption.",
              URL_EXPORT, src)]

# (d) auto-renewable subscriptions without a Terms of Use (EULA) link in listing / paywall data
_TOU = re.compile(r"terms of (use|service)|\beula\b|stdeula", re.I)
def subscription_terms_link(ctx, store=None, ipa=None):
    if not store: return []
    subs = [p for p in (store.get("in_app_purchases") or []) if str(p.get("type", "")).lower().replace("-", "_") in ("auto_renewable", "auto_renewable_subscription")]
    if not subs: return []
    sources = {k: store.get(k) for k in ("listing", "paywall") if isinstance(store.get(k), dict)}
    if not sources: return []  # no listing/paywall data -> cannot verify
    for d in sources.values():
        if d.get("terms_of_use_url") or d.get("eula_url") or _TOU.search(" ".join(str(v) for v in d.values())): return []
    return [F("subscription_missing_terms_link", "Auto-renewable subscriptions are offered but no Terms of Use (EULA) link is present",
              [f"auto-renewable products: {[p.get('product_id') for p in subs][:5]}", f"checked {sorted(sources)} data: no terms_of_use_url / EULA link"],
              "Add a working Terms of Use (EULA) link to the App Store description (or custom EULA field) and to the paywall.", URL_SUBS, "store data")]

# (f) age rating questionnaire unanswered
def age_rating(ctx, store=None, ipa=None):
    ar = (store or {}).get("age_rating")
    if not isinstance(ar, dict) or "questionnaire_completed" not in ar: return []
    if ar["questionnaire_completed"] is False:
        return [F("age_rating_unanswered", "The App Store Connect age rating questionnaire has not been answered", ["App Store Connect data: age_rating.questionnaire_completed=false"],
                  "In App Store Connect > App Information > Age Ratings, answer the questionnaire; an unrated app can't be published on the App Store.", URL_AGE, "App Store Connect data")]
    return []

# (g) iPhone-shaped screenshots in iPad slots
def _img_size(p):
    try:
        b = Path(p).read_bytes()[:65536]
        if b[:8] == b"\x89PNG\r\n\x1a\n": return struct.unpack(">II", b[16:24])
        if b[:2] == b"\xff\xd8":
            i = 2
            while i < len(b) - 9:
                if b[i] != 0xFF: i += 1; continue
                m = b[i + 1]
                if m in (0xC0, 0xC1, 0xC2): h, w = struct.unpack(">HH", b[i + 5:i + 9]); return w, h
                i += 2 + struct.unpack(">H", b[i + 2:i + 4])[0]
    except Exception: pass
    return None
def ipad_screenshots(ctx, store=None, ipa=None):
    out = []
    for s in (store or {}).get("screenshots") or []:
        if not str(s.get("slot", "")).lower().startswith("ipad"): continue
        wh = (s.get("width"), s.get("height")) if s.get("width") and s.get("height") else (_img_size(ctx.root / s["path"]) if s.get("path") else None)
        if not wh: continue
        w, h = int(wh[0]), int(wh[1]); r = max(w, h) / min(w, h)
        if r >= 1.7:  # every iPad size in Apple's spec is <= 1.53:1; every iPhone size is >= 1.77:1
            out.append(F("iphone_screenshot_in_ipad_slot", f"An iPhone-shaped screenshot is used in the {s['slot']} slot",
                         [f"{s.get('path') or s.get('name') or 'screenshot'}: {w}x{h} (aspect {r:.2f}:1; iPad sizes are about 1.33-1.53:1)"],
                         "Upload real iPad screenshots at an iPad size from Apple's screenshot specifications (e.g. 2064x2752).", URL_SHOTS, "store data"))
    return out

STORE_CHECKS = [sdk_missing_privacy_manifest, build_requirements, encryption_key, subscription_terms_link, age_rating, ipad_screenshots]
def run_all(ctx, store_data=None, ipa=None):
    store = load_store_data(ctx.root, store_data); out = []
    if ctx.platforms.get("ios") == "absent": return out
    for c in STORE_CHECKS:
        try: out += c(ctx, store, ipa)
        except Exception: pass  # a check that cannot run emits nothing (rule 1)
    return out
