# Current official rules - snapshot 2026-10-10

102 rules. Every quote below was matched verbatim against the official page fetched on 2026-10-10 (UTC timestamps in `last_confirmed_current`).
`Applies when` is a machine applicability condition (features in mcp/server/compliance_mcp/features.py). App-specific interpretation is never stored in the rules. Default verdict without evidence: NEEDS_REVIEW (never PASS).
Machine-readable: `current-rules-2026-10-10.jsonl` / `rules.json`. Community notes are UNOFFICIAL (`community-notes.jsonl`).

## Apple

### CUR-APL-1.4.1-ACCURACY - Medical apps: disclose data and methodology for accuracy claims
- Publisher section: 1.4.1  |  Strength: MUST  |  Scope: Apps with health measurements or diagnostic/treatment use
- Source: https://developer.apple.com/app-store/review/guidelines/#1.4.1 (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Medical apps get greater scrutiny; health-measurement accuracy claims need disclosed data and methodology, otherwise rejection.
  > Medical apps that could provide inaccurate data or information, or that could be used for diagnosing or treating patients may be reviewed with greater scrutiny.
  > Apps must clearly disclose data and methodology to support accuracy claims relating to health measurements
- Applies when (all features present): health
- Static checks: medical_claims_scan

### CUR-APL-1.4.1-DOCTOR - Medical apps: remind users to check with a doctor
- Publisher section: 1.4.1  |  Strength: SHOULD  |  Scope: Medical apps
- Source: https://developer.apple.com/app-store/review/guidelines/#1.4.1 (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Medical apps should remind users to consult a doctor before medical decisions.
  > Apps should remind users to check with a doctor in addition to using the app and before making medical decisions.
- Applies when (all features present): health
- Static checks: medical_disclaimer_strings

### CUR-APL-1.4.1-CLEARANCE - Submit regulatory clearance documentation if cleared
- Publisher section: 1.4.1  |  Strength: SHOULD  |  Scope: Medical apps with regulatory clearance
- Source: https://developer.apple.com/app-store/review/guidelines/#1.4.1 (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: If the app has regulatory clearance, link the documentation in the submission.
  > If your medical app has received regulatory clearance, please submit a link to that documentation with your app.
- Applies when (all features present): health, regulatory_clearance

### CUR-APL-2.1-DEMO - Demo account / working backend for review
- Publisher section: 2.1(a)  |  Strength: SHOULD  |  Scope: Apps with login
- Source: https://developer.apple.com/app-store/review/guidelines/#2.1 (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Provide demo account info and a running backend if the app has a login.
  > include demo account info (and turn on your back-end service!) if your app includes a login
- Applies when (all features present): accounts

### CUR-APL-2.1-IAP - In-app purchases complete and visible to reviewer
- Publisher section: 2.1(b)  |  Strength: SHOULD  |  Scope: Apps with IAP
- Source: https://developer.apple.com/app-store/review/guidelines/#2.1 (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: IAPs must be complete, visible to the reviewer and functional.
  > If you offer in-app purchases in your app, make sure they are complete, up-to-date, visible to the reviewer and functional.
- Applies when (all features present): iap
- Static checks: revenuecat_or_storekit
- Community notes (unofficial): COM-2026-RC-EAS-ENV

### CUR-APL-2.3.6-AGE - Answer age rating questions honestly
- Publisher section: 2.3.6  |  Strength: SHOULD  |  Scope: All apps
- Source: https://developer.apple.com/app-store/review/guidelines/#2.3.6 (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Age rating questionnaire answers must be honest.
  > Answer the age rating questions in App Store Connect honestly
- Applies when (all features present): every app on this platform

### CUR-APL-3.1.1-IAP - Use in-app purchase to unlock features; provide restore
- Publisher section: 3.1.1  |  Strength: MUST  |  Scope: Apps selling digital features/content
- Source: https://developer.apple.com/app-store/review/guidelines/#3.1.1 (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Unlocking features/functionality (incl. subscriptions) requires in-app purchase; restorable purchases need a restore mechanism.
  > you must use in-app purchase
  > you should make sure you have a restore mechanism for any restorable in-app purchases
- Exceptions: US storefront and entitlement exceptions in 3.1.1(a)/3.1.3.
- Applies when (all features present): iap
- Static checks: revenuecat_or_storekit, restore_purchases

### CUR-APL-3.1.1a-LINKS - External purchase links: US storefront vs other storefronts
- Publisher section: 3.1.1(a)  |  Strength: MUST  |  Scope: Apps linking to external purchase
- Source: https://developer.apple.com/app-store/review/guidelines/#3.1.1a (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Entitlements are not required for buttons/external links/calls to action in US storefront apps; in other storefronts such calls to action are not allowed outside the entitlement programs.
  > These entitlements are not required for developers to include buttons, external links, or other calls to action in their United States storefront apps.
  > In all other storefronts, except for the United States storefront, where this prohibition does not apply, apps and their metadata may not include buttons, external links, or other calls to action that direct customers to purchasing mechanisms other than in-app
- Exceptions: United States storefront; StoreKit External Purchase Link / Music Streaming entitlements in specific storefronts.
- Applies when (all features present): external_purchase
- Static checks: external_purchase_links
- Uncertainty: The former US entitlement page (developer.apple.com/support/storekit-external-entitlement-us/) redirected to /support/ on 2026-10-10; the guideline text is the current source.

### CUR-APL-3.1.2a-SUBS - Auto-renewable subscriptions: ongoing value, >=7 days, all devices
- Publisher section: 3.1.2(a)  |  Strength: MUST  |  Scope: Apps with auto-renewable subscriptions
- Source: https://developer.apple.com/app-store/review/guidelines/#3.1.2a (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Auto-renewable subscriptions must give ongoing value, last at least seven days and work across the user's devices.
  > If you offer an auto-renewable subscription, you must provide ongoing value to the customer, and the subscription period must last at least seven days and be available across all of the user’s devices.
- Applies when (all features present): iap

### CUR-APL-3.1.2a-SCAM - No subscription scams / bait-and-switch
- Publisher section: 3.1.2(a)  |  Strength: MUST  |  Scope: Subscription apps
- Source: https://developer.apple.com/app-store/review/guidelines/#3.1.2a (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Apps that trick users into subscriptions are removed.
  > Apps that attempt to scam users will be removed from the App Store.
- Applies when (all features present): iap
- Community notes (unofficial): COM-2025-RC-3.1.2-TRIAL

### CUR-APL-3.1.2c-INFO - Subscription information before purchase; Schedule 2 requirements
- Publisher section: 3.1.2(c)  |  Strength: SHOULD  |  Scope: Subscription apps
- Source: https://developer.apple.com/app-store/review/guidelines/#3.1.2c (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Describe what the user gets for the price and communicate Schedule 2 requirements.
  > Before asking a customer to subscribe, you should clearly describe what the user will get for the price.
  > Ensure you clearly communicate the requirements described in Schedule 2 of the Apple Developer Program License Agreement.
- Applies when (all features present): iap
- Static checks: paywall_legal_links
- Community notes (unofficial): COM-2026-3.1.2-LINKS, COM-2025-RC-3.1.2-TRIAL
- Uncertainty: Schedule 2 itself was not re-fetched in this snapshot; Terms/Privacy link expectations come from community reports.

### CUR-APL-3.1.3-OTHER - Other purchase methods: no in-app steering except US / 3.1.1(a) / 3.1.3(a)
- Publisher section: 3.1.3  |  Strength: MUST  |  Scope: Apps under 3.1.3 categories
- Source: https://developer.apple.com/app-store/review/guidelines/#3.1.3 (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Apps using other purchase methods cannot encourage non-IAP purchasing in-app except on the US storefront and per 3.1.1(a)/3.1.3(a).
  > Apps in this section cannot, within the app, encourage users to use a purchasing method other than in-app purchase, except for apps on the United States storefront and as set forth in 3.1.1(a) and 3.1.3(a).
