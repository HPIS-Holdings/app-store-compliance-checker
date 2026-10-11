# mobile-compliance-checker v0.4.0 (CLI `mcc` + MCP server `mcc-mcp`)

Static App Store / Google Play compliance checker for Expo (managed/bare) and React Native apps, packaged with the
quote-verified rules snapshot `current-rules/2026-10-10`. Use `mcc snapshot` for its current
rule count and fingerprint; do not rely on a hard-coded number. Stdlib-only Python >= 3.10.

## Output rule (hard)
**HARD RULE - verified issues only.** Report ONLY issues the checker verified from code, config, build artifact or store-listing / App Store Connect data (the `findings` list). Anything it cannot verify is DROPPED from the answer: do not soften it, hedge it, list it as "possible", or present it as a possible cause. Other verdict statuses (NEEDS_REVIEW, NOT_CHECKED, NOT_APPLICABLE) are internal coverage accounting and are never shown to the user as causes.

Excluded by design (cannot be verified from code, config, build or listing data, so never reported): lookalike / terminated-developer Guideline 4.3 flags, reply-vs-resubmit rejection loops, subscription-attachment backend glitches. Also left out: "IAP/subscription available in only one territory" - no official Apple page states it as a requirement (checked 2026-10-11).

## Install

Python 3.10+ and [pipx](https://pipx.pypa.io/):

    pipx install "git+https://github.com/HPIS-Holdings/app-store-compliance-checker.git@v0.4.0#subdirectory=mcp/server"
    mcc snapshot                             # CLI and bundled policy data
    # mcc-mcp is also installed; launch it from an MCP client (stdio)

From a clone of the repository root:

    pipx install ./mcp/server                # or: python -m pip install ./mcp/server
    uvx --from ./mcp/server mcc snapshot     # run without a permanent install
    uvx --from ./mcp/server mcc-mcp          # start the stdio server via uvx

The installed package contains its rules and lookup tables; neither command needs
to be launched from the repository folder.

Packaging smoke test (requires local `build`, setuptools>=68, and wheel):

    python mcp/server/tests/smoke_install.py

Optional: `./mcp/tools/install_greenlight.sh` installs pinned Greenlight v0.2.0.

## CLI
    mcc check <repo-or-app> [--format md|json] [--out FILE] [--platform apple|google] [--rule ID]
              [--declare eu_distribution=true] [--greenlight auto|off] [--aab F|--apk F|--ipa F] [--fail-on-review]
    mcc discover <repo>    # app roots, framework, config state, platforms
    mcc rules [--platform apple|google]
Exit codes: 0 no verified issue | 1 >=1 verified issue (rule FAIL or store finding) | 2 bad input (path missing/not a dir/'/'/outside COMPLIANCE_ALLOWED_ROOTS, bad flag) | 3 internal error | 4 NEEDS_REVIEW present with --fail-on-review.

## MCP
`mcc-mcp` speaks MCP over stdio (newline-delimited JSON-RPC 2.0, protocol 2025-06-18). Example client config:
    {"mcpServers": {"store-compliance": {"command": "mcc-mcp", "env": {"COMPLIANCE_ALLOWED_ROOTS": "/home/me/code"}}}}
Tools: `snapshot_info`, `list_rules`, `get_rule`, `list_deprecated`, `discover_apps`, `check_project`. See ../mcp-skill-draft.md.

## Store data (optional) - `.compliance/store.json` or MCP `store_data`
    {"in_app_purchases": [{"product_id": "pro.monthly", "type": "auto_renewable"}],
     "listing": {"description": "...", "terms_of_use_url": "https://..."}, "paywall": {"terms_of_use_url": "https://..."},
     "age_rating": {"questionnaire_completed": true},
     "screenshots": [{"slot": "ipad_13", "path": "store/ipad1.png"}, {"slot": "ipad_13", "width": 2064, "height": 2752}]}
Store checks and sources: ../mcp-skill-draft.md. A check whose data is missing emits nothing.

## Verdict semantics (internal; summary)
- Gates first: platform absent -> NOT_APPLICABLE (definite). Feature (rule `applies_when`) declared false -> NOT_APPLICABLE (definite);
  not detected -> NOT_APPLICABLE with `definite: false` (no signal, not proof); unresolved (dynamic app.config, declaration-only feature) -> NEEDS_REVIEW.
- FAIL only for a demonstrated violation in fully static config: used capability without its Info.plist purpose string
  (microphone, speech, HealthKit), explicit targetSdk < 36 (new/updates) or < 35 (existing), iOS deployment target < 13.
- Missing keywords (delete account, AI consent, report button, restore purchases, disclaimers) -> NEEDS_REVIEW, never FAIL.
  USE_EXACT_ALARM / SCHEDULE_EXACT_ALARM -> always NEEDS_REVIEW (alarm/calendar apps may qualify).
- PASS only for 5 fully static rules with positive evidence; `verification_level` = `source-config` (no artifact) or `release-artifact`.
- Greenlight (optional, offline, `unshare -rn` sandbox when available) is evidence only; a Greenlight finding against a PASS -> NEEDS_REVIEW.
- Evidence strings are secret-redacted; scans never follow symlinks out of the project; test/mock/tooling files are not evidence.

## Tests
    pip install "mcp>=1.10,<2" && python -m unittest discover -s mcp/server/tests -v
24 fixtures (`tests/build_fixtures.py`), 45 tests incl. a real MCP SDK client session and a malformed-input stream. Last run: tests/test-run-2026-10-11.txt.

## Third-party
`compliance_mcp/data/required_reason_apis.json` and `privacy_sdks.json` derive from store-preflight-mcp (MIT, pinned bd53be8) and were validated
against Apple's official pages fetched 2026-10-10 (`mcp/tools/import_store_preflight_tables.py`); see data/THIRD_PARTY_NOTICES.md.
Refresh the bundled rules after rebuilding a snapshot: `python mcp/tools/sync_snapshot.py 2026-10-10`.
