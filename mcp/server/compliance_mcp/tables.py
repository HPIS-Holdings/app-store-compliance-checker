"""Validated tables (see data/THIRD_PARTY_NOTICES.md)."""
import json, re
from pathlib import Path
DATA = Path(__file__).parent / "data"
def _load(n):
    try: return json.loads((DATA / n).read_text())
    except Exception: return None
def required_reason_summary(ctx, declared):
    t = _load("required_reason_apis.json")
    if not t: return ["required-reason table unavailable"]
    out = []
    for c in t["categories"]:
        if not c["category_validated"]: continue
        trig = [x for x in c["triggers"] if (x["kind"] == "dependency" and x["value"] in ctx.deps)]
        if trig or c["category"] in declared:
            codes = [x["code"] for x in c["codes"] if x["validated"]]
            out.append(f"{c['category']}: {'declared' if c['category'] in declared else 'NOT declared'}; trigger deps {[x['value'] for x in trig]}; valid reason codes {codes}")
    return out or ["no required-reason trigger dependency matched (native code not scanned; React Native core itself uses UserDefaults/file-timestamp APIs)"]
def listed_sdks_in_deps(ctx):
    t = _load("privacy_sdks.json")
    if not t: return []
    names = {s["sdk"].lower(): s["sdk"] for s in t["sdks"] if s["validated"]}
    hits = []
    for d in ctx.deps:
        key = d.split("/")[-1].lower().replace("react-native-", "").replace("-", "")
        for n, orig in names.items():
            if n.replace("_", "") == key or (d.startswith("@react-native-firebase/") and orig.lower() == "firebase" + key):
                hits.append(f"dependency {d} -> Apple-listed SDK {orig}")
    for d in t.get("npm_dependencies_bundling_listed_sdks_upstream_unvalidated", []):
        if d in ctx.deps and not any(d in h for h in hits): hits.append(f"dependency {d} bundles a listed SDK (upstream mapping, not validated)")
    return hits
def validated_sdk_names():
    t = _load("privacy_sdks.json")
    return [s["sdk"] for s in t["sdks"] if s["validated"]] if t else []
def listed_sdk_pairs(ctx):
    """(npm dependency, Apple-listed SDK) pairs, validated name mappings only."""
    t = _load("privacy_sdks.json")
    if not t: return []
    names = {s["sdk"].lower(): s["sdk"] for s in t["sdks"] if s["validated"]}; out = []
    for d in ctx.deps:
        key = d.split("/")[-1].lower().replace("react-native-", "").replace("-", "")
        for n, orig in names.items():
            if n.replace("_", "") == key or (d.startswith("@react-native-firebase/") and orig.lower() == "firebase" + key): out.append((d, orig))
    return out