- Applies when (all features present): external_purchase
- Static checks: external_purchase_links

### CUR-APL-4.2-MINFUNC - Minimum functionality (not a repackaged website)
- Publisher section: 4.2  |  Strength: SHOULD  |  Scope: All apps
- Source: https://developer.apple.com/app-store/review/guidelines/#4.2 (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Apps should go beyond a repackaged website and provide lasting utility.
  > Your app should include features, content, and UI that elevate it beyond a repackaged website.
- Applies when (all features present): every app on this platform
- Static checks: webview_only_scan

### CUR-APL-4.3a-SPAM - Spam: no multiple Bundle IDs of the same app
- Publisher section: 4.3(a)  |  Strength: MUST  |  Scope: All apps
- Source: https://developer.apple.com/app-store/review/guidelines/#4.3 (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Do not submit multiple bundle IDs of the same app.
  > Don’t create multiple Bundle IDs of the same app
- Applies when (all features present): every app on this platform
- Community notes (unofficial): COM-2026-4.3-FORUM-788684, COM-2026-4.3-TEMPLATE

### CUR-APL-4.3b-SPAM - Spam: not indistinguishable from widely available apps
- Publisher section: 4.3(b)  |  Strength: MUST  |  Scope: All apps
- Source: https://developer.apple.com/app-store/review/guidelines/#4.3 (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Do not submit apps indistinguishable from what is widely available.
  > Don’t submit apps that are indistinguishable from what's already widely available.
- Applies when (all features present): every app on this platform
- Community notes (unofficial): COM-2026-4.3-TEMPLATE

### CUR-APL-4.8-LOGIN - Third-party login requires an equivalent privacy-preserving login option
- Publisher section: 4.8  |  Strength: MUST  |  Scope: Apps using third-party/social login for primary account
- Source: https://developer.apple.com/app-store/review/guidelines/#4.8 (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: If third-party/social login sets up the primary account, also offer an equivalent login meeting the listed privacy features.
  > must also offer as an equivalent option another login service with the following features
- Exceptions: Own account system only; enterprise/education; government ID; client for a specific third-party service; alternative marketplace.
- Applies when (all features present): social_login
- Static checks: social_login_siwa

### CUR-APL-5.1.1i-PRIVACY - Privacy policy link in metadata and in app
- Publisher section: 5.1.1(i)  |  Strength: MUST  |  Scope: All apps
- Source: https://developer.apple.com/app-store/review/guidelines/#5.1.1 (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Privacy policy link required in App Store Connect and in the app; must cover collection, third-party sharing, retention/deletion.
  > All apps must include a link to their privacy policy in the App Store Connect metadata field and within the app in an easily accessible manner.
- Applies when (all features present): every app on this platform
- Static checks: privacy_policy_link

### CUR-APL-5.1.1ii-CONSENT - Consent for data collection; purpose strings; no paywalled consent
- Publisher section: 5.1.1(ii)  |  Strength: MUST  |  Scope: All apps collecting data
- Source: https://developer.apple.com/app-store/review/guidelines/#5.1.1 (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Collecting user/usage data needs consent; purpose strings must describe the use; paid functionality cannot depend on granting data access.
  > Apps that collect user or usage data must secure user consent for the collection
  > Paid functionality must not be dependent on or require a user to grant access to this data.
  > Ensure your purpose strings clearly and completely describe your use of the data.
- Applies when (all features present): every app on this platform
- Static checks: ios_usage_descriptions

### CUR-APL-5.1.1iii-MIN - Data minimization
- Publisher section: 5.1.1(iii)  |  Strength: SHOULD  |  Scope: All apps
- Source: https://developer.apple.com/app-store/review/guidelines/#5.1.1 (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Request only data relevant to core functionality.
  > Apps should only request access to data relevant to the core functionality of the app
- Applies when (all features present): every app on this platform
- Static checks: permission_inventory

### CUR-APL-5.1.1v-ACCDEL - Account deletion in app when account creation is supported
- Publisher section: 5.1.1(v)  |  Strength: MUST  |  Scope: Apps with account creation
- Source: https://developer.apple.com/app-store/review/guidelines/#5.1.1v (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Apps supporting account creation must offer account deletion within the app.
  > If your app supports account creation, you must also offer account deletion within the app.
- Applies when (all features present): accounts
- Static checks: account_deletion_presence

