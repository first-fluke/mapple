# Push Notifications Setup

This document walks through activating Firebase Cloud Messaging (FCM) in Globe CRM Mobile. The app ships with a no-op implementation that compiles and passes all tests without any Firebase credentials. Follow the steps below to switch it to the live implementation.

## Overview

| File | Role |
|---|---|
| `lib/features/notifications/notifications_service.dart` | Abstract interface + live `_FirebaseNotificationsService` + no-op fallback |
| `lib/features/notifications/notifications_provider.dart` | Riverpod providers: service singleton, `NotificationsNotifier` |
| `lib/features/notifications/device_token_repository.dart` | Posts FCM token to `POST /notifications/device-tokens` |
| `lib/main.dart` | Firebase init stub (commented out until credentials are ready) |

The feature flag `_kFirebaseConfigured` (driven by `--dart-define=FIREBASE_CONFIGURED=true`) controls which implementation is active. When the flag is false the app runs without any Firebase symbols being invoked.

---

## Step 1: Create a Firebase Project

1. Go to [https://console.firebase.google.com](https://console.firebase.google.com) and click **Add project**.
2. Name it (e.g. `globe-crm`) and follow the wizard. You do not need Google Analytics for basic push.
3. In **Project settings > Cloud Messaging**, verify that FCM API (v1) is enabled.

---

## Step 2: Register the Android App

1. In the Firebase console sidebar click **Add app** and choose the Android icon.
2. Enter the package name: `com.globecrm.mobile` (must match `android/app/build.gradle.kts` `applicationId`).
3. Download `google-services.json`.
4. Copy it to:

```
apps/mobile/android/app/google-services.json
```

A template showing all required fields is at `android/app/google-services.json.example`. Do **not** commit the real file to version control — add it to `.gitignore` if it is not already there.

---

## Step 3: Register the iOS App

1. Click **Add app** again and choose the iOS icon.
2. Enter the bundle ID: `com.globecrm.mobile` (must match `PRODUCT_BUNDLE_IDENTIFIER` in Xcode).
3. Download `GoogleService-Info.plist`.
4. Copy it to:

```
apps/mobile/ios/Runner/GoogleService-Info.plist
```

A template is at `ios/Runner/GoogleService-Info.plist.example`. Do **not** commit the real file.

### iOS: Enable Push Notifications capability in Xcode

1. Open `ios/Runner.xcworkspace` in Xcode.
2. Select the **Runner** target, go to **Signing & Capabilities**.
3. Click **+ Capability** and add **Push Notifications**.
4. Also add **Background Modes** and check **Remote notifications**.

`Info.plist` already has the `UIBackgroundModes` key set (`remote-notification` and `fetch`) so step 4 is pre-wired.

### iOS: APNS key or certificate

FCM on iOS requires an Apple Push Notification service (APNs) key or certificate uploaded to Firebase:

1. In the Apple Developer portal go to **Certificates, IDs & Profiles > Keys** and create a key with **Apple Push Notifications service (APNs)** enabled.
2. Download the `.p8` file.
3. In the Firebase console go to **Project settings > Cloud Messaging > Apple app configuration** and upload the `.p8` key (or a `.p12` certificate).

---

## Step 4: Install FlutterFire CLI and Configure

```bash
dart pub global activate flutterfire_cli
flutterfire configure --project=<your-firebase-project-id>
```

This generates `apps/mobile/lib/firebase_options.dart`. The file is referenced by `main.dart` and must exist before the live flag is turned on.

---

## Step 5: Uncomment the Firebase Init Block in main.dart

Open `apps/mobile/lib/main.dart` and replace the commented block with the live version:

```dart
import 'package:firebase_core/firebase_core.dart';
import 'package:mobile/features/notifications/notifications_provider.dart';
import 'package:mobile/features/notifications/notifications_service.dart';

import 'firebase_options.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );

  // Create the ProviderContainer before runApp so the service can be
  // initialised (wires FCM listeners) before the first frame.
  final container = ProviderContainer();
  final service = container.read(notificationsServiceProvider);
  await initNotificationsService(service);

  runApp(UncontrolledProviderScope(container: container, child: const GlobeApp()));
}
```

---

## Step 6: Enable the Android Gradle Plugin

Open `android/settings.gradle.kts` and uncomment:

```kotlin
id("com.google.gms.google-services") version "4.4.2" apply false
```

Then open `android/app/build.gradle.kts` and uncomment:

```kotlin
id("com.google.gms.google-services")
```

These two lines are already present but commented out so the build works without `google-services.json`.

---

## Step 7: Activate the Feature Flag

The preferred method is a `--dart-define` so the flag can be set per build variant without modifying source:

```bash
# Development
flutter run --dart-define=FIREBASE_CONFIGURED=true

# Release
flutter build apk --dart-define=FIREBASE_CONFIGURED=true
flutter build ios --dart-define=FIREBASE_CONFIGURED=true
```

Alternatively, edit `lib/features/notifications/notifications_service.dart` line 29 and change the `defaultValue` to `true`:

```dart
const bool _kFirebaseConfigured = bool.fromEnvironment(
  'FIREBASE_CONFIGURED',
  defaultValue: true, // changed from false
);
```

---

## Step 8: Verify

```bash
flutter pub get
flutter analyze        # must report 0 issues
flutter test           # all tests must pass
flutter run            # check device logs for [FCM] token registered
```

On first launch after permission is granted the app will:

1. Call `FirebaseMessaging.instance.requestPermission()`.
2. Fetch the FCM registration token.
3. POST the token to `POST /notifications/device-tokens` with body:

```json
{ "token": "<fcm_registration_token>", "platform": "ios" | "android" }
```

The backend endpoint is part of the Globe CRM API (`apps/api`). The Dio instance used is the shared `dioProvider` from `lib/core/api/dio_client.dart`, which applies the `AuthInterceptor` (Bearer JWT). If the user is not authenticated the 401 response is silently swallowed; the token is re-registered on the next `onTokenRefresh` event or the next permission grant.

---

## Token Refresh

The `_FirebaseNotificationsService` subscribes to `FirebaseMessaging.instance.onTokenRefresh`. When the FCM token rotates (e.g., after app reinstall or token expiry) `DeviceTokenRepository.registerToken()` is called automatically. The backend should treat `POST /notifications/device-tokens` as an upsert keyed on `(user_id, platform)`.

---

## Background Messages

A top-level Dart function `firebaseMessagingBackgroundHandler` is registered via `FirebaseMessaging.onBackgroundMessage()`. It runs in a separate Dart isolate. Add any lightweight data processing there; do not access UI or most Flutter plugins from that isolate.

---

## Files That Require Real Credentials (Do Not Commit)

| File | Description |
|---|---|
| `android/app/google-services.json` | Android Firebase config |
| `ios/Runner/GoogleService-Info.plist` | iOS Firebase config |
| `lib/firebase_options.dart` | Generated by `flutterfire configure` |

Template placeholders:

| File | Description |
|---|---|
| `android/app/google-services.json.example` | Android template |
| `ios/Runner/GoogleService-Info.plist.example` | iOS template |

---

## What Is Already Implemented (No Credentials Required)

- `_FirebaseNotificationsService`: full implementation behind `_kFirebaseConfigured`
  - `requestPermission()` — iOS + Android 13+ POST_NOTIFICATIONS
  - `getToken()` — APNS handshake on iOS then FCM token fetch
  - `onMessage` / `onMessageOpenedApp` streams
  - `getInitialMessage()` for cold-launch handling
  - `onTokenRefresh` subscription
  - Top-level `firebaseMessagingBackgroundHandler`
  - All subscriptions cancelled in `dispose()`
- `DeviceTokenRepository.registerToken()` — POST with graceful 401/network degradation
- `NotificationsNotifier.enable()` — registers token immediately on first grant
- Android: `POST_NOTIFICATIONS` permission in `AndroidManifest.xml`; Google Services plugin wiring commented in Gradle files
- iOS: `UIBackgroundModes` (`remote-notification`, `fetch`) in `Info.plist`; Push Notifications capability notes above
