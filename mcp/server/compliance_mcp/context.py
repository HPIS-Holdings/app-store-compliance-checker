"""Per-app scan context: static config, dependencies, permissions, plist keys, file trees (app + repo backend)."""
import json, re
from pathlib import Path
from .safety import Tree
from .discovery import app_config

BACKEND_DIRS = ("infra", "convex", "server", "backend", "api", "functions", "supabase", "worker", "workers", "services", "lambda", "cloud-functions",
                "packages", "libs", "shared", "modules")  # backend + monorepo shared code the app may import

class AppContext:
    def __init__(self, app_root, repo_root=None, framework="expo-managed", platforms=None, declared=None, other_app_roots=()):
        self.root = Path(app_root); self.repo = Path(repo_root or app_root); self.framework = framework
        self.platforms = platforms or {"ios": "assumed", "android": "assumed"}
        self.declared = declared or {}
        self.tree = Tree(self.root)
        # backend code anywhere in the repo (monorepo servers, convex/, supabase functions), excluding other apps
        cand = [self.repo / d for d in BACKEND_DIRS]
        if self.root.parent != self.repo and self.root.parent.is_relative_to(self.repo): cand += [self.root.parent / d for d in BACKEND_DIRS]
        seen = set(); self.backend = []
        for c in cand:
            if c.is_dir() and c != self.root and self.root not in c.parents and c not in self.root.parents and c.resolve() not in seen:
                seen.add(c.resolve()); self.backend.append(Tree(c))
        cfg = app_config(self.root); self.expo = cfg["expo"] or {}; self.config_state = cfg["state"]; self.config_resolved = cfg["resolved"]
        self.dynamic_files = cfg["dynamic_files"]
        pk = self._json("package.json") or {}
        self.deps = {**(pk.get("dependencies") or {}), **(pk.get("devDependencies") or {})}
        self.coverage = {"app_files_scanned": len(self.tree.files), "truncated": self.tree.truncated, "skipped_large_files": self.tree.skipped_large,
                         "skipped_escaping_symlinks": self.tree.skipped_links, "backend_dirs": [str(t.root.relative_to(self.repo)) if t.root.is_relative_to(self.repo) else str(t.root) for t in self.backend],
                         "config_state": self.config_state}
        self.dynamic_literals = self._dynamic_literals()
        self.derived = self._derived_defaults()
    def _dynamic_literals(self):
        """Static read of app.config.* (NEVER executed): literal purpose strings / permissions / plugin names with file:line."""
        out = {"purpose_strings": {}, "permissions": [], "plugins": [], "spreads_static_config": False, "env_dependent_keys": []}
        for n in self.dynamic_files:
            try: L = (self.root / n).read_text(errors="replace").splitlines()
            except OSError: continue
            for i, l in enumerate(L, 1):
                for m in re.finditer(r"(NS\w+UsageDescription|\w+Permission)['\"]?\s*:\s*(['\"`])([^'\"`$]*)\2", l): out["purpose_strings"][m.group(1)] = (f"{n}:{i}", m.group(3))
                for m in re.finditer(r"(NS\w+UsageDescription|\w+Permission)['\"]?\s*:\s*(process\.env|`[^`]*\$\{)", l): out["env_dependent_keys"].append(f"{m.group(1)} @ {n}:{i}")
                for m in re.finditer(r"['\"](android\.permission\.[A-Z_]+|[A-Z][A-Z_]{5,}_?[A-Z]*)['\"]", l):
                    if "permission" in l.lower() or m.group(1).startswith("android.permission"): out["permissions"].append((m.group(1).replace("android.permission.", ""), f"{n}:{i}"))
                for m in re.finditer(r"['\"]((?:@[\w-]+/)?[\w-]*(?:expo|react-native)[\w/-]*)['\"]", l):
                    if "plugin" in " ".join(L[max(0, i - 15):i]).lower(): out["plugins"].append(m.group(1))
                if re.search(r"\.\.\.\s*config\b|\.\.\.\s*\(?\s*config", l): out["spreads_static_config"] = True
        out["plugins"] = sorted(set(out["plugins"]))
        return out
    def _derived_defaults(self):
        """Vendor-documented defaults for Expo managed apps without overriding plugins (data/expo_sdk_defaults.json)."""
        try: t = json.loads((Path(__file__).parent / "data/expo_sdk_defaults.json").read_text())
        except Exception: return {}
        m = re.search(r"(\d+)\.", str(self.deps.get("expo", ""))); row = t["by_sdk_major"].get(m.group(1)) if m else None
        if not row or self.framework != "expo-managed": return {}
        override = [p for p in (self.expo.get("plugins") or []) if (p[0] if isinstance(p, list) else p) in ("expo-build-properties",)] + \
                   [p for p in self.dynamic_literals["plugins"] if "build-properties" in p]
        return {"expo_sdk": m.group(1), "targetSdkVersion": row["targetSdkVersion"], "ios_min": row["ios_min"], "xcode_min": row["xcode_min"],
                "source": t["source"], "fetched": t["fetched"], "overridden_by": [str(o)[:60] for o in override], "basis": "vendor-default (not a release-artifact fact)"}
    @property
    def complete(self): return self.config_resolved and not self.tree.truncated
    def _json(self, n):
        try: return json.loads((self.root / n).read_text())
        except Exception: return None
    def has_dep(self, *names): return [n for n in names if n in self.deps]
    def plugin(self, name):
        for p in self.expo.get("plugins") or []:
            if isinstance(p, list) and p and p[0] == name: return p[1] if len(p) > 1 and isinstance(p[1], dict) else {}
            if p == name: return {}
        return None
    def plist(self):
        d = {}
        for k, v in ((self.expo.get("ios") or {}).get("infoPlist") or {}).items(): d[k] = ("app.json ios.infoPlist", v)
        for pl in self.expo.get("plugins") or []:
            if isinstance(pl, list) and len(pl) > 1 and isinstance(pl[1], dict):
                for k, v in pl[1].items():
                    if isinstance(v, str) and (k.startswith("NS") or k.endswith("Permission")): d.setdefault(k, (f"app.json plugin {pl[0]}", v))
        for f in self.tree.files:
            if f.name == "Info.plist":
                t = self.tree.text(f)
                for m in re.finditer(r"<key>(\w+)</key>\s*<string>([^<]*)</string>", t): d.setdefault(m.group(1), (self.tree.rel(f), m.group(2)))
        return d
    def android_permissions(self):
        perms = {}
        for p in (self.expo.get("android") or {}).get("permissions") or []:
            perms[str(p).replace("android.permission.", "")] = "app.json android.permissions"
        for f in self.tree.files:
            if f.name == "AndroidManifest.xml":
                for m in re.finditer(r'<uses-permission[^>]*android:name="([^"]+)"', self.tree.text(f)):
                    perms.setdefault(m.group(1).replace("android.permission.", ""), self.tree.rel(f))
        return perms
    def grep_all(self, pattern, limit=8, code_only=True):
        hits = self.tree.grep(pattern, code_only=code_only, limit=limit)
        for t in self.backend:
            if len(hits) >= limit: break
            hits += [f"[backend {t.root.name}] {h}" for h in t.grep(pattern, code_only=code_only, limit=limit - len(hits))]
        return hits
