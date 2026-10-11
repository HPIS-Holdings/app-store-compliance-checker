# Contributing

Thanks for helping developers ship without surprise rejections!

## Ground rules
- **Proof-only.** A new check must report a finding only when it has concrete evidence (file + line, config key, artifact field or supplied store data). If it can't be proven statically, it doesn't belong in `findings`.
- **Official sources only.** Every rule cites an official Apple or Google URL and quotes the requirement verbatim, with the date it was fetched. Community reports can inform tests, never rules.
- **Zero runtime dependencies.** The package uses only the Python standard library (3.10+).
- **Generic fixtures.** Test fixtures use made-up apps (`com.example.*`), never real apps or personal data.

## Development
```bash
cd mcp/server
python -m pip install -e ".[test]"
python -m unittest discover -s tests -v
python tests/smoke_install.py        # packaging smoke test (needs build, wheel)
```

## Adding or updating a rule
1. Add/modify the rule in `current-rules/<snapshot>/` with `official_url`, verbatim quote and fetch date.
2. Sync the bundled copy: `python mcp/tools/sync_snapshot.py`.
3. Implement the check in `mcp/server/compliance_mcp/checks.py` or `store_checks.py`.
4. Add a passing and a failing fixture and tests in `tests/test_checker.py`.
5. Note the change in `CHANGELOG.md`.

## Pull requests
Keep PRs focused, describe the evidence the check relies on, and make sure tests pass. By contributing you agree your contribution is licensed under the MIT License.
