# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/) and the project uses [Semantic Versioning](https://semver.org/).

## [0.4.0] - 2026-10-11
First public open-source release.

### Added
- `mcc` CLI and `mcc-mcp` stdio MCP server in one zero-dependency Python package, installable with `pipx install "git+https://github.com/HPIS-Holdings/app-store-compliance-checker.git@v0.4.0#subdirectory=mcp/server"`.
- **Proof-only output**: only findings verified from code, config, build artifact or supplied store data are reported; unverifiable items are dropped.
- New Apple checks: microphone, speech-recognition and HealthKit usage descriptions; iOS 13 minimum deployment target; account-deletion support; privacy label; EU DPLA terms.
- Bundled rules snapshot `2026-10-10`: 102 quote-verified rules (53 Apple, 49 Google) with official URLs.
- Portable Agent Skill (`mcp/skill/store-compliance`), client setup guides for Claude Desktop, Claude Code, Cursor and VS Code.
- Composite GitHub Action (`action.yml`) that fails only on evidence-backed problems, plus an example workflow.
- Optional Greenlight v0.2.0 integration for `.ipa`/`.apk`/`.aab` artifacts (checksum-verified installer).

[0.4.0]: https://github.com/HPIS-Holdings/app-store-compliance-checker/releases/tag/v0.4.0
