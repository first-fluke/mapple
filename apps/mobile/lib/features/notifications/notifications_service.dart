// TODO(oma-deferred): provision Firebase (google-services.json /
// GoogleService-Info.plist) to enable push notifications. Until those files
// are present this service no-ops gracefully so the app builds and runs
// without Firebase credentials.
//
// To activate:
//   1. Add google-services.json    →  android/app/google-services.json
//   2. Add GoogleService-Info.plist →  ios/Runner/GoogleService-Info.plist
//   3. Run `flutterfire configure` — generates lib/firebase_options.dart
//   4. Uncomment the Firebase init block in lib/main.dart
//   5. Pass --dart-define=FIREBASE_CONFIGURED=true to flutter run/build
//      (or flip `_kFirebaseConfigured` to `true` directly below)
//
// See docs/push-notifications-setup.md for the complete walkthrough.

import 'dart:async';
import 'dart:io';

import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';

// ---------------------------------------------------------------------------
// Feature flag
//
// Preferred: --dart-define=FIREBASE_CONFIGURED=true  (CI / release builds)
// Fallback : change the `defaultValue` to true after running flutterfire configure.
// ---------------------------------------------------------------------------

const bool _kFirebaseConfigured = bool.fromEnvironment(
  'FIREBASE_CONFIGURED',
  defaultValue: false,
);

// ---------------------------------------------------------------------------
// Top-level background handler (must be a top-level function).
// Firebase invokes this in a separate isolate when the app is terminated or
// in the background. The Firebase SDK calls Firebase.initializeApp()
// automatically before dispatching to this handler.
// ---------------------------------------------------------------------------

@pragma('vm:entry-point')
Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  debugPrint(
    '[FCM] background message: ${message.notification?.title ?? message.messageId}',
  );
}

// ---------------------------------------------------------------------------
// Domain model
// ---------------------------------------------------------------------------

/// Represents a received push message (foreground, background tap, or data).
class PushMessage {
  final String? title;
  final String? body;
  final Map<String, dynamic> data;

  const PushMessage({this.title, this.body, this.data = const {}});

  factory PushMessage.fromRemote(RemoteMessage message) => PushMessage(
        title: message.notification?.title,
        body: message.notification?.body,
        data: message.data,
      );

  @override
  String toString() => 'PushMessage(title: $title, body: $body, data: $data)';
}

// ---------------------------------------------------------------------------
// Abstract interface
// ---------------------------------------------------------------------------

/// Abstraction that isolates Firebase details from the rest of the app.
/// When [_kFirebaseConfigured] is false every method is a no-op and no
/// Firebase network calls are made.
abstract interface class NotificationsService {
  /// Requests OS-level notification permission (iOS / Android 13+).
  /// Returns true if granted, false otherwise.
  Future<bool> requestPermission();

  /// Returns the current FCM registration token, or null when not available.
  Future<String?> getToken();

  /// Stream of messages received while the app is in the foreground.
  Stream<PushMessage> get onMessage;

  /// Stream fired when the user taps a notification that opens the app.
  Stream<PushMessage> get onMessageOpenedApp;

  /// Disposes resources held by the service.
  void dispose();
}

// ---------------------------------------------------------------------------
// Live implementation — firebase_messaging
// Only instantiated when [_kFirebaseConfigured] is true.
// ---------------------------------------------------------------------------

class _FirebaseNotificationsService implements NotificationsService {
  final _messageController = StreamController<PushMessage>.broadcast();
  final _openedController = StreamController<PushMessage>.broadcast();

  StreamSubscription<RemoteMessage>? _onMessageSub;
  StreamSubscription<RemoteMessage>? _onMessageOpenedSub;
  StreamSubscription<String>? _tokenRefreshSub;

  /// Called whenever a new or refreshed FCM token is available.
  final void Function(String token)? onTokenRefreshed;

  _FirebaseNotificationsService({this.onTokenRefreshed});

