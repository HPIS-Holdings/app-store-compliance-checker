#!/usr/bin/env python3
"""Generate the test fixtures (committed). Each fixture is a minimal repo; expectations live in test_checker.py."""
import json, shutil
from pathlib import Path
F = Path(__file__).parent / "fixtures"
def w(path, content):
    p = F / path; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content if isinstance(content, str) else json.dumps(content, indent=1))
def expo(fx, name, slug, extra=None, deps=None, sub="", tsdk=36, ios_t="15.1"):
    e = {"name": name, "slug": slug, "version": "1.0.0", "ios": {"bundleIdentifier": f"com.example.{slug.replace('-', '')}", "config": {"usesNonExemptEncryption": False}},
         "android": {"package": f"com.example.{slug.replace('-', '')}"},
         "plugins": [["expo-build-properties", {"android": {"targetSdkVersion": tsdk}, "ios": {"deploymentTarget": ios_t}}]]}
    for k, v in (extra or {}).items():
        if k == "plugins": e["plugins"] += v
        elif isinstance(v, dict) and isinstance(e.get(k), dict): e[k].update(v)
        else: e[k] = v
    w(f"{fx}/{sub}app.json", {"expo": e})
    w(f"{fx}/{sub}package.json", {"name": slug, "dependencies": {"expo": "~54.0.0", "react-native": "0.81.4", "expo-build-properties": "~1.0.0", **(deps or {})}})
PRIV = "import { Link } from 'expo-router';\nexport default function Privacy() { return <Link href='https://example.org/privacy'>Privacy Policy</Link>; }\n"
if F.exists(): shutil.rmtree(F)

# simple non-health utility (positive / clean)
expo("simple-clean", "Tip Splitter", "tip-splitter"); w("simple-clean/app/privacy.tsx", PRIV)
w("simple-clean/app/index.tsx", "export default function Home() { const split = (t, n) => t / n; return null; }\n")

# game with 'health' points in many files -> must not be a health app; expo-av playback only -> no microphone
expo("game", "Pixel Dungeon", "pixel-dungeon", deps={"expo-av": "~15.0.0"}); w("game/app/privacy.tsx", PRIV)
for i in range(7): w(f"game/src/enemy{i}.ts", f"export const enemy{i} = {{ health: 10, maxHealth: 20 }}; // player health bar\n")
w("game/src/sound.ts", "import { Audio } from 'expo-av';\nexport async function boom() { const { sound } = await Audio.Sound.createAsync(require('./boom.mp3')); await sound.playAsync(); }\n")

# wallpaper app (positive / clean)
expo("wallpaper", "Wallpaper Studio", "wallpaper-studio", deps={"expo-media-library": "~17.0.0"},
     extra={"ios": {"infoPlist": {"NSPhotoLibraryAddUsageDescription": "Save wallpapers you choose to your photo library."}}})
w("wallpaper/app/privacy.tsx", PRIV); w("wallpaper/app/index.tsx", "import * as MediaLibrary from 'expo-media-library';\nexport const save = (uri) => MediaLibrary.saveToLibraryAsync(uri);\n")

# health app, good (HealthKit keys, mic key, disclaimers, deletion)
expo("health-good", "Wellness Journal", "wellness-journal", deps={"@kingstinct/react-native-healthkit": "^9.0.0", "expo-audio": "~1.0.0"},
     extra={"plugins": [["@kingstinct/react-native-healthkit", {"NSHealthShareUsageDescription": "Reads blood pressure to complete your wellness journal.", "NSHealthUpdateUsageDescription": "Saves logged water intake to Apple Health."}],
                        ["expo-audio", {"microphonePermission": "Wellness Journal records your voice when you dictate a meal log."}]]})
w("health-good/app/privacy.tsx", PRIV)
w("health-good/app/voice.tsx", "import { useAudioRecorder, RecordingPresets } from 'expo-audio';\nexport function useVoice() { return useAudioRecorder(RecordingPresets.HIGH_QUALITY); }\n")
w("health-good/app/settings.tsx", "export const DeleteAccountButton = () => 'Delete account'; // calls api.deleteAccount()\n")
w("health-good/app/about.tsx", "export const Disclaimer = 'Wellness Journal is not a medical device. Consult your doctor before changing treatment.';\n")

