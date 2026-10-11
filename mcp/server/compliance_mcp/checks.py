"""Static checks. Return [{check, status, evidence[], fix, level}].
status: PASS | FAIL | NEEDS_REVIEW | NOT_APPLICABLE.
FAIL only for a demonstrated violation in resolved static config (e.g. a used capability whose required
Info.plist key is absent from a fully static config, or an explicit targetSdk below the requirement).
Missing keywords never FAIL (-> NEEDS_REVIEW). PASS carries level='source-config' (no release artifact checked)."""
import re
from .safety import redact

def R(check, status, evidence, fix=None, level="source-config"):
    return {"check": check, "status": status, "evidence": [redact(str(e)) for e in evidence] or ["(no evidence)"], "fix": fix, "level": level}

def _purpose(ctx, check, key, plugin_keys, fix):
    pl = ctx.plist(); hit = pl.get(key)
    for pk in plugin_keys:
        if not hit and pk in pl: hit = pl[pk]
    if hit:
        src, val = hit
        if not str(val).strip(): return [R(check, "FAIL" if ctx.config_resolved else "NEEDS_REVIEW", [f"{key} is empty ({src})"], fix)]
        if not ctx.config_resolved:
            return [R(check, "NEEDS_REVIEW", [f"{key} set in {src}: {str(val)[:120]!r}", f"but config is {ctx.config_state} ({', '.join(ctx.dynamic_files)}); the generated Info.plist may differ"], "Confirm the key in the built Info.plist (npx expo config --type introspect, or the .ipa).")]
        return [R(check, "PASS", [f"{key} set in {src}: {str(val)[:120]!r}"])]
    if ctx.config_resolved:
        return [R(check, "FAIL", [f"{key} not found in app.json ios.infoPlist, config-plugin options or Info.plist (config fully static)"], fix)]
    lit = ctx.dynamic_literals["purpose_strings"].get(key) or next((ctx.dynamic_literals["purpose_strings"][k] for k in plugin_keys if k in ctx.dynamic_literals["purpose_strings"]), None)
    ev = [f"{key} not found in static files; config is {ctx.config_state} ({', '.join(ctx.dynamic_files)}) so the generated Info.plist is unresolved (app.config not executed)"]
    if lit: ev.append(f"literal {key} found in {lit[0]}: {lit[1][:100]!r} (static read; final value UNKNOWN)")
    ev += [f"env-dependent: {x}" for x in ctx.dynamic_literals["env_dependent_keys"] if key in x]
    return [R(check, "NEEDS_REVIEW", ev, fix)]

def ios_mic_usage(ctx, f):
    return _purpose(ctx, "ios_mic_usage", "NSMicrophoneUsageDescription", ["microphonePermission", "recordAudioAndroid"][:1],
                    "Add NSMicrophoneUsageDescription (app.json ios.infoPlist or the expo-audio/expo-av 'microphonePermission' plugin option) that explains the voice feature.")
def ios_speech_usage(ctx, f):
    return _purpose(ctx, "ios_speech_usage", "NSSpeechRecognitionUsageDescription", ["speechRecognitionPermission"], "Add NSSpeechRecognitionUsageDescription.")
def healthkit_usage(ctx, f):
    pl = ctx.plist(); have = [k for k in ("NSHealthShareUsageDescription", "NSHealthUpdateUsageDescription", "healthSharePermission", "healthUpdatePermission") if k in pl]
    if not have:
        st = "FAIL" if ctx.config_resolved else "NEEDS_REVIEW"
        return [R("healthkit_usage", st, [f"HealthKit integration: {f['healthkit']['evidence'][0]}", "no NSHealthShareUsageDescription / NSHealthUpdateUsageDescription found" + ("" if ctx.config_resolved else f" (config {ctx.config_state})")],
                  "Add NSHealthShareUsageDescription (read) and NSHealthUpdateUsageDescription (write) and a privacy policy.")]
    return [R("healthkit_usage", "NEEDS_REVIEW", [f"present: {have}"], "Confirm each HealthKit read/write has its key, a privacy policy exists, and HealthKit data is not used for ads or shared with third parties (incl. AI) without express permission.")]

def _ver(v):
    m = re.match(r"\s*(\d+)(?:\.(\d+))?", str(v)); return (int(m.group(1)), int(m.group(2) or 0)) if m else None