  // ----- NotificationsService interface -----

  @override
  Future<bool> requestPermission() async {
    final settings = await FirebaseMessaging.instance.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );
    final status = settings.authorizationStatus;
    return status == AuthorizationStatus.authorized ||
        status == AuthorizationStatus.provisional;
  }

  @override
  Future<String?> getToken() async {
    // On iOS the APNS token must be available before an FCM token can be
    // fetched. Awaiting getAPNSToken() ensures it is resolved first.
    if (!kIsWeb && Platform.isIOS) {
      await FirebaseMessaging.instance.getAPNSToken();
    }
    return FirebaseMessaging.instance.getToken();
  }

  @override
  Stream<PushMessage> get onMessage => _messageController.stream;

  @override
  Stream<PushMessage> get onMessageOpenedApp => _openedController.stream;

  @override
  void dispose() {
    _onMessageSub?.cancel();
    _onMessageOpenedSub?.cancel();
    _tokenRefreshSub?.cancel();
    _messageController.close();
    _openedController.close();
  }

  // ----- Initialisation (called after Firebase.initializeApp) -----

  /// Wires up foreground, opened-app, initial-message, and token-refresh
  /// listeners. Must be called once after Firebase.initializeApp().
  Future<void> init() async {
    // Register the top-level background handler.
    FirebaseMessaging.onBackgroundMessage(firebaseMessagingBackgroundHandler);

    // Foreground messages.
    _onMessageSub = FirebaseMessaging.onMessage.listen((msg) {
      _messageController.add(PushMessage.fromRemote(msg));
    });

    // Tapped while app was in background (not terminated).
    _onMessageOpenedSub = FirebaseMessaging.onMessageOpenedApp.listen((msg) {
      _openedController.add(PushMessage.fromRemote(msg));
    });

    // Notification that caused a cold launch from terminated state.
    final initial = await FirebaseMessaging.instance.getInitialMessage();
    if (initial != null) {
      // Emit on next tick so listeners can attach first.
      Future.microtask(
        () => _openedController.add(PushMessage.fromRemote(initial)),
      );
    }

    // Token refresh — re-register with backend.
    _tokenRefreshSub = FirebaseMessaging.instance.onTokenRefresh.listen(
      (token) => onTokenRefreshed?.call(token),
    );
  }
}

// ---------------------------------------------------------------------------
// No-op implementation
// ---------------------------------------------------------------------------

class _NoOpNotificationsService implements NotificationsService {
  static const Stream<PushMessage> _empty = Stream.empty();

  @override
  Future<bool> requestPermission() async {
    debugPrint(
      '[NotificationsService] Firebase not configured — '
      'permission request skipped.',
    );
    return false;
  }

  @override
  Future<String?> getToken() async {
    debugPrint(
      '[NotificationsService] Firebase not configured — '
      'FCM token unavailable.',
    );
    return null;
  }

  @override
  Stream<PushMessage> get onMessage => _empty;

  @override
  Stream<PushMessage> get onMessageOpenedApp => _empty;

  @override
  void dispose() {}
}

// ---------------------------------------------------------------------------
// Factory
// ---------------------------------------------------------------------------

/// Creates the appropriate [NotificationsService] for the current environment.
///
/// [onTokenRefreshed] is invoked whenever an FCM token is refreshed by the
/// Firebase SDK. Only invoked by the live implementation.
NotificationsService createNotificationsService({
  void Function(String token)? onTokenRefreshed,
}) {
  if (_kFirebaseConfigured) {
    return _FirebaseNotificationsService(onTokenRefreshed: onTokenRefreshed);
  }
  return _NoOpNotificationsService();
}

/// Initialises the live service (wires FCM listeners).
/// Must be called after [Firebase.initializeApp()].
/// Safe to call on the no-op implementation — does nothing.
Future<void> initNotificationsService(NotificationsService service) async {
  if (service is _FirebaseNotificationsService) {
    await service.init();
  }
}
