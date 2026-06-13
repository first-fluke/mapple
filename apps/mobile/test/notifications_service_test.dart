// Notifications service unit tests — no platform plugins required.
//
// Tests the no-op service (used when Firebase is not configured) and the
// Riverpod NotificationsNotifier with a stubbed service implementation.

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:mobile/features/notifications/notifications_provider.dart';
import 'package:mobile/features/notifications/notifications_service.dart';

// ---------------------------------------------------------------------------
// Stub NotificationsService
// ---------------------------------------------------------------------------

class _StubNotificationsService implements NotificationsService {
  bool permissionGranted;
  final String? token;
  bool disposeCalled = false;
  int requestPermissionCallCount = 0;

  _StubNotificationsService({
    this.permissionGranted = false,
    this.token,
  });

  @override
  Future<bool> requestPermission() async {
    requestPermissionCallCount++;
    return permissionGranted;
  }

  @override
  Future<String?> getToken() async => token;

  @override
  Stream<PushMessage> get onMessage => const Stream.empty();

  @override
  Stream<PushMessage> get onMessageOpenedApp => const Stream.empty();

  @override
  void dispose() => disposeCalled = true;
}

// ---------------------------------------------------------------------------
// Helper
// ---------------------------------------------------------------------------

ProviderContainer _makeContainer(_StubNotificationsService stub) {
  return ProviderContainer(
    overrides: [
      notificationsServiceProvider.overrideWithValue(stub),
    ],
  );
}

// ---------------------------------------------------------------------------
// Tests: createNotificationsService factory
// ---------------------------------------------------------------------------

void main() {
  group('createNotificationsService', () {
    test('returns a NotificationsService instance', () {
      final service = createNotificationsService();
      expect(service, isA<NotificationsService>());
    });

    test('no-op service returns false for requestPermission', () async {
      final service = createNotificationsService();
      final result = await service.requestPermission();
      expect(result, isFalse);
    });

    test('no-op service returns null FCM token', () async {
      final service = createNotificationsService();
      final token = await service.getToken();
      expect(token, isNull);
    });

    test('no-op service onMessage emits nothing', () async {
      final service = createNotificationsService();
      final events = await service.onMessage.toList().timeout(
            const Duration(milliseconds: 50),
            onTimeout: () => [],
          );
      expect(events, isEmpty);
    });

    test('no-op service dispose does not throw', () {
      final service = createNotificationsService();
      expect(service.dispose, returnsNormally);
    });
  });

  // ---------------------------------------------------------------------------
  // Tests: NotificationsNotifier
  // ---------------------------------------------------------------------------

  group('NotificationsNotifier — initial state', () {
    test('starts with isEnabled=false and isPermissionGranted=false', () {
      final stub = _StubNotificationsService();
      final container = _makeContainer(stub);
      addTearDown(container.dispose);

      final state = container.read(notificationsProvider);
      expect(state.isEnabled, isFalse);
      expect(state.isPermissionGranted, isFalse);
      expect(state.fcmToken, isNull);
    });
  });

  group('NotificationsNotifier — enable()', () {
    test('enable() with permission granted sets isEnabled=true', () async {
      final stub = _StubNotificationsService(
        permissionGranted: true,
        token: 'fcm-token-abc',
      );
      final container = _makeContainer(stub);
      addTearDown(container.dispose);

      final granted =
          await container.read(notificationsProvider.notifier).enable();

      expect(granted, isTrue);
      final state = container.read(notificationsProvider);
      expect(state.isEnabled, isTrue);
      expect(state.isPermissionGranted, isTrue);
      expect(state.fcmToken, 'fcm-token-abc');
    });

    test('enable() with permission denied keeps isEnabled=false', () async {
      final stub = _StubNotificationsService(permissionGranted: false);
      final container = _makeContainer(stub);
      addTearDown(container.dispose);

      final granted =
          await container.read(notificationsProvider.notifier).enable();

      expect(granted, isFalse);
      final state = container.read(notificationsProvider);
      expect(state.isEnabled, isFalse);
      expect(state.isPermissionGranted, isFalse);
    });
  });

  group('NotificationsNotifier — disable()', () {
    test('disable() after enable sets isEnabled=false', () async {
      final stub = _StubNotificationsService(permissionGranted: true);
      final container = _makeContainer(stub);
      addTearDown(container.dispose);

      await container.read(notificationsProvider.notifier).enable();
      container.read(notificationsProvider.notifier).disable();

      expect(container.read(notificationsProvider).isEnabled, isFalse);
    });
  });

  group('NotificationsNotifier — toggle()', () {
    test('toggle() when disabled and permission granted enables', () async {
      final stub =
          _StubNotificationsService(permissionGranted: true, token: 't1');
      final container = _makeContainer(stub);
      addTearDown(container.dispose);

      final result =
          await container.read(notificationsProvider.notifier).toggle();

      expect(result, isTrue);
      expect(container.read(notificationsProvider).isEnabled, isTrue);
    });

    test('toggle() when enabled disables without calling requestPermission',
        () async {
      final stub =
          _StubNotificationsService(permissionGranted: true, token: 't1');
      final container = _makeContainer(stub);
      addTearDown(container.dispose);

      await container.read(notificationsProvider.notifier).enable();
      final callsBefore = stub.requestPermissionCallCount;

      final result =
          await container.read(notificationsProvider.notifier).toggle();

      expect(result, isFalse);
      expect(container.read(notificationsProvider).isEnabled, isFalse);
      // disable() must NOT call requestPermission again
      expect(stub.requestPermissionCallCount, callsBefore);
    });

    test('toggle() when disabled and permission denied returns false', () async {
      final stub = _StubNotificationsService(permissionGranted: false);
      final container = _makeContainer(stub);
      addTearDown(container.dispose);

      final result =
          await container.read(notificationsProvider.notifier).toggle();

      expect(result, isFalse);
      expect(container.read(notificationsProvider).isEnabled, isFalse);
    });
  });

  // ---------------------------------------------------------------------------
  // Tests: service disposal
  // ---------------------------------------------------------------------------

  group('NotificationsService disposal', () {
    test('dispose() on stub sets disposeCalled=true', () {
      final stub = _StubNotificationsService();
      expect(stub.disposeCalled, isFalse);
      stub.dispose();
      expect(stub.disposeCalled, isTrue);
    });

    test('no-op service dispose() does not throw', () {
      final service = createNotificationsService();
      expect(service.dispose, returnsNormally);
    });
  });
}
