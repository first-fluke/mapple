import 'dart:io';

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

/// Repository responsible for registering and refreshing FCM device tokens
/// with the backend API.
///
/// Endpoint: `POST /notifications/device-tokens`
/// Body: `{ "token": "<fcm_token>", "platform": "ios" | "android" }`
class DeviceTokenRepository {
  final Dio _dio;

  DeviceTokenRepository(this._dio);

  /// Registers [token] with the backend.
  ///
  /// Fails silently when the user is unauthenticated (401) or the device is
  /// offline so that a missing token never crashes the app.
  Future<void> registerToken(String token) async {
    final platform = _resolvePlatform();
    try {
      await _dio.post<void>(
        '/notifications/device-tokens',
        data: {'token': token, 'platform': platform},
      );
      debugPrint('[DeviceTokenRepository] token registered (platform=$platform)');
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        // User is not authenticated yet — the token will be re-registered
        // once auth succeeds and onTokenRefresh fires again.
        debugPrint('[DeviceTokenRepository] unauthenticated — skipping token registration');
        return;
      }
      // Network errors / timeouts — degrade gracefully.
      debugPrint('[DeviceTokenRepository] failed to register token: $e');
    } catch (e) {
      debugPrint('[DeviceTokenRepository] unexpected error: $e');
    }
  }

  String _resolvePlatform() {
    if (kIsWeb) return 'web';
    if (Platform.isIOS) return 'ios';
    if (Platform.isAndroid) return 'android';
    return 'unknown';
  }
}
