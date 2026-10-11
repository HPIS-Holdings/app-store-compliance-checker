"""Safe, bounded, read-only file access + secret redaction for evidence strings."""
import os, re
from pathlib import Path

MAX_FILE_BYTES = 1_000_000
MAX_FILES = 40_000
SKIP_DIRS = {"node_modules", ".git", "Pods", "build", "dist", ".expo", ".next", "DerivedData", ".gradle", "vendor",
             "fixtures", "__fixtures__", "coverage", ".turbo", ".venv", "venv", "__pycache__", ".cache"}
TEXT_EXT = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".json", ".xml", ".plist", ".gradle", ".kts", ".properties",
            ".xcprivacy", ".entitlements", ".py", ".yaml", ".yml", ".swift", ".m", ".kt", ".java", ".dart", ".md", ".html"}
NON_APP_PARTS = {"__tests__", "__mocks__", "test", "tests", "e2e", "scripts", "tools", "docs", "examples", "storybook", ".storybook", "mocks"}
CODE_EXT = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".py", ".swift", ".m", ".kt", ".java", ".dart"}

class PathError(ValueError): pass

def resolve_project(path, allowed_roots=None):
    """Validate a user-supplied project path: must exist, be a directory, not '/', and (if
    COMPLIANCE_ALLOWED_ROOTS is set) lie inside one of the allowed roots."""
    if not isinstance(path, str) or not path.strip(): raise PathError("project_path must be a non-empty string")
    p = Path(path).expanduser()
    try: p = p.resolve(strict=True)
    except (FileNotFoundError, RuntimeError, OSError): raise PathError(f"project_path does not exist: {path}")
    if not p.is_dir(): raise PathError(f"project_path is not a directory: {path}")
    if p == Path(p.anchor): raise PathError("refusing to scan a filesystem root")
    roots = allowed_roots if allowed_roots is not None else [r for r in os.environ.get("COMPLIANCE_ALLOWED_ROOTS", "").split(os.pathsep) if r]
    if roots and not any(_inside(p, Path(r).expanduser().resolve()) for r in roots):
        raise PathError(f"project_path outside COMPLIANCE_ALLOWED_ROOTS: {path}")
    return p

def _inside(p, root):
    try: p.relative_to(root); return True
    except ValueError: return False

class Tree:
    """Bounded listing of text files under root. Never follows symlinks; skips files whose real path leaves root."""
    def __init__(self, root, skip_dirs=SKIP_DIRS, exclude=()):
        self.root = Path(root); self.files = []; self.truncated = False; self.skipped_large = 0; self.skipped_links = 0
        excl = {Path(e).resolve() for e in exclude}
        for dp, dn, fn in os.walk(self.root, followlinks=False):
            d = Path(dp)
            dn[:] = [x for x in dn if x not in skip_dirs and not (x.startswith(".") and x not in (".github",)) and (d / x).resolve() not in excl]
            for f in fn:
                fp = d / f
                if fp.suffix not in TEXT_EXT: continue
                if fp.is_symlink():
                    if not _inside(fp.resolve(), self.root.resolve()): self.skipped_links += 1; continue
                try:
                    if fp.stat().st_size > MAX_FILE_BYTES: self.skipped_large += 1; continue
                except OSError: continue
                self.files.append(fp)
                if len(self.files) >= MAX_FILES: self.truncated = True; return
        self._cache = {}
    def text(self, p):
        if not hasattr(self, "_cache"): self._cache = {}
        if p not in self._cache:
            try: self._cache[p] = p.read_text(errors="replace")
            except OSError: self._cache[p] = ""
        return self._cache[p]
    def rel(self, p, base=None):
        try: return str(Path(p).relative_to(base or self.root))
        except ValueError: return str(p)
    def grep(self, pattern, code_only=True, limit=10, base=None, flags=re.I, exts=None):
        """Search app source. Test/mocks/tooling files are excluded so evidence reflects shipped code."""
        rx = re.compile(pattern, flags); hits = []
        for f in self.files:
            if code_only and f.suffix not in (exts or CODE_EXT): continue
            rel = f.relative_to(self.root).parts
            if any(x in NON_APP_PARTS for x in rel[:-1]) or ".test." in f.name or ".spec." in f.name or f.name.startswith(("jest.", "vitest.", "playwright.", "detox.")): continue
            for i, line in enumerate(self.text(f).splitlines(), 1):
                if rx.search(line):
                    hits.append(redact(f"{self.rel(f, base)}:{i}: {line.strip()[:160]}"))
                    if len(hits) >= limit: return hits
        return hits

_SECRET_PATTERNS = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "[REDACTED:aws-key]"),
    (re.compile(r"\b(sk|rk|pk)_(live|test)_[A-Za-z0-9]{10,}"), "[REDACTED:stripe-key]"),
    (re.compile(r"\bsk-(proj-|ant-)?[A-Za-z0-9_\-]{16,}"), "[REDACTED:api-key]"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"), "[REDACTED:github-token]"),
    (re.compile(r"\bxox[abprs]-[A-Za-z0-9\-]{10,}"), "[REDACTED:slack-token]"),
    (re.compile(r"\bAIza[0-9A-Za-z_\-]{35}"), "[REDACTED:google-api-key]"),
    (re.compile(r"\b(appl|goog|amzn|strp)_[A-Za-z0-9]{16,}"), "[REDACTED:revenuecat-key]"),
    (re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{5,}"), "[REDACTED:jwt]"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "[REDACTED:private-key]"),
    (re.compile(r"(?i)\b([A-Z0-9_]*(api[_-]?key|secret|token|password|passwd|auth|private[_-]?key)[A-Z0-9_]*)(\s*[:=]\s*)(['\"`]?)([^'\"`\s,;)]{6,})"),
     lambda m: f"{m.group(1)}{m.group(3)}{m.group(4)}[REDACTED]"),
]
def redact(s):
    for rx, rep in _SECRET_PATTERNS: s = rx.sub(rep, s)
    return s