def android_target_sdk(ctx, f, need=36, check="android_target_sdk"):
    bp = ctx.plugin("expo-build-properties") or {}; v, src = (bp.get("android") or {}).get("targetSdkVersion"), "expo-build-properties"
    if v is None:
        for fl in ctx.tree.files:
            if fl.name in ("build.gradle", "build.gradle.kts", "gradle.properties", "libs.versions.toml"):
                m = re.search(r"targetSdk(?:Version)?\s*[=:]?\s*(\d{2})\b", ctx.tree.text(fl))
                if m: v, src = int(m.group(1)), ctx.tree.rel(fl); break
    if v is None and ctx.derived and not ctx.derived["overridden_by"]:
        d = ctx.derived; ok = d["targetSdkVersion"] >= need
        return [R(check, "NEEDS_REVIEW", [f"no explicit targetSdkVersion; derived default {d['targetSdkVersion']} for Expo SDK {d['expo_sdk']} ({d['source']}, fetched {d['fetched']}) - {'meets' if ok else 'BELOW'} {need}", "vendor default, not a release-artifact fact"],
                  "Confirm targetSdkVersion in the built AAB." if ok else f"Upgrade Expo SDK or set targetSdkVersion >= {need}.", level="derived-vendor-default")]
    if v is None:
        return [R(check, "NEEDS_REVIEW", [f"no explicit targetSdkVersion in static config (expo={ctx.deps.get('expo')}, react-native={ctx.deps.get('react-native')})"],
                  "Check the built AAB (bundletool dump manifest / greenlight --aab): new apps and updates need targetSdk >= 36 since 2026-08-31 (extension to 2026-11-01).")]
    if int(v) >= need: return [R(check, "PASS", [f"targetSdkVersion={v} ({src}) >= {need}"])]
    return [R(check, "FAIL", [f"targetSdkVersion={v} ({src}) < {need}"], f"Set targetSdkVersion to {need} or higher.")]
def android_target_sdk_existing(ctx, f): return android_target_sdk(ctx, f, 35, "android_target_sdk_existing")
def ios_deployment_target(ctx, f):
    bp = ctx.plugin("expo-build-properties") or {}; v = (bp.get("ios") or {}).get("deploymentTarget"); src = "expo-build-properties"
    if v is None:
        for fl in ctx.tree.files:
            if fl.name in ("Podfile", "Podfile.properties.json", "project.pbxproj"):
                m = re.search(r"(?:platform :ios, ['\"]|\"ios\.deploymentTarget\"\s*:\s*\"|IPHONEOS_DEPLOYMENT_TARGET = )([\d.]+)", ctx.tree.text(fl))
                if m: v, src = m.group(1), ctx.tree.rel(fl); break
    if v is None and ctx.derived and not ctx.derived["overridden_by"]:
        d = ctx.derived
        return [R("ios_deployment_target", "NEEDS_REVIEW", [f"no explicit deployment target; derived Expo SDK {d['expo_sdk']} minimum iOS {d['ios_min']} ({d['source']}) - meets 13.0", "vendor default, not a release-artifact fact"], "Confirm MinimumOSVersion in the built .ipa.", level="derived-vendor-default")]
    if v is None: return [R("ios_deployment_target", "NEEDS_REVIEW", ["no explicit iOS deployment target in static config"], "Confirm IPHONEOS_DEPLOYMENT_TARGET >= 13.0 in the built app.")]
    ok = _ver(v) and _ver(v) >= (13, 0)
    return [R("ios_deployment_target", "PASS" if ok else "FAIL", [f"deployment target {v} ({src})"], None if ok else "Raise the iOS deployment target to 13.0 or later.")]

def exact_alarm(ctx, f):
    ea = f["exact_alarm"]; sig = ea.get("alarm_or_calendar_signal")
    use = any("USE_EXACT_ALARM" in e for e in ea["evidence"])
    fix = ("Document that alarm/timer/calendar is the core user-facing function and complete the Play exact-alarm declaration." if sig else
           "USE_EXACT_ALARM is restricted to apps whose core function needs exact alarms (alarm clock/timer, calendar). If reminders are not core alarm/calendar functionality, use inexact alarms or SCHEDULE_EXACT_ALARM with a runtime check.") if use else \
          "SCHEDULE_EXACT_ALARM is denied by default on Android 14+; check canScheduleExactAlarms() and justify use."
    return [R("exact_alarm", "NEEDS_REVIEW", ea["evidence"] + ([f"alarm/calendar signal in app metadata: {sig}"] if sig else ["no alarm/calendar signal in app name/description"]), fix)]