# health app, bad (negative): HealthKit without keys, recording without mic key, speech lib without key, targetSdk 34, iOS 12
expo("health-bad", "Health Tracker", "health-tracker", tsdk=34, ios_t="12.0",
     deps={"react-native-health": "^1.19.0", "expo-audio": "~1.0.0", "expo-speech-recognition": "^2.1.0"})
w("health-bad/app/voice.tsx", "import { useAudioRecorder, RecordingPresets } from 'expo-audio';\nimport { ExpoSpeechRecognitionModule } from 'expo-speech-recognition';\nexport function useVoice() { ExpoSpeechRecognitionModule.start({ lang: 'en-US' }); return useAudioRecorder(RecordingPresets.HIGH_QUALITY); }\n")

# AI in app code + a hardcoded secret (redaction test)
expo("ai-client", "Recipe Helper", "recipe-helper", deps={"openai": "^5.0.0"}); w("ai-client/app/privacy.tsx", PRIV)
w("ai-client/src/ai.ts", "import OpenAI from 'openai';\nconst OPENAI_API_KEY = \"sk-proj-abcdefghijklmnopqrstuvwxyz0123456789\";\nconst client = new OpenAI({ apiKey: OPENAI_API_KEY });\nexport const ask = (q) => client.responses.create({ model: 'x', input: q });\n")

# backend-only AI: app calls own backend; convex/ calls the AI provider
expo("backend-ai", "Study Buddy", "study-buddy", sub="apps/mobile/", deps={"convex": "^1.20.0"}); w("backend-ai/apps/mobile/app/privacy.tsx", PRIV)
w("backend-ai/package.json", {"name": "study-buddy", "private": True, "workspaces": ["apps/*"]})
w("backend-ai/apps/mobile/app/chat.tsx", "import { useAction } from 'convex/react';\nexport function useChat() { return useAction('chat:ask'); }\n")
w("backend-ai/convex/chat.ts", "import Anthropic from '@anthropic-ai/sdk';\nexport const ask = async (q) => new Anthropic().messages.create({ model: 'x', max_tokens: 100, messages: [{ role: 'user', content: q }] });\n")

# subscription app: RevenueCat, no restore, no paywall disclosures (negative for keyword -> NEEDS_REVIEW, never FAIL)
expo("subscription", "Focus Timer Pro", "focus-timer-pro", deps={"react-native-purchases": "^9.2.0"}); w("subscription/app/privacy.tsx", PRIV)
w("subscription/app/paywall.tsx", "import Purchases from 'react-native-purchases';\nexport const buy = (p) => Purchases.purchasePackage(p);\n")

# real alarm clock app with USE_EXACT_ALARM (must be NEEDS_REVIEW, not FAIL)
expo("alarm-app", "Sunrise Alarm Clock", "sunrise-alarm", extra={"android": {"permissions": ["USE_EXACT_ALARM", "POST_NOTIFICATIONS"]}}); w("alarm-app/app/privacy.tsx", PRIV)
# reminder app (not alarm/calendar) declaring USE_EXACT_ALARM (NEEDS_REVIEW with stronger fix text, still not FAIL)
expo("reminder-exact", "Plant Water Reminders", "plant-reminders", extra={"android": {"permissions": ["USE_EXACT_ALARM"]}}); w("reminder-exact/app/privacy.tsx", PRIV)

# monorepo: apps/mobile (expo), apps/web (next), packages/ui
w("monorepo/package.json", {"name": "mono", "private": True, "workspaces": ["apps/*", "packages/*"]})
expo("monorepo", "Shop List", "shop-list", sub="apps/mobile/"); w("monorepo/apps/mobile/app/privacy.tsx", PRIV)
w("monorepo/apps/web/package.json", {"name": "web", "dependencies": {"next": "15.0.0", "react": "19.0.0"}})
w("monorepo/packages/ui/package.json", {"name": "ui", "dependencies": {"react": "19.0.0"}})

