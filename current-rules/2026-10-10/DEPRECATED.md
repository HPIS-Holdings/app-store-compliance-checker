# Deprecated / superseded / excluded - snapshot 2026-10-10

CONFIRMED = official text fetched 2026-10-10 states it (quoted). UNKNOWN = no official statement found; not treated as deprecated.

## DEP-APL-EU-ADDENDA - CONFIRMED
- Item: Alternative Terms Addendum for Apps in the EU; StoreKit External Purchase Link Entitlement (EU) Addendum
- Source: https://developer.apple.com/support/dma-and-apps-in-the-eu/ (final URL https://developer.apple.com/support/apps-in-the-eu, HTTP 200)
  > the Alternative Terms Addendum for Apps in the EU and StoreKit External Purchase Link Entitlement (EU) Addendum have been phased out
  > As of October 1, 2026, these terms have been superseded by Attachment 14 of the Apple Developer Program License Agreement.
- Replaced by: DPLA Attachment 14 (CUR-APL-EU-DPLA)
- Effective: 2026-10-01

## DEP-APL-US-ENTITLEMENT-PAGE - UNKNOWN
- Item: Support page 'Distributing apps in the U.S. that provide an external purchase link' (developer.apple.com/support/storekit-external-entitlement-us/)
- Source: https://developer.apple.com/support/storekit-external-entitlement-us/ (final URL https://developer.apple.com/support/, HTTP 200)
- Replaced by: Guideline 3.1.1(a): entitlements not required for US storefront links (CUR-APL-3.1.1a-LINKS)
- Effective: None
- Note: On 2026-10-10 the URL redirected to https://developer.apple.com/support/ (generic page). No official deprecation notice found; treat page content as not current.

## DEP-APL-XCODE15 - CONFIRMED
- Item: Xcode 15 / iOS 17 SDK minimum (since April 29, 2024)
- Source: https://developer.apple.com/news/upcoming-requirements/ (final URL https://developer.apple.com/news/upcoming-requirements/, HTTP 200)
  > Apps uploaded to App Store Connect must be built with Xcode 26 or later
- Replaced by: CUR-APL-UR-XCODE26
- Effective: 2026-04-28
- Note: Superseded by the later, stricter Xcode 26 requirement on the same page (inference from the newer entry; the page does not use the word 'superseded').

## DEP-APL-XML-FEED - CONFIRMED
- Item: App Store Connect XML feed (IAP/metadata/pricing; Game Center)
- Source: https://developer.apple.com/news/upcoming-requirements/ (final URL https://developer.apple.com/news/upcoming-requirements/, HTTP 200)
  > Game Center management will no longer be supported by the XML feed as of July 15, 2024.
- Replaced by: App Store Connect API
- Effective: 2024-07-15

## DEP-APL-SUBS-REPORT-1.2 - CONFIRMED
- Item: Subscription reports version 1.2
- Source: https://developer.apple.com/news/upcoming-requirements/ (final URL https://developer.apple.com/news/upcoming-requirements/, HTTP 200)
  > Subscription reports version 1.2 will no longer be available as of March 1, 2023.
- Replaced by: version 1.3
- Effective: 2023-03-01

## DEP-APL-SHA1-RECEIPT - CONFIRMED
- Item: SHA-1 App Store receipt signing intermediate certificate
- Source: https://developer.apple.com/news/upcoming-requirements/ (final URL https://developer.apple.com/news/upcoming-requirements/, HTTP 200)
  > The SHA-1 intermediate certificate used for signing App Store receipts expires on January 24, 2025.
- Replaced by: SHA-256 / AppTransaction and Transaction APIs
- Effective: 2025-01-24

## DEP-GPL-PBL-5-6-7 - CONFIRMED
- Item: Play Billing Library 5, 6 (past deadlines) and 7 (new app/update deadline August 31, 2026; extension November 1, 2026)
- Source: https://developer.android.com/google/play/billing/deprecation-faq (final URL https://developer.android.com/google/play/billing/deprecation-faq, HTTP 200)
  > All versions of the Google Play Billing Library have a two-year deprecation cycle.
  > August 31, 2026
  > November 1, 2026
- Replaced by: PBL 8+ (CUR-GPL-PBL)
- Effective: 2026-08-31
- Note: Version-date pairing read from table order (cells fetched as separate lines).

## DEP-GPL-TAPI-35-NEW - CONFIRMED
- Item: Target API 35 as the requirement for new apps/updates (August 31, 2025)
- Source: https://support.google.com/googleplay/android-developer/answer/11926878?hl=en (final URL https://support.google.com/googleplay/android-developer/answer/11926878?hl=en, HTTP 200)
  > New apps and app updates must target Android 16 (API level 36) or higher to be submitted to Google Play
- Replaced by: CUR-GPL-TAPI-NEW
- Effective: 2026-08-31

## DEP-GPL-DELETION-BADGE - CONFIRMED
- Item: Previous Play data deletion badge
- Source: https://support.google.com/googleplay/android-developer/answer/13327111?hl=en (final URL https://support.google.com/googleplay/android-developer/answer/13327111?hl=en, HTTP 200)
  > The previous data deletion badge will be removed and no longer shown for all apps.
- Replaced by: Data deletion area in Data safety
- Effective: None

## DEP-GPL-CRANE-PILOT - CONFIRMED
- Item: Online Crane Games pilot in Japan
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en (final URL https://support.google.com/googleplay/android-developer/answer/18258653?hl=en, HTTP 200)
  > The Online Crane Games pilot in Japan ended on July 11, 2023.
- Replaced by: Global listing subject to law (from July 12, 2023)
- Effective: 2023-07-11

## DEP-GPL-US-DL-REPORTING-OCT1 - CONFIRMED
- Item: October 1, 2026 date for external-content-links download reporting/fees
- Source: https://support.google.com/googleplay/android-developer/answer/15582165?hl=en (final URL https://support.google.com/googleplay/android-developer/answer/15582165?hl=en, HTTP 200)
  > they now have until December 1, 2026 to report successful download and pay the relevant service fees.
- Replaced by: December 1, 2026 (CUR-GPL-US-PROGRAMS)
- Effective: 2026-09-17

## DEP-GPL-EXACT-ALARM-WORDING - UNKNOWN
- Item: Exact Alarm Permission section wording 'will be introduced' (Android 13)
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en (final URL https://support.google.com/googleplay/android-developer/answer/18258653?hl=en, HTTP 200)
  > A new permission, USE_EXACT_ALARM, will be introduced
- Replaced by: None
- Effective: None
- Note: Wording is outdated (Android 13 shipped in 2022) but the section is still published and in force; NOT an exclusion.

## DEP-GPL-INSTANT-APPS - UNKNOWN
- Item: Android Instant Apps policy section
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en (final URL https://support.google.com/googleplay/android-developer/answer/18258653?hl=en, HTTP 200)
  > Developers choosing to distribute Android Instant Apps through Google Play must adhere to the following policies
- Replaced by: None
- Effective: None
- Note: Section still published in the policy page fetched 2026-10-10. Any retirement of the Instant Apps product is not stated in the fetched policy text; status UNKNOWN.

## Repo rules (Oct 9 baseline) whose cited text no longer matches today's text

- GPL-SUBSCRIPTIONS: TEXT_CHANGED_SINCE_BASELINE - Cited section text differs from the text the repo rule was written against; rule needs re-review (not proven deprecated).
