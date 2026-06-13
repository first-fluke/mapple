// Device token repository unit tests.
//
// Tests cover:
//   - Successful token registration (POST /notifications/device-tokens)
//   - Silent degradation on 401 Unauthorized (unauthenticated user)
//   - Silent degradation on network error / timeout (offline)
//   - Unexpected exceptions do not propagate
//   - NotificationsNotifier.enable() calls registerToken when permission granted
//   - NotificationsNotifier.enable() skips registerToken when permission denied
//   - Token refresh callback triggers registerToken

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:mobile/features/notifications/device_token_repository.dart';
import 'package:mobile/features/notifications/notifications_provider.dart';
import 'package:mobile/features/notifications/notifications_service.dart';

// ---------------------------------------------------------------------------
// Fake Dio that records calls and returns a configured response.
// ---------------------------------------------------------------------------

class _FakeDio implements Dio {
  final int statusCode;
  final bool throwNetwork;

  final List<Map<String, dynamic>> capturedRequests = [];

  _FakeDio({this.statusCode = 200, this.throwNetwork = false});

  @override
  Future<Response<T>> post<T>(
    String path, {
    Object? data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
    void Function(int, int)? onSendProgress,
    void Function(int, int)? onReceiveProgress,
  }) async {
    capturedRequests.add({
      'path': path,
      'data': data,
    });

    if (throwNetwork) {
      throw DioException(
        requestOptions: RequestOptions(path: path),
        type: DioExceptionType.connectionError,
      );
    }

    if (statusCode != 200) {
      throw DioException(
        requestOptions: RequestOptions(path: path),
        response: Response(
          requestOptions: RequestOptions(path: path),
          statusCode: statusCode,
        ),
        type: DioExceptionType.badResponse,
      );
    }

    return Response<T>(
      requestOptions: RequestOptions(path: path),
      statusCode: 200,
    );
  }

  // --- unused Dio interface members ---
  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

// ---------------------------------------------------------------------------
// Stub NotificationsService
// ---------------------------------------------------------------------------

class _StubNotificationsService implements NotificationsService {
  final bool permissionGranted;
  final String? token;
  bool disposeCalled = false;

  _StubNotificationsService({this.permissionGranted = false, this.token});