# dynamic Expo config only (app.config.ts) + mic recording: unresolved, never FAIL
w("dynamic-config/package.json", {"name": "dyn", "dependencies": {"expo": "~54.0.0", "react-native": "0.81.4", "expo-audio": "~1.0.0"}})
w("dynamic-config/app.config.ts", "export default ({ config }) => ({ ...config, name: process.env.APP_NAME, ios: { infoPlist: { NSMicrophoneUsageDescription: process.env.MIC_TEXT } } });\n")
w("dynamic-config/app/voice.tsx", "import { useAudioRecorder, RecordingPresets } from 'expo-audio';\nexport const useVoice = () => useAudioRecorder(RecordingPresets.HIGH_QUALITY);\n")

# discovery-only stacks
w("rn-bare/package.json", {"name": "rnbare", "dependencies": {"react-native": "0.81.4"}}); w("rn-bare/ios/.keep", ""); w("rn-bare/android/.keep", "")
w("rn-bare/ios/RNBare/Info.plist", "<plist><dict><key>NSMicrophoneUsageDescription</key><string>Voice notes</string></dict></plist>")
w("native-android/settings.gradle", "include ':app'\n"); w("native-android/app/src/main/AndroidManifest.xml", "<manifest><uses-permission android:name=\"android.permission.RECORD_AUDIO\"/></manifest>")
w("flutter-app/pubspec.yaml", "name: fl\nflutter:\n  uses-material-design: true\n")
# --- v0.3 code-path fixtures ---
# Convex template: deletion UI -> backend deletes workspace rows only (identity survives)
expo("deletion-data-only", "Shelf Notes", "shelf-notes", sub="apps/mobile/", deps={"@convex-dev/auth": "^0.0.94", "convex": "^1.20.0"})
w("deletion-data-only/apps/mobile/app/privacy.tsx", PRIV)
w("deletion-data-only/apps/mobile/app/auth.tsx", "import { useAuthActions } from '@convex-dev/auth/react';\nexport function useAuth() { const { signIn } = useAuthActions(); return () => signIn('password', { flow: 'signUp' }); }\n")
w("deletion-data-only/apps/mobile/app/more.tsx", "import { useMutation } from 'convex/react';\nimport { makeFunctionReference } from 'convex/server';\nconst requestDeletionRef = makeFunctionReference<'mutation'>('workspaces:requestDeletion');\nexport function More() {\n  const requestDeletion = useMutation(requestDeletionRef);\n  function deleteRemoteWorkspace() {\n    void requestDeletion({ workspaceId: 'w' });\n  }\n  return deleteRemoteWorkspace;\n}\n")
w("deletion-data-only/convex/workspaces.ts", "import { mutation } from './_generated/server';\nexport const requestDeletion = mutation({ args: {}, handler: async (ctx, args) => {\n  const rows = await ctx.db.query('items').collect();\n  for (const row of rows) await ctx.db.delete(row._id);\n} });\n")
# Supabase: deletion UI -> helper -> edge function -> auth.admin.deleteUser
expo("deletion-identity", "Trip Ledger", "trip-ledger", deps={"@supabase/supabase-js": "^2.45.0"})
w("deletion-identity/app/privacy.tsx", PRIV)
w("deletion-identity/src/account.ts", "import { supabase } from './client';\nexport async function signUpUser(email, password) { return supabase.auth.signUp({ email, password }); }\nasync function invokeDeletion(body) {\n  return supabase.functions.invoke('delete-account', { body });\n}\nexport async function deleteMyAccountNow() {\n  await invokeDeletion({ confirm: true });\n}\n")
w("deletion-identity/app/settings.tsx", "import { deleteMyAccountNow } from '../src/account';\nexport function Settings() {\n  const onDelete = () => deleteMyAccountNow();\n  return 'Delete account';\n}\n")
w("deletion-identity/supabase/functions/delete-account/index.ts", "Deno.serve(async (req) => {\n  const admin = createClient();\n  const { data } = await admin.auth.getUser();\n  await admin.auth.admin.deleteUser(data.user.id);\n  return new Response('ok');\n});\n")
# external checkout reachable in native vs web-gated
expo("checkout-native", "Course Pass", "course-pass"); w("checkout-native/app/privacy.tsx", PRIV)
w("checkout-native/app/upgrade.tsx", "import * as Linking from 'expo-linking';\nexport async function upgrade(url) { await Linking.openURL('https://buy.stripe.com/test_abc'); }\n")
expo("checkout-webgated", "Course Pass Web", "course-pass-web", deps={"react-native-iap": "^12.0.0"}); w("checkout-webgated/app/privacy.tsx", PRIV)
w("checkout-webgated/app/upgrade.tsx", "import { Platform } from 'react-native';\nimport * as Linking from 'expo-linking';\nimport { requestPurchase } from 'react-native-iap';\nexport async function upgrade(checkoutUrl) {\n  if (Platform.OS === 'web') {\n    await Linking.openURL(checkoutUrl);\n    return;\n  }\n  await requestPurchase({ sku: 'pro' });\n}\n")
expo("checkout-indirect", "Lifetime Unlock", "lifetime-unlock"); w("checkout-indirect/app/privacy.tsx", PRIV)
w("checkout-indirect/app/buy.tsx", "import * as Linking from 'expo-linking';\nexport async function buy(createCheckout) {\n  const result = await createCheckout({ productId: 'lifetime' });\n  await Linking.openURL(result.url);\n}\n")
# veterinary health app
expo("vet-app", "Pet Kidney Care", "pet-kidney-care"); w("vet-app/app/privacy.tsx", PRIV)
w("vet-app/app/index.tsx", "export const Note = 'Track your cat kidney values with your veterinarian.';\n")
# dynamic config with literal purpose string + env-dependent key
w("dynamic-literal/package.json", {"name": "dynlit", "dependencies": {"expo": "~57.0.0", "react-native": "0.86.0", "expo-audio": "~1.0.0"}})
w("dynamic-literal/app.config.ts", "export default ({ config }) => ({\n  ...config,\n  ios: { infoPlist: {\n    NSMicrophoneUsageDescription: 'Records voice notes you dictate.',\n    NSCameraUsageDescription: process.env.CAMERA_TEXT,\n  } },\n});\n")
w("dynamic-literal/app/voice.tsx", "import { useAudioRecorder, RecordingPresets } from 'expo-audio';\nexport const useVoice = () => useAudioRecorder(RecordingPresets.HIGH_QUALITY);\n")
# Expo SDK 57 without explicit targetSdk (derived default)
w("derived-default/package.json", {"name": "dd", "dependencies": {"expo": "~57.0.7", "react-native": "0.86.0"}})
w("derived-default/app.json", {"expo": {"name": "Unit Converter", "slug": "unit-converter"}}); w("derived-default/app/privacy.tsx", PRIV)
# AI boundary: client invokes convex action that calls the provider with health fields; consent flag in caller
expo("ai-boundary", "Meal Coach", "meal-coach", sub="apps/mobile/", deps={"convex": "^1.20.0"}); w("ai-boundary/apps/mobile/app/privacy.tsx", PRIV)
w("ai-boundary/apps/mobile/app/coach.tsx", "import { useAction } from 'convex/react';\nimport { api } from '../../../convex/_generated/api';\nexport function Coach({ aiConsentGiven }) {\n  const ask = useAction(api.coach.askCoach);\n  return () => aiConsentGiven && ask({ q: 'hi' });\n}\n")
w("ai-boundary/convex/coach.ts", "import { action } from './_generated/server';\nexport const askCoach = action({ args: {}, handler: async (ctx, args) => {\n  const body = { weight: args.weight, glucose: args.glucose };\n  return fetch('https://api.openai.com/v1/responses', { method: 'POST', body: JSON.stringify(body) });\n} });\n")
print("fixtures written:", sorted(p.name for p in F.iterdir()))
