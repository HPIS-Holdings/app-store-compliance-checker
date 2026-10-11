# Policy diff: 2026-10-10 vs 2026-10-09 baseline

Method (factual): every source in `sources.yaml` was re-fetched on 2026-10-10 (14:35-14:37 UTC) and its normalized-text SHA-256 compared to the committed Oct 9 state (`sources/state/*.json`, fetched 2026-10-09 11:26-12:59 UTC). The App Store Review Guidelines and Google Play Developer Program Policy were re-split into sections and section hashes compared to `index/sections/*.json` (Oct 9).

## Result summary
| Comparison | Result |
|---|---|
| Apple pages (16 with baseline) | all text hashes identical |
| Google pages (18 with baseline) | identical except the consolidated Developer Program Policy |
| App Store Review Guidelines sections | 0 added, 0 removed, 0 changed (page "last updated" still June 8, 2026) |
| Google Developer Program Policy sections | 0 added, 0 removed, **1 changed: Subscriptions** (`GPL-SUBSCRIPTIONS`) |
| New sources without baseline | NSMicrophoneUsageDescription, NSSpeechRecognitionUsageDescription (Apple docs), Android 14 schedule-exact-alarms page, Apple medical-device status URL (soft 404) |

## Meaningful changes by topic
- **Subscriptions (Google):** `GPL-SUBSCRIPTIONS` section hash changed between Oct 9 and Oct 10. Character count (7,121) and must/must-not/should/required counts are identical. The Oct 9 full text was not kept in the cache, so **the exact change cannot be shown**; it is a same-length edit (possibly character/formatting-level). Treat repo rule GPL-SUBSCRIPTIONS as NEEDS_REVIEW until it is re-read (`deprecated-exclusions.jsonl` lists it as TEXT_CHANGED_SINCE_BASELINE). Current quotes in CUR-GPL-SUBS were verified against today's text.
- **Health, AI, privacy, permissions (both platforms):** no text change in a day. Wording verified today in the current rules: Apple 5.1.2(i) "including with third-party AI" explicit-permission rule; Google AI-Generated Content in-app reporting; Google health "not a medical device" description disclaimer; Health Connect limited use.
- **Developer requirements:** no text change in a day. Date-driven status as of 2026-10-10 (from page text, not a text change):
  - Apple: Xcode 26 / iOS 26 SDK uploads (since 2026-04-28) and iOS 13 minimum target (since 2026-09-09) are in force.
  - Apple EU: earlier EU addenda superseded by DPLA Attachment 14 as of 2026-10-01.
  - Google: target API 36 for new apps/updates since 2026-08-31; extension window ends 2026-11-01. Play Billing Library 7 extension ends 2026-11-01.
  - Google US programs: service-fee reporting started 2026-10-01; download reporting deadline extended to 2026-12-01.
  - Google: 16 KB page-size update block from 2027-02-01; developer verification protections started 2026-09-30 in BR/ID/SG/TH.

## What the Oct 9 repo had that today's packet corrects/adds
- `CUR-*` rules carry today's verified quotes for 84 requirements; 1 repo rule flagged (GPL-SUBSCRIPTIONS). No repo rule was proven deprecated by today's text.
- The Apple US external-purchase entitlement page now redirects to /support/ (DEP-APL-US-ENTITLEMENT-PAGE, UNKNOWN); 3.1.1(a) text is the current source.
