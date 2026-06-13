import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/core/api/dio_client.dart';
import 'package:mobile/features/notifications/device_token_repository.dart';
import 'package:mobile/features/notifications/notifications_service.dart';

// ---------------------------------------------------------------------------
// Repository provider
// ---------------------------------------------------------------------------

final deviceTokenRepositoryProvider = Provider<DeviceTokenRepository>((ref) {
  return DeviceTokenRepository(ref.watch(dioProvider));
});

// ---------------------------------------------------------------------------
// Service provider — singleton for the app lifetime
// ---------------------------------------------------------------------------

final notificationsServiceProvider = Provider<NotificationsService>((ref) {
  final repo = ref.read(deviceTokenRepositoryProvider);

  final service = createNotificationsService(
    onTokenRefreshed: (token) async {
      await repo.registerToken(token);
    },
  );

  ref.onDispose(service.dispose);
  return service;
});

// ---------------------------------------------------------------------------
// Notifications-enabled toggle state
// ---------------------------------------------------------------------------

class NotificationsState {
  final bool isEnabled;
  final bool isPermissionGranted;
  final String? fcmToken;

  const NotificationsState({
    this.isEnabled = false,
    this.isPermissionGranted = false,
    this.fcmToken,
  });

  NotificationsState copyWith({
    bool? isEnabled,
    bool? isPermissionGranted,
    String? Function()? fcmToken,
  }) {
    return NotificationsState(
      isEnabled: isEnabled ?? this.isEnabled,
      isPermissionGranted: isPermissionGranted ?? this.isPermissionGranted,
      fcmToken: fcmToken != null ? fcmToken() : this.fcmToken,
    );
  }
}

// ---------------------------------------------------------------------------
// Notifier
// ---------------------------------------------------------------------------

class NotificationsNotifier extends Notifier<NotificationsState> {
  @override
  NotificationsState build() => const NotificationsState();

  /// Requests permission and enables notifications if granted.
  ///
  /// On success, fetches the FCM token and registers it with the backend.
  Future<bool> enable() async {
    final service = ref.read(notificationsServiceProvider);
    final granted = await service.requestPermission();
    if (granted) {
      final token = await service.getToken();
      state = state.copyWith(
        isEnabled: true,
        isPermissionGranted: true,
        fcmToken: () => token,
      );
      // Register the token with the backend if one was obtained.
      if (token != null) {
        final repo = ref.read(deviceTokenRepositoryProvider);
        await repo.registerToken(token);
      }
    } else {
      state = state.copyWith(
        isEnabled: false,
        isPermissionGranted: false,
      );
    }
    return granted;
  }

  /// Disables notifications (does not revoke OS permission).
  void disable() {
    state = state.copyWith(isEnabled: false);
  }

  /// Toggles the enabled state, requesting permission when enabling.
  Future<bool> toggle() async {
    if (state.isEnabled) {
      disable();
      return false;
    }
    return enable();
  }
}

final notificationsProvider =
    NotifierProvider<NotificationsNotifier, NotificationsState>(
  NotificationsNotifier.new,
);
