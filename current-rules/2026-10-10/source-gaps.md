# Source gaps (high-impact only), prioritized by verdict impact - 2026-10-10

| # | Gap | Rules whose verdict depends on it | Why it matters | Next step |
|---|---|---|---|---|
| 1 | Apple **regulated medical device status** declaration page: the URL `developer.apple.com/help/app-store-connect/manage-compliance-information/declare-regulated-medical-device-status/` returns a soft 404 (200 with generic page) | CUR-APL-1.4.1-*, EU MDR equivalents | An app's medical-device status decides whether Apple requires a declaration; current wording could not be verified | Find the current ASC Help URL via the ASC Help index; re-fetch |
| 2 | Oct 9 full text of Google **Subscriptions** section not retained | CUR-GPL-SUBS, repo GPL-SUBSCRIPTIONS | Section changed in the last day; diff unknown | Keep section text per snapshot in cache (done for Oct 10); compare next run |
| 3 | Apple **DPLA Schedule 2** (subscription disclosure terms) not fetched | CUR-APL-3.1.2c-INFO | 3.1.2(c) defers to Schedule 2; paywall checks rely on community reports for Terms/EULA links | Fetch public DPLA PDF/HTML |
| 4 | Play Console **login-only** forms: Health apps declaration, Data safety, Health Connect declaration, Payments profile | CUR-GPL-HEALTH-DECL*, CUR-GPL-DATASAFETY, CUR-GPL-HC-* | Always NEEDS_REVIEW: cannot be confirmed from repo | Owner exports/screenshots as evidence |
| 5 | Mapping **react-native-purchases version -> bundled Play Billing Library version** (RevenueCat changelog) | CUR-GPL-PBL | PBL 7 extension ends 2026-11-01; checker can't decide PASS/FAIL | Fetch RevenueCat Android SDK changelog |
| 6 | Mapping **Expo SDK / React Native version -> default targetSdk and 16 KB alignment** (official Expo/RN docs) | CUR-GPL-TAPI-*, CUR-GPL-16KB* | Projects without explicit targetSdkVersion get NEEDS_REVIEW | Fetch Expo SDK 54/55 changelog |
| 7 | Health Connect **data-access declaration / approved use-case list** help page | CUR-GPL-HC-USECASE | Whether chronic-condition management is an approved use case | Locate and fetch Play Help article |
| 8 | **DPLA Attachment 14** text | CUR-APL-EU-DPLA | EU business terms since 2026-10-01 | Fetch if public |
| 9 | No microphone-specific Play policy located | CUR-GPL-PERMS | Voice logging judged only under general permissions/prominent disclosure | Confirm in permissions help pages |
