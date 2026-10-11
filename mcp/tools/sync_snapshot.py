#!/usr/bin/env python3
"""Copy the rules snapshot into the installable package (compliance_mcp/data) and write snapshot.json."""
import hashlib, json, shutil, sys, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; SNAP = sys.argv[1] if len(sys.argv) > 1 else "2026-10-10"
src = ROOT / "current-rules" / SNAP; dst = ROOT / "mcp/server/compliance_mcp/data"
shutil.copy(src / f"current-rules-{SNAP}.jsonl", dst / "current-rules.jsonl"); shutil.copy(src / "deprecated-exclusions.jsonl", dst / "deprecated-exclusions.jsonl")
rules = [json.loads(l) for l in open(dst / "current-rules.jsonl")]; dep = [json.loads(l) for l in open(dst / "deprecated-exclusions.jsonl")]
meta = {"snapshot": SNAP, "source_dir": f"current-rules/{SNAP}", "rules_by_platform": dict(collections.Counter(r["platform"] for r in rules)),
        "exclusions_by_status": dict(collections.Counter(d.get("status") for d in dep)),
        "rules_sha256": hashlib.sha256((dst / "current-rules.jsonl").read_bytes()).hexdigest()}
json.dump(meta, open(dst / "snapshot.json", "w"), indent=1); print(meta)
