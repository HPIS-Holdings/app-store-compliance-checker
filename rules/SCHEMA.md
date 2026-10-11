# Rule schema and labelling

Rules are authored in `rules/**/*.yaml` and compiled by `scripts/build_index.py` into
`index/rules.json` (full), `index/rules.jsonl` (compact, one rule per line) and `index/topics.json`,
plus generated markdown in `apple/policies/`, `google/policies/`, `shared-topics/`.
Never edit generated files by hand.

## Rule IDs (stable)
| Prefix | Meaning | Example |
|---|---|---|
| `APL-<n>` | Apple App Store Review Guidelines, publisher number preserved (letter suffix = Apple sub-letter, `v` = 5.1.1(v)) | `APL-3.1.1`, `APL-3.1.2c`, `APL-5.1.1v` |
| `APL-INTRO`, `APL-BEFORE-SUBMIT`, `APL-AFTER-SUBMIT` | Unnumbered parts of the Apple guidelines page | |
| `APL-SUPP-*` | Rules from other official Apple pages (support pages, DPLA, Upcoming Requirements) | `APL-SUPP-SDK-MIN-XCODE26` |
| `GPL-<HEADING-SLUG>` | Google Play Developer Program Policy section; slug of the official heading (Google does not number policies). `-2` = repeated heading | `GPL-PAYMENTS`, `GPL-SPAM-2` |
| `GPL-SUPP-*` | Rules from Play Console Help / Android Developers pages | `GPL-SUPP-TARGET-API-2026` |
| `XPL-*` | Cross-platform implementation rules (Expo / React Native / RevenueCat) | `XPL-MIC-001` |

IDs never change once published; if a publisher renumbers, add a new rule and mark the old one superseded in `policy-changelog/`.

## Labels (`label`)
| Value | Rendered as | Meaning |
|---|---|---|
| `official_requirement` | Official requirement | Paraphrase of mandatory publisher text (must / may not / required / will be rejected) |
| `official_recommendation` | Official recommendation | Publisher text using should / encourage / best practice |
| `community_experience` | Community experience | Reported by developers (forums, Reddit, GitHub); never policy |
| `interpretation` | Interpretation | Our synthesis; must cite `related_rules`; never policy |
| `vendor_documentation` | Vendor documentation (not store policy) | Expo, RevenueCat, React Native docs |

Within a rule, fields carry their own epistemic status:
* `requires`, `prohibited`, `exceptions_regions`, `dpla_reference` — paraphrase of the official text cited in `sources`.
* `enforcement_risk` — official where the publisher states the consequence; otherwise marked "(Interpretation)" or "(Community experience)".
* `implementation`, `examples`, `agent_verification` — Interpretation unless explicitly attributed.
* `uncertainty` — what we could not confirm.

## Obligation (`obligation`)
`mandatory` (applies to all apps), `conditional` (applies when a feature/category/region is present),
`recommended` (official should-level), `informational` (headings, process descriptions, omitted numbers).
`unknown` is used only for `extracted-only` index entries.

## Analysis status
* `analyzed` — a human/agent read the official section text and wrote the fields.
* `extracted-only` — section text was fetched, hashed and excerpted, but no analysis has been written. Do not rely on it beyond the excerpt; read the source.

## Verification
`verification.first_pass` is the author read; `verification.second_pass` entries come from `qc/verification-log.json`
(independent re-check of the claim against a fresh fetch of the source text).
