# Store compliance check: ./my-app

- Checker v0.4.0 | rules snapshot 2026-10-10 (102 rules: {'apple': 53, 'google': 49}) | rules sha256 3b87f46ffe1e78fc
- Monorepo: False | apps: 1
- Output rule: HARD RULE: report ONLY the items in `findings`. Each one is verified from code, config, build or store-listing data. Anything the checker could not verify is dropped: do not mention it, soften it, hedge it, or present it as a possible cause. Other verdict statuses are internal coverage accounting, not user-facing causes.

## App `.` (expo-managed)
- Platforms: {'ios': 'assumed', 'android': 'assumed'}

### Verified issues (5)
- **CUR-APL-5.1.1ii-CONSENT** Consent for data collection; purpose strings; no paywalled consent - Evidence: NSMicrophoneUsageDescription not found in app.json ios.infoPlist, config-plugin options or Info.plist (config fully static). Source: https://developer.apple.com/app-store/review/guidelines/#5.1.1
  - Fix: Add NSMicrophoneUsageDescription (app.json ios.infoPlist or the expo-audio/expo-av 'microphonePermission' plugin option) that explains the voice feature.
- **CUR-APL-UR-IOS13** Minimum deployment target iOS 13 - Evidence: deployment target 12.0 (expo-build-properties). Source: https://developer.apple.com/news/upcoming-requirements/
  - Fix: Raise the iOS deployment target to 13.0 or later.
- **CUR-APL-MIC** Microphone usage description required - Evidence: NSMicrophoneUsageDescription not found in app.json ios.infoPlist, config-plugin options or Info.plist (config fully static). Source: https://developer.apple.com/documentation/bundleresources/information-property-list/nsmicrophoneusagedescription
  - Fix: Add NSMicrophoneUsageDescription (app.json ios.infoPlist or the expo-audio/expo-av 'microphonePermission' plugin option) that explains the voice feature.
- **CUR-APL-SPEECH** Speech recognition usage description required - Evidence: NSSpeechRecognitionUsageDescription not found in app.json ios.infoPlist, config-plugin options or Info.plist (config fully static). Source: https://developer.apple.com/documentation/bundleresources/information-property-list/nsspeechrecognitionusagedescription
  - Fix: Add NSSpeechRecognitionUsageDescription.
- **CUR-APL-HK-USAGE** HealthKit usage descriptions and privacy policy - Evidence: HealthKit integration: dependency/entitlement: react-native-health; no NSHealthShareUsageDescription / NSHealthUpdateUsageDescription found. Source: https://developer.apple.com/documentation/healthkit/protecting-user-privacy
  - Fix: Add NSHealthShareUsageDescription (read) and NSHealthUpdateUsageDescription (write) and a privacy policy.

## Limits
- Static source/config scan only unless --aab/--apk/--ipa is given (then Greenlight inspects the artifact). PASS without an artifact is labelled verification_level=source-config.
- app.config.js/ts is never executed; values that only exist there are not verifiable and produce no finding.
- Library-contributed Android permissions are only checked when an artifact is given.
- App Store Connect / store-listing data is only used when supplied in .compliance/store.json; checks without their data emit nothing.
- Excluded by design (not verifiable from code/config/build/listing data): lookalike / terminated-developer 4.3 flags, reply-vs-resubmit rejection loops, subscription-attachment backend glitches.
- Rules gated on a feature run only when the feature is detected or declared in .compliance/features.json.
- Only Expo (managed/bare) and React Native app roots are checked; Flutter, native and Capacitor roots are listed but not checked.