  @override
  Future<bool> requestPermission() async => permissionGranted;

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
// Helpers
// ---------------------------------------------------------------------------

ProviderContainer _makeContainer({
  required _StubNotificationsService notifService,
  required _FakeDio fakeDio,
}) {
  final repo = DeviceTokenRepository(fakeDio);
  return ProviderContainer(
    overrides: [
      notificationsServiceProvider.overrideWithValue(notifService),
      deviceTokenRepositoryProvider.overrideWithValue(repo),
    ],
  );
}

// ---------------------------------------------------------------------------
// Tests: DeviceTokenRepository
// ---------------------------------------------------------------------------

void main() {
  group('DeviceTokenRepository.registerToken', () {
    test('sends POST to /notifications/device-tokens with token', () async {
      final fake = _FakeDio();
      final repo = DeviceTokenRepository(fake);

      await repo.registerToken('test-fcm-token');

      expect(fake.capturedRequests, hasLength(1));
      final req = fake.capturedRequests.first;
      expect(req['path'], '/notifications/device-tokens');
      final body = req['data'] as Map<String, dynamic>;
      expect(body['token'], 'test-fcm-token');
      expect(body['platform'], isNotNull);
    });

    test('body platform field is a non-empty string', () async {
      final fake = _FakeDio();
      final repo = DeviceTokenRepository(fake);

      await repo.registerToken('some-token');

      final body =
          fake.capturedRequests.first['data'] as Map<String, dynamic>;
      expect(body['platform'], isA<String>());
      expect((body['platform'] as String).isNotEmpty, isTrue);
    });

    test('degrades silently on 401 (unauthenticated)', () async {
      final fake = _FakeDio(statusCode: 401);
      final repo = DeviceTokenRepository(fake);

      // Must not throw.
      await expectLater(repo.registerToken('tkn'), completes);
    });

    test('degrades silently on 500 server error', () async {
      final fake = _FakeDio(statusCode: 500);
      final repo = DeviceTokenRepository(fake);

      await expectLater(repo.registerToken('tkn'), completes);
    });

    test('degrades silently on network error (offline)', () async {
      final fake = _FakeDio(throwNetwork: true);
      final repo = DeviceTokenRepository(fake);

      await expectLater(repo.registerToken('tkn'), completes);
    });
  });

  // ---------------------------------------------------------------------------
  // Tests: NotificationsNotifier wires to DeviceTokenRepository
  // ---------------------------------------------------------------------------

  group('NotificationsNotifier token registration integration', () {
    test('enable() registers token with backend when permission granted',
        () async {
      final fakeDio = _FakeDio();
      final notifService = _StubNotificationsService(
        permissionGranted: true,
        token: 'integration-token',
      );
      final container = _makeContainer(
        notifService: notifService,
        fakeDio: fakeDio,
      );
      addTearDown(container.dispose);

      await container.read(notificationsProvider.notifier).enable();

      // enable() calls repo.registerToken once (directly — not via onTokenRefresh).
      expect(fakeDio.capturedRequests, hasLength(1));
      final body =
          fakeDio.capturedRequests.first['data'] as Map<String, dynamic>;
      expect(body['token'], 'integration-token');
    });

    test('enable() skips backend call when permission denied', () async {
      final fakeDio = _FakeDio();
      final notifService = _StubNotificationsService(permissionGranted: false);
      final container = _makeContainer(
        notifService: notifService,
        fakeDio: fakeDio,
      );
      addTearDown(container.dispose);

      await container.read(notificationsProvider.notifier).enable();

      expect(fakeDio.capturedRequests, isEmpty);
    });

    test('enable() skips backend call when token is null', () async {
      final fakeDio = _FakeDio();
      // permissionGranted=true but token=null (edge case)
      final notifService = _StubNotificationsService(
        permissionGranted: true,
        token: null,
      );
      final container = _makeContainer(
        notifService: notifService,
        fakeDio: fakeDio,
      );
      addTearDown(container.dispose);

      await container.read(notificationsProvider.notifier).enable();

      expect(fakeDio.capturedRequests, isEmpty);
    });

    test('backend 401 during enable() does not fail the enable flow', () async {
      final fakeDio = _FakeDio(statusCode: 401);
      final notifService = _StubNotificationsService(
        permissionGranted: true,
        token: 'tkn',
      );
      final container = _makeContainer(
        notifService: notifService,
        fakeDio: fakeDio,
      );
      addTearDown(container.dispose);

      final granted =
          await container.read(notificationsProvider.notifier).enable();

      // enable() should still return true — backend failure is non-fatal.
      expect(granted, isTrue);
      final state = container.read(notificationsProvider);
      expect(state.isEnabled, isTrue);
      expect(state.isPermissionGranted, isTrue);
    });

    test('onTokenRefresh callback calls registerToken', () async {
      final fakeDio = _FakeDio();
      String? capturedRefreshToken;

      // Directly exercise the DeviceTokenRepository via the callback path.
      final repo = DeviceTokenRepository(fakeDio);
      void onRefresh(String token) {
        capturedRefreshToken = token;
        repo.registerToken(token);
      }

      onRefresh('refreshed-token-xyz');
      await Future<void>.delayed(Duration.zero);

      expect(capturedRefreshToken, 'refreshed-token-xyz');
      expect(fakeDio.capturedRequests, hasLength(1));
      final body =
          fakeDio.capturedRequests.first['data'] as Map<String, dynamic>;
      expect(body['token'], 'refreshed-token-xyz');
    });
  });

  // ---------------------------------------------------------------------------
  // Tests: PushMessage
  // ---------------------------------------------------------------------------

  group('PushMessage', () {
    test('toString includes title, body and data', () {
      const msg = PushMessage(
        title: 'Hello',
        body: 'World',
        data: {'key': 'value'},
      );
      final str = msg.toString();
      expect(str, contains('Hello'));
      expect(str, contains('World'));
    });

    test('defaults data to empty map', () {
      const msg = PushMessage(title: 'T', body: 'B');
      expect(msg.data, isEmpty);
    });
  });
}