def _presence(check, hits, found_fix, missing_fix, what):
    if hits: return [R(check, "NEEDS_REVIEW", hits[:4], found_fix)]
    return [R(check, "NEEDS_REVIEW", [f"{what} not found by keyword search (absence of a keyword is not proof of absence)"], missing_fix)]

def iap_library(ctx, f): return [R("iap_library", "NEEDS_REVIEW", f["iap"]["evidence"], "Confirm all digital unlocks use App Store IAP / Google Play Billing (RevenueCat uses both).")]
def restore_purchases(ctx, f):
    h = ctx.tree.grep(r"restorePurchases|restoreTransactions|getAvailablePurchases|RevenueCatUI\.|presentPaywall|<Paywall\b", limit=4)
    return _presence("restore_purchases", h, "Verify a visible Restore Purchases action in the release build (RevenueCat Paywalls include one).",
                     "Add a visible 'Restore Purchases' action (Purchases.restorePurchases()).", "restore-purchases call or RevenueCat paywall")
def paywall_disclosures(ctx, f):
    h = ctx.tree.grep(r"terms of (use|service)|\beula\b|stdeula|privacy policy|auto-?renew", limit=4)
    return _presence("paywall_disclosures", h, "Verify on device: price, period, auto-renewal terms, working Terms/EULA and Privacy links; billed amount most prominent.",
                     "Show price, billing period, auto-renewal terms and Terms/EULA + Privacy links on the paywall.", "paywall terms/privacy/auto-renew text")
def account_deletion(ctx, f):
    h = ctx.grep_all(r"delete ?(my )?account|deleteAccount|deleteUser|account deletion|removeAccount|deleteMe|closeAccount", limit=4)
    return _presence("account_deletion", h, "Verify deletion can be initiated in-app (Apple) and via a web URL listed in Play Console (Google), and that data is deleted server-side.",
                     "Offer in-app account deletion and a web deletion resource; freezing/deactivation does not count.", "account-deletion flow")
def ai_consent(ctx, f):
    h = ctx.grep_all(r"consent|opt[- ]?in|allow .{0,30}(share|send)|(ai|assistant).{0,40}(agree|permission)", limit=4)
    where = f["ai"].get("where", "app")
    return _presence("ai_consent", h, f"AI calls detected ({where}). Verify a blocking disclosure names the AI provider and the data sent, obtains explicit opt-in before the first call, and is revocable; name the processor in the privacy policy.",
                     f"AI calls detected ({where}). Add a disclosure + explicit opt-in before personal data is sent to the AI provider.", "AI consent UI")
def ai_report(ctx, f):
    h = ctx.tree.grep(r"report (this )?(response|answer|message|content|output)|flag (this )?(response|content)|reportResponse|reportAi|thumbs[_ -]?down|feedback.{0,20}(response|answer)", limit=4)
    return _presence("ai_report", h, "Verify in-app reporting/flagging of AI output reaches the developer without leaving the app.",
                     "Add an in-app 'Report response' control on generated content.", "AI output report/flag control")
def medical_disclaimers(ctx, f):
    a = ctx.tree.grep(r"not a medical device", code_only=False, limit=2); b = ctx.tree.grep(r"consult (a|your) (doctor|physician|healthcare|veterinarian|vet)|check with (a|your) doctor|medical advice", code_only=False, limit=2)
    return [R("medical_disclaimers", "NEEDS_REVIEW", (a or ["'not a medical device' text not found in repo"]) + (b or ["'consult a doctor/healthcare professional' text not found in repo"]),
              "Play store description must carry the 'not a medical device...' disclaimer (unless regulated); apps must remind users to consult a healthcare professional. Verify store listing + in-app copy.")]
def medical_claims(ctx, f):
    h = ctx.tree.grep(r"diagnos(e|is|tic)|\bcures?\b|clinically (proven|validated)|\b(accurate|accuracy)\b.{0,30}(egfr|reading|measure)|replaces? your doctor", code_only=False, limit=5)
    return [R("medical_claims", "NEEDS_REVIEW", h or ["no claim keywords found in repo (store listing not scanned)"], "Each accuracy/clinical claim needs disclosed data and methodology; avoid diagnosis/treatment claims unless regulated.")]