### CUR-APL-5.1.1ix-ENTITY - Highly regulated fields (incl. healthcare) submitted by a legal entity
- Publisher section: 5.1.1(ix)  |  Strength: SHOULD  |  Scope: Healthcare and sensitive-data apps
- Source: https://developer.apple.com/app-store/review/guidelines/#5.1.1v (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Apps in highly regulated fields such as healthcare, or requiring sensitive information, should be submitted by a legal entity, not an individual.
  > highly regulated fields (such as banking and financial services, healthcare,
  > should be submitted by a legal entity that provides the services, and not by an individual developer
- Applies when (all features present): health

### CUR-APL-5.1.2i-AI - Disclose and get explicit permission before sharing personal data with third-party AI
- Publisher section: 5.1.2(i)  |  Strength: MUST  |  Scope: Apps sending personal data to third parties/AI
- Source: https://developer.apple.com/app-store/review/guidelines/#5.1.2 (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Clearly disclose where personal data is shared with third parties, including third-party AI, and obtain explicit permission first.
  > You must clearly disclose where personal data will be shared with third parties, including with third-party AI, and obtain explicit permission before doing so.
- Applies when (all features present): ai
- Static checks: ai_provider_consent
- Community notes (unofficial): COM-2026-5.1.2i-FORUM-816140, COM-2026-5.1.2i-FORUM-815842, COM-2026-5.1.2i-REDDIT

### CUR-APL-5.1.2i-ATT - App Tracking Transparency for tracking
- Publisher section: 5.1.2(i)  |  Strength: MUST  |  Scope: Apps that track
- Source: https://developer.apple.com/app-store/review/guidelines/#5.1.2 (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Tracking requires explicit permission via ATT.
  > You must receive explicit permission from users via the App Tracking Transparency APIs to track their activity.
- Applies when (all features present): tracking
- Static checks: att_tracking

### CUR-APL-5.1.2vi-HEALTHKIT - HealthKit/Clinical Records data not for marketing/advertising
- Publisher section: 5.1.2(vi)  |  Strength: MUST  |  Scope: HealthKit users
- Source: https://developer.apple.com/app-store/review/guidelines/#5.1.2 (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Data from HealthKit, Clinical Health Records etc. may not be used for marketing, advertising or use-based data mining.
  > may not be used for marketing, advertising or use-based data mining, including by third parties
- Applies when (all features present): healthkit

### CUR-APL-5.1.3i-HEALTH - Health data: no ads/marketing use; disclose specific health data collected
- Publisher section: 5.1.3(i)  |  Strength: MUST  |  Scope: Health apps
- Source: https://developer.apple.com/app-store/review/guidelines/#5.1.3 (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Health/fitness/medical data may not be used/disclosed for advertising or data mining beyond health management/research with permission; disclose specific health data collected.
  > You must disclose the specific health data that you are collecting from the device.
- Applies when (all features present): health

### CUR-APL-5.1.3ii-ICLOUD - No false HealthKit data; no personal health information in iCloud
- Publisher section: 5.1.3(ii)  |  Strength: MUST  |  Scope: Health apps
- Source: https://developer.apple.com/app-store/review/guidelines/#5.1.3 (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Do not write false data into HealthKit and do not store personal health information in iCloud.
  > Apps must not write false or inaccurate data into HealthKit
  > may not store personal health information in iCloud
- Applies when (all features present): health
- Static checks: icloud_health_storage

### CUR-APL-5.1.3iii-RESEARCH - Health research: consent and ethics board approval
- Publisher section: 5.1.3(iii)-(iv)  |  Strength: MUST  |  Scope: Health research apps
- Source: https://developer.apple.com/app-store/review/guidelines/#5.1.3 (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Health-related human subject research needs participant consent and independent ethics review approval.
  > Apps conducting health-related human subject research must obtain consent from participants
  > Apps conducting health-related human subject research must secure approval from an independent ethics review board.
- Applies when (all features present): health, health_research

### CUR-APL-UR-XCODE26 - Build with Xcode 26 / iOS 26 SDK
- Publisher section: Upcoming Requirements: SDK minimum requirements  |  Strength: MUST  |  Scope: All uploads
- Source: https://developer.apple.com/news/upcoming-requirements/
- Confirmed current: 2026-10-10T14:35:48+00:00
- Requirement: Apps uploaded to App Store Connect must be built with Xcode 26 or later using an SDK for iOS 26 (and peers).
  > Since April 28, 2026
  > Apps uploaded to App Store Connect must be built with Xcode 26 or later
- Enforcement dates: 2026-04-28
- Applies when (all features present): every app on this platform
- Static checks: eas_xcode_image

### CUR-APL-UR-IOS13 - Minimum deployment target iOS 13
- Publisher section: Upcoming Requirements: iOS and iPadOS minimum system requirements  |  Strength: MUST  |  Scope: iOS/iPadOS uploads
- Source: https://developer.apple.com/news/upcoming-requirements/
- Confirmed current: 2026-10-10T14:35:48+00:00
- Requirement: iOS/iPadOS apps uploaded must target iOS 13 or later.
  > Since September 9, 2026
  > iOS and iPadOS apps uploaded to App Store Connect must target iOS 13 or later.
- Enforcement dates: 2026-09-09
- Applies when (all features present): every app on this platform
- Static checks: ios_deployment_target

### CUR-APL-UR-AGE - Respond to updated age rating questions
- Publisher section: Upcoming Requirements: Age Rating Updates  |  Strength: PROGRAM  |  Scope: All apps
- Source: https://developer.apple.com/news/upcoming-requirements/
- Confirmed current: 2026-10-10T14:35:48+00:00
- Requirement: Respond to the updated age rating questions to avoid interruption when submitting updates; age rating is a required property.
  > Provide responses to the updated age rating questions for each of your apps by January 31, 2026, to avoid an interruption when submitting your app updates in App Store Connect.
- Enforcement dates: 2026-01-31
- Applies when (all features present): every app on this platform

### CUR-APL-ASC-AGE - Age rating is required app information
- Publisher section: App Store Connect Help: Set an app age rating  |  Strength: PROGRAM  |  Scope: All apps
- Source: https://developer.apple.com/help/app-store-connect/manage-app-information/set-an-app-age-rating/
- Confirmed current: 2026-10-10T14:35:52+00:00
- Requirement: An age rating is required; EULA minimum ages above the computed rating require an override.
  > An age rating is a required app information property
- Applies when (all features present): every app on this platform

### CUR-APL-DSA-TRADER - EU DSA trader status
- Publisher section: Upcoming Requirements: DSA trader status  |  Strength: PROGRAM  |  Scope: Apps distributed in the EU
- Source: https://developer.apple.com/news/upcoming-requirements/
- Confirmed current: 2026-10-10T14:35:48+00:00
- Requirement: Apps without trader status are removed from the EU App Store until status is provided and verified; developers must self-assess trader status.
  > Apps without trader status will be removed from the App Store in the European Union (EU) until trader status is provided and verified
- Enforcement dates: 2024-10-16, 2025-02-17
- Applies when (all features present): eu_distribution

### CUR-APL-DSA-SELF - Trader self-assessment
- Publisher section: App Store Connect Help: DSA trader requirements  |  Strength: PROGRAM  |  Scope: Apps distributed in the EU
- Source: https://developer.apple.com/help/app-store-connect/manage-compliance-information/manage-european-union-digital-services-act-trader-requirements/
- Confirmed current: 2026-10-10T14:35:52+00:00
- Requirement: Developers must assess whether they are a trader under EU law.
  > You must assess whether you're a trader for EU law purposes.
- Applies when (all features present): eu_distribution

### CUR-APL-RRA - Required reason APIs declared in privacy manifest; no fingerprinting
- Publisher section: Describing use of required reason API  |  Strength: MUST  |  Scope: iOS uploads
- Source: https://developer.apple.com/documentation/bundleresources/describing-use-of-required-reason-api
- Confirmed current: 2026-10-10T14:35:50+00:00
- Requirement: Uploads using required-reason APIs without reasons in the privacy manifest are not accepted; fingerprinting is not allowed.
  > Starting May 1, 2024, apps that don’t describe their use of required reason API in their privacy manifest file aren’t accepted by App Store Connect.
  > Regardless of whether a user gives your app permission to track, fingerprinting is not allowed.
- Enforcement dates: 2024-05-01
- Applies when (all features present): every app on this platform
- Static checks: privacy_manifest

### CUR-APL-SDK-PM - Privacy manifests and signatures for listed third-party SDKs
- Publisher section: Third-party SDK requirements  |  Strength: MUST  |  Scope: Apps including listed SDKs
- Source: https://developer.apple.com/support/third-party-SDK-requirements/
- Confirmed current: 2026-10-10T14:35:51+00:00
- Requirement: Listed commonly used SDKs must include a privacy manifest (and signature when binary) in new apps or updates adding them.
  > You must include the privacy manifest for any SDK listed below when you submit new apps in App Store Connect that include those SDKs
- Applies when (all features present): every app on this platform
- Static checks: privacy_manifest

### CUR-APL-PMF - PrivacyInfo.xcprivacy records data types collected and required-reason APIs
- Publisher section: Privacy manifest files  |  Strength: INFO  |  Scope: iOS apps and SDKs
- Source: https://developer.apple.com/documentation/bundleresources/privacy-manifest-files
- Confirmed current: 2026-10-10T14:35:49+00:00
- Requirement: The privacy manifest PrivacyInfo.xcprivacy records collected data types and required-reason API use.
  > can contain a privacy manifest file, named PrivacyInfo.xcprivacy
- Applies when (all features present): every app on this platform
- Static checks: privacy_manifest

### CUR-APL-MIC - Microphone usage description required
- Publisher section: NSMicrophoneUsageDescription  |  Strength: MUST  |  Scope: Apps using microphone
- Source: https://developer.apple.com/documentation/bundleresources/information-property-list/nsmicrophoneusagedescription
- Confirmed current: 2026-10-10T14:35:56+00:00
- Requirement: NSMicrophoneUsageDescription is required when using microphone APIs.
  > This key is required if your app uses APIs that access the device’s microphone.
- Applies when (all features present): microphone
- Static checks: ios_mic_usage

### CUR-APL-SPEECH - Speech recognition usage description required
- Publisher section: NSSpeechRecognitionUsageDescription  |  Strength: MUST  |  Scope: Apps using Apple speech recognition
- Source: https://developer.apple.com/documentation/bundleresources/information-property-list/nsspeechrecognitionusagedescription
- Confirmed current: 2026-10-10T14:35:57+00:00
- Requirement: NSSpeechRecognitionUsageDescription is required when sending user data to Apple speech recognition servers.
  > This key is required if your app uses APIs that send user data to Apple’s speech recognition servers.
- Applies when (all features present): speech
- Static checks: ios_speech_usage

### CUR-APL-HK-USAGE - HealthKit usage descriptions and privacy policy
- Publisher section: HealthKit: Protecting user privacy  |  Strength: MUST  |  Scope: HealthKit apps
- Source: https://developer.apple.com/documentation/healthkit/protecting-user-privacy
- Confirmed current: 2026-10-10T14:35:55+00:00
- Requirement: HealthKit apps need NSHealthShareUsageDescription / NSHealthUpdateUsageDescription and a privacy policy.
  > Include the NSHealthShareUsageDescription key to read, and NSHealthUpdateUsageDescription key to write data to Healthkit.
  > You must also provide a privacy policy for any app that uses the HealthKit framework.
- Applies when (all features present): healthkit
- Static checks: healthkit_usage

### CUR-APL-HK-3P - HealthKit data to third parties only with express permission
- Publisher section: HealthKit: Protecting user privacy  |  Strength: MUST  |  Scope: HealthKit apps
- Source: https://developer.apple.com/documentation/healthkit/protecting-user-privacy
- Confirmed current: 2026-10-10T14:35:55+00:00
- Requirement: Do not disclose HealthKit information to third parties without express permission; only to health/fitness service providers.
  > You must not disclose any information gained through HealthKit to a third party without express permission from the user.
- Applies when (all features present): healthkit
- Static checks: ai_provider_consent

### CUR-APL-ACCDEL-SUPPORT - Initiate deletion in app; inform about billing; SIWA token revocation
- Publisher section: Offering account deletion in your app  |  Strength: MUST  |  Scope: Apps with accounts
- Source: https://developer.apple.com/support/offering-account-deletion-in-your-app/
- Confirmed current: 2026-10-10T14:35:48+00:00
- Requirement: Apps with account creation must let people initiate deletion in the app; apps with Sign in with Apple should revoke tokens via REST API.
  > Apps submitted to the App Store that support account creation must also let people initiate deletion of their account within the app.
  > Apps that support Sign in with Apple should use the Sign in with Apple REST API to revoke user tokens
- Applies when (all features present): accounts
- Static checks: account_deletion_presence

### CUR-APL-PRIVLABEL - App privacy (nutrition label) disclosures
- Publisher section: App privacy details on the App Store  |  Strength: PROGRAM  |  Scope: All apps
- Source: https://developer.apple.com/app-store/app-privacy-details/
- Confirmed current: 2026-10-10T14:35:55+00:00
- Requirement: Data types collected must be disclosed in App Store Connect unless all optional-disclosure criteria are met.
  > If a data type collected by your app meets some, but not all, of the above criteria, it must be disclosed in App Store Connect.
- Applies when (all features present): every app on this platform

### CUR-APL-EU-DPLA - EU unified business terms (DPLA Attachment 14) effective Oct 1, 2026
- Publisher section: Update on apps distributed in the EU  |  Strength: PROGRAM  |  Scope: Apps distributed in the EU
- Source: https://developer.apple.com/support/dma-and-apps-in-the-eu/
- Confirmed current: 2026-10-10T14:35:58+00:00
- Requirement: EU distribution terms changed: earlier EU addenda superseded by DPLA Attachment 14 as of October 1, 2026.
  > As of October 1, 2026, these terms have been superseded by Attachment 14 of the Apple Developer Program License Agreement.
- Enforcement dates: 2026-10-01
- Applies when (all features present): eu_distribution
- Uncertainty: Attachment 14 itself not analysed in this snapshot.

### CUR-APL-1.2-UGC - UGC: filtering, reporting, blocking, contact info
- Publisher section: 1.2  |  Strength: MUST  |  Scope: Apps with UGC / social features
- Source: https://developer.apple.com/app-store/review/guidelines/#1.2 (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Apps with user-generated content or social networking must filter objectionable material, offer reporting with timely responses, let users block abusive users, and publish contact information.
  > apps with user-generated content or social networking services must include:
  > A mechanism to report offensive content and timely responses to concerns
  > The ability to block abusive users from the service
- Applies when (all features present): ugc

### CUR-APL-1.1.1-RELIGION - No defamatory/mean-spirited content incl. about religion
- Publisher section: 1.1.1  |  Strength: MUST NOT  |  Scope: Apps with religious or targeted-group content
- Source: https://developer.apple.com/app-store/review/guidelines/#1.1.1 (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Content that is defamatory, discriminatory or mean-spirited, including about religion, is objectionable; political satire/humour generally exempt.
  > Defamatory, discriminatory, or mean-spirited content, including references or commentary about religion
- Exceptions: Professional political satirists and humorists are generally exempt.
- Applies when (all features present): religious_content

### CUR-APL-1.3-KIDS - Kids Category: parental gate, no PII/device info to third parties
- Publisher section: 1.3  |  Strength: MUST  |  Scope: Apps in (or designed for) the Kids Category
- Source: https://developer.apple.com/app-store/review/guidelines/#1.3 (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Kids Category apps must keep links out/purchases behind a parental gate and may not send PII or device information to third parties.
  > These apps must not include links out of the app, purchasing opportunities, or other distractions to kids unless reserved for a designated area behind a parental gate.
  > apps may not send personally identifiable information or device information to third parties.
- Applies when (all features present): kids_audience

### CUR-APL-5.1.4-KIDS - Kids data: no third-party analytics/ads in apps primarily for kids
- Publisher section: 5.1.4  |  Strength: SHOULD  |  Scope: Apps intended primarily for kids
- Source: https://developer.apple.com/app-store/review/guidelines/#5.1.4 (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Apps intended primarily for kids should not include third-party analytics or advertising; birthdate/parental contact only for statutory compliance.
  > Apps intended primarily for kids should not include third-party analytics or third-party advertising.
  > Apps may ask for birthdate and parental contact information only for the purpose of complying with these statutes
- Applies when (all features present): kids_audience

### CUR-APL-2.5.18-ADS - Ads: no targeting on sensitive data; age-appropriate; visible close
- Publisher section: 2.5.18  |  Strength: MUST  |  Scope: Apps displaying ads
- Source: https://developer.apple.com/app-store/review/guidelines/#2.5.18 (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Ads must suit the age rating, must not be targeted on sensitive data (health/medical, kids), and interstitials need visible close/skip.
  > may not engage in targeted or behavioral advertising based on sensitive user data such as health/medical data
  > Ads displayed in an app must be appropriate for the app's age rating
- Applies when (all features present): ads

### CUR-APL-3.1.1-LOOTBOX - Loot boxes: disclose odds before purchase
- Publisher section: 3.1.1  |  Strength: MUST  |  Scope: Apps/games selling randomized items
- Source: https://developer.apple.com/app-store/review/guidelines/#3.1.1 (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Randomized purchasable virtual items must disclose the odds of each item type before purchase.
  > must disclose the odds of receiving each type of item to customers prior to purchase.
- Applies when (all features present): loot_boxes

### CUR-APL-3.1.3e-GOODS - Physical goods/services: must NOT use IAP
- Publisher section: 3.1.3(e)  |  Strength: MUST  |  Scope: Apps selling physical goods/services
- Source: https://developer.apple.com/app-store/review/guidelines/#3.1.3e (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Physical goods or services consumed outside the app must be paid with non-IAP methods (Apple Pay, card entry). This is the exception that can make external checkout correct.
  > If your app enables people to purchase physical goods or services that will be consumed outside of the app, you must use purchase methods other than in-app purchase to collect those payments
- Applies when (all features present): external_purchase, physical_goods

### CUR-APL-3.1.3a-READER - Reader apps: External Link Account Entitlement
- Publisher section: 3.1.3(a)  |  Strength: MAY  |  Scope: Reader apps only (content types enumerated)
- Source: https://developer.apple.com/app-store/review/guidelines/#3.1.3a (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Reader apps (magazines, news, books, audio, music, video) may offer account creation/management and may apply for the External Link Account Entitlement; not required for US storefront calls to action.
  > Reader app developers may apply for the External Link Account Entitlement
  > This entitlement is not required for developers to include buttons, external links, or other calls to action in their United States storefront apps.
- Applies when (all features present): external_purchase, reader_content

### CUR-APL-5.3.3-RMG - No IAP for real-money gaming credit
- Publisher section: 5.3.3  |  Strength: MUST NOT  |  Scope: Real-money gaming apps
- Source: https://developer.apple.com/app-store/review/guidelines/#5.3.3 (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: In-app purchase may not be used to buy credit or currency for real-money gaming.
  > Apps may not use in-app purchase to purchase credit or currency for use in conjunction with real money gaming of any kind.
- Applies when (all features present): real_money_gaming

### CUR-APL-4.7-CHATBOT - Chatbots/mini apps: developer responsible for all such software
- Publisher section: 4.7  |  Strength: MUST  |  Scope: Apps offering chatbots, mini apps/games, streaming games, plug-ins
- Source: https://developer.apple.com/app-store/review/guidelines/#4.7 (page last updated: June 8, 2026)
- Confirmed current: 2026-10-10T14:35:47+00:00
- Requirement: Apps offering chatbots, mini apps/games or plug-ins are responsible for that software complying with the Guidelines and law.
  > You are responsible for all such software offered in your app, including ensuring that such software complies with these Guidelines and all applicable laws.
- Applies when (all features present): ai
- Uncertainty: Whether a server-side LLM assistant is a 'chatbot' under 4.7 is not defined in the text; human judgment.

## Google

### CUR-GPL-HEALTH-DECL - Complete the Health apps declaration form
- Publisher section: Health and Medical Apps: Console Declaration  |  Strength: PROGRAM  |  Scope: All apps
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: All developers must complete the Health apps declaration in Play Console (even with no health features).
  > All developers must complete the Health apps declaration form on the App content page
- Applies when (all features present): every app on this platform
- Community notes (unofficial): COM-2026-HEALTH-DISCLAIMER

### CUR-GPL-HEALTH-DECL-ALL - Declaration required even without health features
- Publisher section: Health apps declaration form (Help)  |  Strength: PROGRAM  |  Scope: All apps
- Source: https://support.google.com/googleplay/android-developer/answer/14738291?hl=en
- Confirmed current: 2026-10-10T14:36:09+00:00
- Requirement: Even apps without health features must complete the form and certify that.
  > Even developers with apps that do not offer any health features must complete this form and certify that no health features are offered through the app.
- Applies when (all features present): every app on this platform

### CUR-GPL-HEALTH-PRIVACY - Health apps privacy policy in Console and in app
- Publisher section: Health and Medical Apps: Privacy Policy and Prominent Disclosure  |  Strength: MUST  |  Scope: Health apps
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: Health apps must post a privacy policy link in Play Console and in the app, covering access, collection, use and sharing.
  > Your app must post a privacy policy link in the designated field within Play Console, and a privacy policy link or text within the app itself.
- Applies when (all features present): health
- Static checks: privacy_policy_link

### CUR-GPL-HEALTH-PERMS - Remove permissions not needed for core health functionality
- Publisher section: Health and Medical Apps  |  Strength: MUST  |  Scope: Health apps
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: Do not request permissions not required for core functionality; remove unused permissions.
  > Permissions that are not required for a health app to perform its core functionality should not be requested and unused permissions must be removed.
- Applies when (all features present): health
- Static checks: permission_inventory

### CUR-GPL-HEALTH-DISCLAIMER - Non-device health apps: 'not a medical device' disclaimer in description
- Publisher section: Health and Medical Functionalities  |  Strength: MUST  |  Scope: Health/medical apps not regulated as devices
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: Health/medical apps not regulated as medical devices must include the prescribed disclaimer in the app description.
  > Other health and medical apps must include a clear disclaimer in their app description indicating that the app is “not a medical device and does not diagnose, treat, cure, or prevent any medical condition.”
- Applies when (all features present): health
- Static checks: medical_disclaimer_strings
- Community notes (unofficial): COM-2026-HEALTH-DISCLAIMER

### CUR-GPL-HEALTH-CONSULT - Remind users to consult a healthcare professional
- Publisher section: Health and Medical Functionalities  |  Strength: MUST  |  Scope: Health/medical apps
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: Apps must remind users to consult a healthcare professional.
  > Apps must also remind users to consult a healthcare professional for medical advice, diagnosis, or treatment.
- Applies when (all features present): health
- Static checks: medical_disclaimer_strings

### CUR-GPL-HEALTH-MEDDEV - Regulated medical devices must be declared
- Publisher section: Health and Medical Functionalities  |  Strength: MUST  |  Scope: Regulated medical device apps
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: Apps regulated as medical devices must be declared and provide proof of clearance upon request.
  > Apps that are regulated because they are a medical device must be declared as such
- Applies when (all features present): health, regulated_medical_device

### CUR-GPL-HEALTH-HW - Disclose external hardware/device compatibility
- Publisher section: Health and Medical Functionalities  |  Strength: MUST  |  Scope: Apps using external health hardware
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: Apps relying on external hardware or device sensors must disclose requirements/compatibility in the description.
  > must clearly disclose these external hardware requirements in the app description
- Applies when (all features present): health, external_health_hardware

### CUR-GPL-HEALTH-EU-MDR - EU MDR/IVDR regulated apps: additional disclosures
- Publisher section: Health apps declaration form (Help): EU MDR/IVDR  |  Strength: PROGRAM  |  Scope: EU-regulated medical device apps
- Source: https://support.google.com/googleplay/android-developer/answer/14738291?hl=en
- Confirmed current: 2026-10-10T14:36:09+00:00
- Requirement: Apps in EEA/Northern Ireland regulated by EU MDR/IVDR have additional disclosure obligations.
  > your app is a medical device that is subject to additional disclosure obligations
- Applies when (all features present): health, regulated_medical_device, eu_distribution

### CUR-GPL-HEALTH-MISINFO - No misleading health claims
- Publisher section: Health Misinformation  |  Strength: MUST  |  Scope: All apps with health content
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: No misleading health claims contradicting medical consensus or causing harm.
  > We don’t allow apps containing misleading health claims that contradict existing medical consensus, or can cause harm to users.
- Applies when (all features present): health
- Static checks: medical_claims_scan

### CUR-GPL-ORG-ACCOUNT - Health apps must register as an Organization account
- Publisher section: Play Console Requirements 1.2  |  Strength: PROGRAM  |  Scope: Health apps
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: Developers providing health apps (e.g., medical) must register as an Organization.
  > developers providing the following services must register as an Organization
  > Health apps, such as Medical apps and Human Subjects Research apps.
- Applies when (all features present): health

### CUR-GPL-PKG-REGISTER - Register package names for developer verification
- Publisher section: Play Console Requirements 3.4  |  Strength: PROGRAM  |  Scope: All apps
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: Register app package names in Play Console for Android developer verification.
  > Register your app package names via Play Console to comply with Android developer verification requirements.
- Applies when (all features present): every app on this platform

### CUR-GPL-HC-USECASE - Health Connect only for approved use cases
- Publisher section: Health Connect: Appropriate Access  |  Strength: MUST  |  Scope: Apps using Health Connect
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: Health Connect permissions may only be requested for approved use cases.
  > you may only request access to permissions when your application or service meets one of the approved use cases.
- Applies when (all features present): health_connect
- Static checks: health_connect_usage

### CUR-GPL-HC-LIMITED - Health Connect data: no ads use, no sale; limited transfers
- Publisher section: Health Connect: Limited Use  |  Strength: MUST  |  Scope: Apps using Health Connect
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: Health Connect data cannot be sold or used for ads; transfers only with explicit consent for listed purposes.
  > Transferring, selling, or using user data for serving ads, including personalized or interest-based advertising.
- Applies when (all features present): health_connect
- Static checks: health_connect_usage, ai_provider_consent
- Uncertainty: Whether sending Health Connect data to an AI provider for a user-visible feature fits 'providing or improving the appropriate use case' needs review.

### CUR-GPL-AI-REPORT - In-app reporting/flagging for AI-generated content
- Publisher section: AI-Generated Content  |  Strength: MUST  |  Scope: Apps with generative AI
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: Apps generating content with AI must offer in-app reporting/flagging without leaving the app and prevent restricted content.
  > Apps that generate content using AI must contain in-app user reporting or flagging features that allow users to report or flag offensive content to developers without needing to exit the app.
  > prohibiting and preventing the generation of Restricted Content
- Applies when (all features present): ai
- Static checks: ai_report_feature

### CUR-GPL-DATASAFETY - Accurate Data safety section (incl. SDKs)
- Publisher section: Data safety section  |  Strength: PROGRAM  |  Scope: All apps
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: Complete an accurate, up-to-date Data safety section consistent with the privacy policy.
  > All developers must complete a clear and accurate Data safety section for every app detailing collection, use, and sharing of user data.
- Applies when (all features present): every app on this platform
- Static checks: sdk_inventory

### CUR-GPL-PRIVACYPOLICY - Privacy policy in Play Console and in app
- Publisher section: Privacy Policy  |  Strength: MUST  |  Scope: All apps
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: All apps must post a privacy policy in Play Console and in the app; public, non-geofenced, non-PDF URL.
  > Please make sure your privacy policy is available on an active, publicly accessible and non-geofenced URL (no PDFs) and is non-editable.
- Applies when (all features present): every app on this platform
- Static checks: privacy_policy_link

### CUR-GPL-PROMINENT - Prominent disclosure before consent/runtime permission
- Publisher section: Prominent Disclosure & Consent  |  Strength: MUST  |  Scope: Apps with unexpected data access
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: Where data use may be unexpected, an in-app disclosure must immediately precede consent and runtime permission requests.
  > Requests for in-app user consent and runtime permission requests must be immediately preceded by an in-app disclosure that meets the requirement of this policy.
- Applies when (all features present): every app on this platform
- Static checks: ai_provider_consent, permission_inventory

### CUR-GPL-PERMS - Only permissions needed for promoted current features
- Publisher section: Permissions and APIs that Access Sensitive Information  |  Strength: MUST  |  Scope: All apps
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: Request only permissions necessary for current features promoted in the listing; request in context.
  > You may only request permissions and APIs that access sensitive information that are necessary to implement current features or services in your app that are promoted in your Google Play listing.
- Applies when (all features present): every app on this platform
- Static checks: permission_inventory
- Uncertainty: No microphone-specific Play policy section was identified; RECORD_AUDIO falls under this section plus Data safety/prominent disclosure.

### CUR-GPL-EXACT-ALARM - USE_EXACT_ALARM only for alarm/timer/calendar core functionality
- Publisher section: Exact Alarm Permission  |  Strength: MUST  |  Scope: Apps declaring exact alarm permissions
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: USE_EXACT_ALARM is restricted to core functionality needing exact alarms (alarm/timer, calendar); otherwise consider SCHEDULE_EXACT_ALARM.
  > USE_EXACT_ALARM is a restricted permission and apps must only declare this permission if their core functionality supports the need for an exact alarm.
- Applies when (all features present): exact_alarm
- Static checks: exact_alarm
- Community notes (unofficial): COM-2026-EXACT-ALARM-GH

### CUR-GPL-FGS - Foreground service types and permissions
- Publisher section: Permissions for Foreground Services  |  Strength: MUST  |  Scope: Apps with foreground services
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: Apps targeting Android 14+ must specify a valid foreground service type and matching permission for each foreground service.
  > you must specify a valid foreground service type for each foreground service used in your app
- Applies when (all features present): foreground_service
- Static checks: foreground_service

### CUR-GPL-PAYMENTS - Google Play billing for in-app digital purchases (outside program exceptions)
- Publisher section: Payments  |  Strength: MUST  |  Scope: Apps selling digital goods
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: In-app purchases of digital features/services must use Google Play's billing system unless policy sections 3, 8 or 9 apply.
  > must use Google Play’s billing system for those transactions unless Section 3, 8, or 9 applies.
- Exceptions: US programs (see CUR-GPL-US-PROGRAMS); EEA/other alternative billing programs.
- Applies when (all features present): iap
- Static checks: revenuecat_or_storekit

### CUR-GPL-US-PROGRAMS - US: alternative billing / external content links programs and fees
- Publisher section: Update regarding Google Play's policies for US users  |  Strength: PROGRAM  |  Scope: Apps serving US users using external links/alternative billing
- Source: https://support.google.com/googleplay/android-developer/answer/15582165?hl=en
- Confirmed current: 2026-10-10T14:36:27+00:00
- Requirement: For US users, Google does not require Play Billing; current programs remain in effect; enrolled developers report and pay fees from Oct 1, 2026 (download reporting until Dec 1, 2026).
  > Google will not require the use of Google Play Billing in apps distributed on the Google Play Store
  > will need to report transactions and pay the relevant service fees starting on October 1, 2026.
  > they now have until December 1, 2026 to report successful download and pay the relevant service fees.
- Enforcement dates: 2026-10-01, 2026-12-01
- Applies when (all features present): external_purchase
- Static checks: external_purchase_links
- Uncertainty: Page states a new settlement (March 4, 2026) and a requested revised Modified Injunction; terms may change.

### CUR-GPL-ECL - External content links program eligibility
- Publisher section: External content links program (US)  |  Strength: PROGRAM  |  Scope: US external links
- Source: https://support.google.com/googleplay/android-developer/answer/16470497?hl=en
- Confirmed current: 2026-10-10T14:36:25+00:00
- Requirement: The program lets Play apps link US users to external content/purchases; apps must serve US users.
  > In order to be eligible for this program, your app(s) must be a mobile or tablet app or game serving users in the United States and its territories.
- Applies when (all features present): external_purchase

### CUR-GPL-SUBS - Transparent subscription offers; sustained value
- Publisher section: Subscriptions  |  Strength: MUST  |  Scope: Subscription apps
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: Disclose offer terms, cost, billing frequency, auto-renewal; subscriptions must provide sustained value.
  > You must be transparent about your offer.
  > Subscriptions must provide sustained or recurring value to users throughout the life of the subscription
- Applies when (all features present): iap
- Static checks: paywall_legal_links

### CUR-GPL-PBL - Play Billing Library version deadlines
- Publisher section: Play Billing Library version deprecation  |  Strength: MUST  |  Scope: Apps using Play Billing
- Source: https://developer.android.com/google/play/billing/deprecation-faq (page last updated: 2026-09-09 UTC)
- Confirmed current: 2026-10-10T14:36:58+00:00
- Requirement: PBL 7: new app and update deadline August 31, 2026, extension November 1, 2026; PBL 8: August 31, 2027.
  > All versions of the Google Play Billing Library have a two-year deprecation cycle.
- Enforcement dates: 2026-08-31, 2026-11-01, 2027-08-31
- Applies when (all features present): iap
- Static checks: play_billing_version
- Uncertainty: Table cells fetched as separate lines; version-to-date mapping read from the table order on the page.

### CUR-GPL-IMPERSONATION - No impersonation
- Publisher section: Impersonation  |  Strength: MUST  |  Scope: All apps
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: Do not impersonate other developers, entities or apps or imply false affiliation.
  > We don’t allow apps that mislead users by impersonating someone else
- Applies when (all features present): every app on this platform

### CUR-GPL-SPAM - No repetitive / low-quality apps or message spam
- Publisher section: Spam  |  Strength: MUST  |  Scope: All apps
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: No apps that spam users or Play, including repetitive or low-quality apps.
  > We don't allow apps that spam users or Google Play, such as apps that send users unsolicited messages or apps that are repetitive or low-quality.
- Applies when (all features present): every app on this platform

### CUR-GPL-LIMITED - No limited-functionality apps
- Publisher section: Minimum Functionality  |  Strength: MUST  |  Scope: All apps
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: Apps with only limited functionality and content are not allowed.
  > We do not allow apps that only have limited functionality and content.
- Applies when (all features present): every app on this platform
- Static checks: webview_only_scan

### CUR-GPL-ACCDEL - Account deletion in app and via web resource; delete data
- Publisher section: Account Deletion Requirement  |  Strength: MUST  |  Scope: Apps with account creation
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: Apps with account creation must offer deletion in-app and via a web resource linked in Play Console; freezing is not deletion.
  > This option must be available both from within your app and externally through a designated web resource.
  > Temporary account deactivation, disabling, or “freezing” the app account does not qualify as account deletion.
- Applies when (all features present): accounts
- Static checks: account_deletion_presence

### CUR-GPL-ACCDEL-FORM - Data deletion questions; subscription-cancellation steps disclosed
- Publisher section: Understanding app account deletion requirements  |  Strength: PROGRAM  |  Scope: Apps with account creation
- Source: https://support.google.com/googleplay/android-developer/answer/13327111?hl=en
- Confirmed current: 2026-10-10T14:36:02+00:00
- Requirement: Complete Data deletion questions in Data safety; extra steps such as cancelling a subscription must be clearly outlined.
  > All developers must complete new Data deletion questions in the Data safety form on the App content page in Play Console.
  > If the user needs to take additional steps before deleting their account (for example, canceling a subscription), this must be clearly outlined
- Applies when (all features present): accounts

### CUR-GPL-TAPI-NEW - Target API 36 for new apps and updates from Aug 31, 2026
- Publisher section: Target API level requirements  |  Strength: MUST  |  Scope: All Play submissions
- Source: https://support.google.com/googleplay/android-developer/answer/11926878?hl=en
- Confirmed current: 2026-10-10T14:36:11+00:00
- Requirement: New apps and updates must target Android 16 (API 36); extension to November 1, 2026 on request.
  > Starting August 31, 2026:
  > New apps and app updates must target Android 16 (API level 36) or higher to be submitted to Google Play
  > You will be able to request an extension to November 1, 2026 if you need more time to update your app.
- Exceptions: Wear OS / Automotive: API 35; TV / XR: API 34.
- Enforcement dates: 2026-08-31, 2026-11-01
- Applies when (all features present): every app on this platform
- Static checks: android_target_sdk

### CUR-GPL-TAPI-EXISTING - Existing apps target API 35 to stay available to new users
- Publisher section: Target API level requirements  |  Strength: MUST  |  Scope: Existing apps
- Source: https://support.google.com/googleplay/android-developer/answer/11926878?hl=en
- Confirmed current: 2026-10-10T14:36:11+00:00
- Requirement: Existing apps must target API 35+ to remain available to new users on newer Android versions.
  > Existing apps must target Android 15 (API level 35) or higher to remain available to new users
- Enforcement dates: 2026-08-31
- Applies when (all features present): every app on this platform
- Static checks: android_target_sdk_existing

### CUR-GPL-TAPI-POLICY - Target within one year of latest major Android release
- Publisher section: Target API Level Policy  |  Strength: MUST  |  Scope: All Play submissions
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: New apps and updates must target an API level within one year of the latest major Android release.
  > New apps and app updates MUST target an Android API level within one year of the latest major Android version release.
- Applies when (all features present): every app on this platform
- Static checks: android_target_sdk

### CUR-GPL-16KB - 16 KB page size and 64-bit for native code
- Publisher section: Play Console technical quality requirements  |  Strength: MUST  |  Scope: Apps with native code (React Native/Expo ship native libraries)
- Source: https://support.google.com/googleplay/android-developer/answer/17492799?hl=en
- Confirmed current: 2026-10-10T14:36:20+00:00
- Requirement: New app bundles with native code must support 16 KB page sizes and 64-bit-only architectures.
  > Apps that contain native code must support devices with 16 KB memory page sizes.
  > Apps that contain native code must support 64-bit only architectures.
- Applies when (all features present): native_code
- Static checks: page_size_16kb

### CUR-GPL-16KB-DEV - 16 KB requirement for apps targeting Android 15+; update block from Feb 1, 2027
- Publisher section: Support 16 KB page sizes  |  Strength: MUST  |  Scope: Apps targeting API 35+
- Source: https://developer.android.com/guide/practices/page-sizes (page last updated: 2026-09-16 UTC)
- Confirmed current: 2026-10-10T14:36:22+00:00
- Requirement: Apps targeting Android 15+ must support 16 KB page sizes on 64-bit devices; from February 1, 2027 non-compliant updates can't be released.
  > apps targeting Android 15 (API level 35) and higher must support 16 KB memory page sizes on 64-bit devices on Google Play.
  > Starting February 1, 2027,
- Enforcement dates: 2027-02-01
- Applies when (all features present): native_code
- Static checks: page_size_16kb

### CUR-GPL-DEVVER - Developer verification timeline
- Publisher section: Android developer verification  |  Strength: PROGRAM  |  Scope: All Android developers
- Source: https://developer.android.com/developer-verification
- Confirmed current: 2026-10-10T14:36:23+00:00
- Requirement: From September 30, 2026 protections begin for installs from participating stores in Brazil, Indonesia, Singapore and Thailand; global expansion 2027.
  > Protections begin for all users who install apps from participating stores in Brazil, Indonesia, Singapore, and Thailand on certified devices running Android 7+.
- Enforcement dates: 2026-09-30
- Applies when (all features present): every app on this platform

### CUR-GPL-TEST-NEWACCT - Closed test: 12 testers for 14 days (new personal accounts)
- Publisher section: App testing requirements for new personal developer accounts  |  Strength: PROGRAM  |  Scope: New personal developer accounts
- Source: https://support.google.com/googleplay/android-developer/answer/14151465?hl=en
- Confirmed current: 2026-10-10T14:36:23+00:00
- Requirement: Personal accounts created after November 13, 2023 must run a closed test with at least 12 testers opted in for 14 continuous days before production access.
  > must run a closed test for their app with a minimum of 12 testers who have been opted in continuously for at least 14 days.
- Applies when (all features present): personal_account

### CUR-GPL-SDK - Developer responsible for SDK behaviour and data practices
- Publisher section: SDK Requirements  |  Strength: MUST  |  Scope: All apps with SDKs
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: You are responsible for SDK code and data practices complying with Play policies (no sale of personal and sensitive data).
  > If you include an SDK in your app, you are responsible for ensuring that their third-party code and practices do not cause your app to violate Google Play Developer Program Policies.
- Applies when (all features present): every app on this platform
- Static checks: sdk_inventory

### CUR-GPL-AUDIENCE - Declare target audience
- Publisher section: Target Audience and Content  |  Strength: PROGRAM  |  Scope: All apps
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: Indicate the target audience age groups in Play Console before publishing.
  > you must indicate the target audience for your app, prior to publishing
- Applies when (all features present): every app on this platform

### CUR-GPL-CONTENT-RATING - Content rating required
- Publisher section: Content Ratings  |  Strength: PROGRAM  |  Scope: All apps
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: Apps without a content rating are not allowed.
  > We don’t allow apps without a content rating on Google Play.
- Applies when (all features present): every app on this platform

### CUR-GPL-UGC - UGC: terms acceptance, in-app reporting and blocking
- Publisher section: User Generated Content  |  Strength: MUST  |  Scope: Apps with UGC visible to other users
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: UGC apps must require acceptance of terms before posting, define/prohibit objectionable content, and provide in-app reporting and blocking of UGC and users.
  > Requires users accept the app's terms of use and/or user policy before users can create or upload UGC
  > providing an in-app system for reporting and blocking objectionable UGC and users
- Applies when (all features present): ugc

### CUR-GPL-HATE-RELIGION - No incitement of hatred incl. based on religion
- Publisher section: Hate Speech  |  Strength: MUST NOT  |  Scope: Apps with religious or group-related content
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: Apps must not promote violence or incite hatred against groups based on protected characteristics including religion.
  > incite hatred against individuals or groups based on race or ethnic origin, religion
- Applies when (all features present): religious_content

### CUR-GPL-ADS-RATING - Ads appropriate for content rating; ads follow all policies
- Publisher section: Ads  |  Strength: MUST  |  Scope: Apps displaying ads
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: Ads and their offers are part of the app, must follow all Play policies and be appropriate for the app's content rating.
  > must be appropriate for the content rating of your app
- Applies when (all features present): ads

### CUR-GPL-FAMILIES - Child audience: Families requirements and accurate console answers
- Publisher section: Families Policy Requirements  |  Strength: MUST  |  Scope: Apps with children in the target audience
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: If any target audience is children the Families requirements apply, including appropriate content and accurate Target Audience, Data safety and IARC answers.
  > If one of the target audiences for your app is children, you must comply with the following requirements.
  > You must accurately answer the questions in the Play Console regarding your app
- Applies when (all features present): kids_audience

### CUR-GPL-LOOTBOX - Loot boxes: disclose odds before purchase
- Publisher section: Payments  |  Strength: MUST  |  Scope: Apps/games selling randomized items
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: Randomized virtual items from a purchase must clearly disclose odds in advance of and close to the purchase.
  > must clearly disclose the odds of receiving those items in advance of, and in close and timely proximity to, that purchase.
- Applies when (all features present): loot_boxes

### CUR-GPL-PHYSICAL-GOODS - Physical goods/services: must NOT use Play Billing
- Publisher section: Payments  |  Strength: MUST NOT  |  Scope: Apps selling physical goods/services
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: Play Billing must not be used where payment is primarily for physical goods or physical services; the exception that can make external checkout correct.
  > Google Play's billing system must not be used in cases where:
  > for the purchase or rental of physical goods (such as groceries, clothing, housewares, electronics);
- Applies when (all features present): external_purchase, physical_goods

### CUR-GPL-RMG - Real-money gambling: licensed operator + application process
- Publisher section: Real-Money Gambling, Games, and Contests  |  Strength: MUST  |  Scope: Real-money gambling/contest apps
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: Gambling apps need the gambling application, an approved/licensed operator status and a valid operating license per country.
  > is an approved governmental operator and/or is registered as a licensed operator with the appropriate governmental gambling authority in the specified country
- Applies when (all features present): real_money_gaming

### CUR-GPL-SENSITIVE-SECURE - Sensitive data: limit use, transmit securely
- Publisher section: Personal and Sensitive User Data  |  Strength: MUST  |  Scope: Apps handling personal or sensitive data
- Source: https://support.google.com/googleplay/android-developer/answer/18258653?hl=en
- Confirmed current: 2026-10-10T14:36:00+00:00
- Requirement: Personal/sensitive data (incl. health, microphone, camera, auth info) must be limited to expected functionality and handled securely, e.g. HTTPS.
  > Handle all personal and sensitive user data securely, including transmitting it using modern cryptography (for example, over HTTPS).
- Applies when (all features present): accounts

## Community notes (UNOFFICIAL - not policy)

- **COM-2026-5.1.2i-FORUM-816140** (Apple Developer Forums, search-result snippet): Rejection under 5.1.1(i)/5.1.2(i): app shared personal data with a third-party AI service without explaining what data is sent, to whom, and asking permission; developer reports a consent screen alone did not clear it. <https://origin-devforums.apple.com/forums/thread/816140>
- **COM-2026-5.1.2i-FORUM-815842** (Apple Developer Forums, search-result snippet): Reviewer text quoted: disclose what data is sent, specify who it is sent to, obtain permission before sending; privacy policy must name AI data processors. <https://origin-devforums.apple.com/forums/thread/815842>
- **COM-2026-5.1.2i-REDDIT** (Reddit r/iOSProgramming (via search results only), search-result snippet): Developers report passing review with a blocking consent sheet naming the provider and data before the first AI call, with a non-AI fallback if declined. <https://www.reddit.com/r/iOSProgramming/comments/1teaqdv/anyone_gotten_through_512i_review_on_a_thirdparty/>
- **COM-2026-5.1.2i-BLOG-STORA** (Blog (stora.sh), search-result snippet, 2026-05-06): Claims the 'including with third-party AI' wording dates from Nov 13, 2025 guideline update; consent must precede first transmission and be revocable. <https://stora.sh/blog/2026-05-06-apple-ai-consent-rule-5-1-2-i-implementation-guide>
- **COM-2026-4.3-FORUM-788684** (Apple Developer Forums, search-result snippet): App approved then update rejected under 4.3(a); Apple reply: such apps typically share similar binary, metadata and concept with existing apps. <https://developer.apple.com/forums/thread/788684>
- **COM-2026-4.3-TEMPLATE** (Reddit r/iosdev (via search results only), search-result snippet): Quoted 4.3(a) rejection text lists factors: same source code/assets as other apps, repackaged templates, purchased templates, similar apps across accounts. <https://www.reddit.com/r/iosdev/comments/1u7jyk4/guideline_43a_design_spam/>
- **COM-2026-3.1.2-LINKS** (Blog (appsubmitter.io), search-result snippet): Quoted 3.1.2 rejection asks for functional Terms of Use (EULA) and privacy policy links in the app and in App Store metadata. <https://www.appsubmitter.io/app-rejection-guides/app-store-guideline-3-1-2-subscriptions/>
- **COM-2025-RC-3.1.2-TRIAL** (RevenueCat Community, search-result snippet): RevenueCat paywall rejected under 3.1.2 because the free trial was more conspicuous than the billed amount; Apple asked that billed amount be the most prominent pricing element. <https://community.revenuecat.com/general-questions-7/rejected-due-to-guideline-3-1-2-business-payments-subscriptions-4775>
- **COM-2026-RC-EAS-ENV** (Blog (DEV Community), search-result snippet): 2.1(b) rejection because RevenueCat key was only in .env and not EAS environment variables, leaving the purchase button disabled in the review build. <https://dev.to/nicoinu/my-subscribe-button-was-greyed-out-and-that-got-my-app-rejected-d42>
- **COM-2026-HEALTH-DISCLAIMER** (Reddit r/reactnative (via search results only), search-result snippet): Expo health app developer's pre-submission setup: Health apps declaration, 'not a medical device' disclaimer, Data safety answers; open questions about web deletion page login and purge grace period. <https://www.reddit.com/r/reactnative/comments/1s9idc1/firsttime_submitting_a_health_fitness_app_that/>
- **COM-2026-EXACT-ALARM-GH** (GitHub issue, search-result snippet): Reminder app on targetSdk 36: SCHEDULE_EXACT_ALARM denied by default on Android 14+; USE_EXACT_ALARM requires Play declaration and review restricted to alarm/timer/calendar apps. <https://github.com/mahirozdin/alliswell/issues/11>
