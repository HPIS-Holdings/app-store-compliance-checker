"""Optional Greenlight integration (https://github.com/RevylAI/greenlight, MIT), pinned to v0.2.0.
Runs ONLY `greenlight preflight <path> --format json` (+ optional local --aab/--apk/--ipa). Never --verify,
--artifact, `scan`, or `auth` (those talk to Revyl / App Store Connect). It runs only inside `unshare -rn`
(no network); if that is unavailable it REFUSES to run. Output is evidence; it never upgrades a verdict to PASS."""
import json, os, re, shutil, subprocess
from pathlib import Path
from .safety import redact
PINNED = "0.2.0"
DEFAULT_BIN = Path.home() / ".local/share/mobile-compliance/greenlight-0.2.0/greenlight"

def locate():
    for c in (os.environ.get("GREENLIGHT_BIN"), str(DEFAULT_BIN), shutil.which("greenlight")):
        if c and Path(c).is_file() and os.access(c, os.X_OK): return c
    return None

def run(project, aab=None, apk=None, ipa=None, timeout=180):
    b = locate()
    if not b: return {"status": "not-installed", "findings": [], "note": "install with mcp/tools/install_greenlight.sh"}
    try: ver = subprocess.run([b, "--version"], capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception as e: return {"status": "error", "findings": [], "note": f"version check failed: {e!r}"}
    if PINNED not in ver: return {"status": "version-mismatch", "findings": [], "note": f"found '{ver}', pinned {PINNED}; not used"}
    cmd = [b, "preflight", str(project), "--format", "json"]
    for flag, v in (("--aab", aab), ("--apk", apk), ("--ipa", ipa)):
        if v: cmd += [flag, str(v)]
    # Network isolation is mandatory: refuse to run rather than fall back to an unsandboxed process.
    if not (shutil.which("unshare") and subprocess.run(["unshare", "-rn", "true"], capture_output=True).returncode == 0):
        return {"status": "refused-no-network-isolation", "findings": [], "version": ver, "note": "`unshare -rn` unavailable; Greenlight not run"}
    cmd = ["unshare", "-rn"] + cmd; sandbox = "no-network namespace"
    try: p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env={"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "/tmp"), "NO_COLOR": "1"})
    except subprocess.TimeoutExpired: return {"status": "timeout", "findings": [], "version": ver}
    try: d = json.loads(p.stdout)
    except Exception: return {"status": "error", "findings": [], "version": ver, "note": redact(p.stderr[-300:])}
    fs = [{**{k: redact(str(v)) for k, v in x.items() if k in ("source", "severity", "guideline", "title", "detail", "file")}, "maps_to": map_finding(x)} for x in d.get("findings", [])]
    return {"status": "ok", "version": ver, "sandbox": sandbox, "artifacts": {k: str(v) for k, v in (("aab", aab), ("apk", apk), ("ipa", ipa)) if v}, "findings": fs}

_MAP = [(r"privacy ?info|xcprivacy|privacy manifest|required reason", "privacy_manifest"), (r"privacy policy", "privacy_policy_link"),
        (r"account deletion|delete account", "account_deletion_presence"), (r"NSMicrophoneUsageDescription|microphone", "ios_mic_usage"),
        (r"NSSpeechRecognition|speech", "ios_speech_usage"), (r"NSHealth|healthkit", "healthkit_usage"), (r"tracking|ATT\b|IDFA", "att_tracking"),
        (r"target ?sdk|target api", "android_target_sdk"), (r"restore", "restore_purchases"), (r"sign in with apple", "social_login_siwa"),
        (r"exact.?alarm", "exact_alarm"), (r"foreground service", "foreground_service"), (r"billing library|play billing", "play_billing_version"),
        (r"deployment target|minimum os", "ios_deployment_target"), (r"16 ?kb|page size", "page_size_16kb")]
def map_finding(x):
    t = f"{x.get('title','')} {x.get('detail','')}"
    for rx, c in _MAP:
        if re.search(rx, t, re.I): return c
    return None
# checks Greenlight is known to evaluate on an Expo/RN source tree (used for 'scanner silent vs our FAIL' disagreement)
COVERS = {"privacy_manifest", "privacy_policy_link"}  # verified 2026-10-10: v0.2.0 does NOT flag missing Expo purpose strings (expo-av/expo-audio/expo-camera), so those are not "covered"