def privacy_policy_link(ctx, f):
    h = [f"privacy screen file: {ctx.tree.rel(x)}" for x in ctx.tree.files if "privacy" in x.name.lower() and x.suffix in (".tsx", ".jsx", ".ts", ".js")]
    h += ctx.tree.grep(r"https?://\S*privacy|privacy ?policy|/privacy\b", limit=3)
    return _presence("privacy_policy_link", h, "Verify the in-app link works and the same URL is set in App Store Connect and Play Console.",
                     "Link the privacy policy inside the app and in both store consoles.", "privacy policy link/screen")
def privacy_manifest(ctx, f):
    pm = (ctx.expo.get("ios") or {}).get("privacyManifests"); files = [ctx.tree.rel(x) for x in ctx.tree.files if x.suffix == ".xcprivacy"]
    from .tables import required_reason_summary
    ev = [f"app.json ios.privacyManifests: {'present' if pm else 'absent'}", f"PrivacyInfo.xcprivacy files: {files or 'none'}"]
    declared = {t.get("NSPrivacyAccessedAPIType") for t in ((pm or {}).get("NSPrivacyAccessedAPITypes") or []) if isinstance(t, dict)}
    ev += required_reason_summary(ctx, declared)
    return [R("privacy_manifest", "NEEDS_REVIEW", ev, "Declare required-reason API categories with valid reason codes (expo ios.privacyManifests or PrivacyInfo.xcprivacy); confirm on upload (ITMS-91053 / 91061).")]
def sdk_privacy_manifests(ctx, f):
    from .tables import listed_sdks_in_deps
    hits = listed_sdks_in_deps(ctx)
    return [R("sdk_privacy_manifests", "NEEDS_REVIEW", hits or ["no dependency matched Apple's listed privacy-impacting SDK names (npm->SDK mapping is partial)"], "Ensure each listed SDK version ships its privacy manifest (and signature for binaries).")]
def att_tracking(ctx, f):
    att = ctx.has_dep("expo-tracking-transparency", "react-native-tracking-transparency"); key = "NSUserTrackingUsageDescription" in ctx.plist()
    return [R("att_tracking", "NEEDS_REVIEW", f["tracking"]["evidence"] + [f"ATT library: {att or 'none'}", f"NSUserTrackingUsageDescription: {'present' if key else 'not found'}"],
              "If the SDK tracks (links data with third-party data for ads/measurement or shares with data brokers), request ATT first; otherwise configure the SDK not to track.")]
def health_connect(ctx, f): return [R("health_connect", "NEEDS_REVIEW", f["health_connect"]["evidence"], "Complete the Health Connect declaration; request only data types needed for an approved use case; no ads use or sale.")]
def icloud_storage(ctx, f):
    ic = ((ctx.expo.get("ios") or {}).get("usesIcloudStorage") and ["ios.usesIcloudStorage=true"]) or ctx.tree.grep(r"CloudKit|NSUbiquitous|react-native-cloud-store|iCloud", limit=3)
    return [R("icloud_storage", "NEEDS_REVIEW", ic or ["no iCloud storage API or capability found"], "Do not store personal health information in iCloud (incl. iCloud Documents/KVS).")]
def social_login(ctx, f):
    siwa = ctx.has_dep("expo-apple-authentication", "@invertase/react-native-apple-authentication") + ctx.tree.grep(r"oauth_apple|AppleAuthentication", limit=2)
    return [R("social_login", "NEEDS_REVIEW", f["social_login"]["evidence"] + [f"Sign in with Apple / equivalent: {siwa or 'not found'}"], "Offer an equivalent privacy-preserving login (e.g. Sign in with Apple) unless a 4.8 exception applies.")]
def external_purchase(ctx, f): return [R("external_purchase", "NEEDS_REVIEW", f["external_purchase"]["evidence"], "External purchase links: allowed on the US App Store storefront; elsewhere only via entitlements; Google Play US: external content links program.")]
def webview_scope(ctx, f):
    w = ctx.has_dep("react-native-webview"); n = len([x for x in ctx.tree.files if x.suffix in (".tsx", ".jsx")])
    return [R("webview_scope", "NEEDS_REVIEW", [f"react-native-webview: {'yes' if w else 'no'}", f"{n} tsx/jsx files"], "Provide native features beyond a wrapped website." if w else "Confirm the app provides lasting, non-trivial functionality.")]
