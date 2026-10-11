"""App-root discovery: Expo managed/bare, React Native, native Android, native iOS, Flutter, Capacitor; monorepos.
Config resolution: app.json is parsed statically; app.config.js/ts is NEVER executed -> marked dynamic/unresolved."""
import json, os, re
from pathlib import Path
from .safety import SKIP_DIRS

SUPPORTED = {"expo-managed", "expo-bare", "react-native"}

def _json(p):
    try: return json.loads(Path(p).read_text())
    except Exception: return None

def _walk(root, maxdepth=5):
    for dp, dn, fn in os.walk(root, followlinks=False):
        d = Path(dp); depth = len(d.relative_to(root).parts)
        dn[:] = [x for x in dn if x not in SKIP_DIRS and not x.startswith(".") and depth < maxdepth]
        yield d, dn, fn

def app_config(root):
    root = Path(root)
    static = _json(root / "app.json")
    dyn = [n for n in ("app.config.js", "app.config.ts", "app.config.mjs", "app.config.cjs") if (root / n).exists()]
    expo = (static or {}).get("expo", static or {}) if isinstance(static, dict) else {}
    if dyn: state = "dynamic-unresolved" if not static else "static+dynamic-unresolved"
    elif static is not None: state = "static"
    else: state = "none"
    return {"expo": expo, "state": state, "dynamic_files": dyn, "resolved": state == "static"}

def platforms(root, framework, cfg):
    root = Path(root); has_ios, has_android = (root / "ios").is_dir(), (root / "android").is_dir()
    if framework == "android-native": return {"ios": "absent", "android": "present"}
    if framework == "ios-native": return {"ios": "present", "android": "absent"}
    if framework == "expo-managed":
        pl = (cfg or {}).get("expo", {}).get("platforms")
        if isinstance(pl, list): return {"ios": "declared" if "ios" in pl else "absent", "android": "declared" if "android" in pl else "absent"}
        return {"ios": "assumed", "android": "assumed"}
    return {"ios": "present" if has_ios else "unknown", "android": "present" if has_android else "unknown"}

def discover(repo):
    repo = Path(repo); roots = []
    claimed = []
    for d, dn, fn in _walk(repo):
        if any(d == c or c in d.parents for c in claimed): continue
        if "package.json" in fn:
            pk = _json(d / "package.json") or {}
            deps = {**(pk.get("dependencies") or {}), **(pk.get("devDependencies") or {})}
            has_cfg = any((d / n).exists() for n in ("app.json", "app.config.js", "app.config.ts", "app.config.mjs", "app.config.cjs"))
            if "expo" in deps and has_cfg:
                fw = "expo-bare" if ((d / "ios").is_dir() or (d / "android").is_dir()) else "expo-managed"
            elif "react-native" in deps and ((d / "ios").is_dir() or (d / "android").is_dir()):
                fw = "react-native"
            elif "@capacitor/core" in deps: fw = "capacitor"
            else: fw = None
            if fw:
                cfg = app_config(d)
                roots.append({"path": d, "framework": fw, "versions": {k: deps.get(k) for k in ("expo", "react-native", "@capacitor/core") if deps.get(k)},
                              "config": {k: v for k, v in cfg.items() if k != "expo"}, "platforms": platforms(d, fw, {"expo": cfg["expo"]}),
                              "supported": fw in SUPPORTED}); claimed.append(d); continue
        if "pubspec.yaml" in fn and re.search(r"^\s*flutter\s*:", (d / "pubspec.yaml").read_text(errors="replace"), re.M):
            roots.append({"path": d, "framework": "flutter", "versions": {}, "config": {"state": "n/a"}, "platforms": {"ios": "present" if (d / "ios").is_dir() else "unknown", "android": "present" if (d / "android").is_dir() else "unknown"}, "supported": False}); claimed.append(d); continue
        if any(x in fn for x in ("settings.gradle", "settings.gradle.kts")) and list(d.glob("*/src/main/AndroidManifest.xml")):
            roots.append({"path": d, "framework": "android-native", "versions": {}, "config": {"state": "n/a"}, "platforms": platforms(d, "android-native", None), "supported": False}); claimed.append(d); continue
        if any(x.endswith(".xcodeproj") for x in dn):
            roots.append({"path": d, "framework": "ios-native", "versions": {}, "config": {"state": "n/a"}, "platforms": platforms(d, "ios-native", None), "supported": False}); claimed.append(d); continue
    root_pkg = _json(repo / "package.json") or {}
    mono = len(roots) > 1 or bool(root_pkg.get("workspaces")) or (repo / "pnpm-workspace.yaml").exists() or (repo / "turbo.json").exists()
    return {"monorepo": mono, "apps": roots}