def permission_inventory(ctx, f):
    return [R("permission_inventory", "NEEDS_REVIEW", [f"android permissions (static, not merged): {sorted(ctx.android_permissions())}", f"iOS purpose strings: {sorted(k for k in ctx.plist() if 'UsageDescription' in k)}"],
              "Request only permissions for promoted core features; show a prominent in-app disclosure before runtime requests for unexpected data access.")]
def sdk_inventory(ctx, f): return [R("sdk_inventory", "NEEDS_REVIEW", [f"{len(ctx.deps)} dependencies"], "Map each SDK's data collection/sharing to Data safety and App privacy answers.")]
def foreground_service(ctx, f): return [R("foreground_service", "NEEDS_REVIEW", f["foreground_service"]["evidence"], "Declare foreground service types + permissions and complete the Play FGS declaration.")]
def page_size_16kb(ctx, f): return [R("page_size_16kb", "NEEDS_REVIEW", [f"react-native={ctx.deps.get('react-native')}", f"expo={ctx.deps.get('expo')}"], "Verify .so alignment in the built AAB (Play Console App bundle explorer / greenlight --aab).")]
def play_billing_version(ctx, f): return [R("play_billing_version", "NEEDS_REVIEW", [f"react-native-purchases={ctx.deps.get('react-native-purchases')}", f"react-native-iap={ctx.deps.get('react-native-iap')}"], "Confirm the bundled Play Billing Library is >= 8 (PBL 7 extension ended 2026-11-01).")]
def eas_xcode_image(ctx, f):
    import json
    try: e = json.loads((ctx.root / "eas.json").read_text())
    except Exception: e = {}
    imgs = {k: (v.get("ios") or {}).get("image") for k, v in (e.get("build") or {}).items() if isinstance(v, dict)}
    return [R("eas_xcode_image", "NEEDS_REVIEW", [f"eas.json ios images: {imgs or 'eas.json not found'}"], "Confirm the iOS build used Xcode 26+ (required since 2026-04-28).")]

# rule static_checks names (from rules jsonl) -> implementation
CHECKS = {
 "ios_mic_usage": ios_mic_usage, "ios_speech_usage": ios_speech_usage, "healthkit_usage": healthkit_usage,
 "android_target_sdk": android_target_sdk, "android_target_sdk_existing": android_target_sdk_existing, "ios_deployment_target": ios_deployment_target, "exact_alarm": exact_alarm,
 "revenuecat_or_storekit": iap_library, "restore_purchases": restore_purchases, "paywall_legal_links": paywall_disclosures,
 "account_deletion_presence": account_deletion, "ai_provider_consent": ai_consent, "ai_report_feature": ai_report,
 "medical_disclaimer_strings": medical_disclaimers, "medical_claims_scan": medical_claims, "privacy_policy_link": privacy_policy_link,
 "privacy_manifest": privacy_manifest, "att_tracking": att_tracking, "health_connect_usage": health_connect,
 "icloud_health_storage": icloud_storage, "external_purchase_links": external_purchase, "social_login_siwa": social_login,
 "webview_only_scan": webview_scope, "permission_inventory": permission_inventory, "sdk_inventory": sdk_inventory,
 "foreground_service": foreground_service, "page_size_16kb": page_size_16kb, "play_billing_version": play_billing_version,
 "eas_xcode_image": eas_xcode_image, "ios_usage_descriptions": lambda c, f: ios_mic_usage(c, f) if f["microphone"]["state"] in ("DETECTED", "DECLARED_TRUE") else [],
}
# checks that only make sense when a feature is present (prevents e.g. an AI check failing a HealthKit rule)
CHECK_FEATURE = {"ios_mic_usage": "microphone", "ios_speech_usage": "speech", "healthkit_usage": "healthkit", "ai_provider_consent": "ai",
                 "ai_report_feature": "ai", "health_connect_usage": "health_connect", "att_tracking": "tracking", "social_login_siwa": "social_login",
                 "exact_alarm": "exact_alarm", "restore_purchases": "iap", "paywall_legal_links": "iap", "revenuecat_or_storekit": "iap",
                 "play_billing_version": "iap", "account_deletion_presence": "accounts", "foreground_service": "foreground_service",
                 "external_purchase_links": "external_purchase", "medical_disclaimer_strings": "health", "medical_claims_scan": "health",
                 "icloud_health_storage": "health"}
