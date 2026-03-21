import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/core/config.dart';
import 'package:mobile/core/storage/token_storage.dart';

final tokenStorageProvider = Provider<TokenStorage>((ref) => TokenStorage());

final apiClientProvider = Provider<Dio>((ref) {
  final storage = ref.read(tokenStorageProvider);
  final dio = Dio(BaseOptions(baseUrl: AppConfig.apiBaseUrl));
  dio.interceptors.add(AuthInterceptor(storage: storage));
  return dio;
});

class AuthInterceptor extends QueuedInterceptorsWrapper {
  final TokenStorage _storage;

  AuthInterceptor({required TokenStorage storage}) : _storage = storage;

  @override
  void onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final token = await _storage.getAccessToken();
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode != 401) {
      return handler.next(err);
    }

    final refreshToken = await _storage.getRefreshToken();
    if (refreshToken == null) {
      return handler.next(err);
    }

    try {
      final refreshDio = Dio(BaseOptions(baseUrl: AppConfig.apiBaseUrl));
      final response = await refreshDio.post(
        '/auth/refresh',
        data: {'refresh_token': refreshToken},
      );

      final data = response.data['data'] as Map<String, dynamic>;
      await _storage.saveTokens(
        accessToken: data['access_token'] as String,
        refreshToken: data['refresh_token'] as String,
      );

      final options = err.requestOptions;
      options.headers['Authorization'] = 'Bearer ${data['access_token']}';
      final retryResponse = await refreshDio.fetch(options);
      handler.resolve(retryResponse);
    } catch (_) {
      await _storage.clear();
      handler.next(err);
    }
  }
}
import 'package:mobile/core/network/jwt_interceptor.dart';
const _baseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://10.0.2.2:3000',
);
  final refreshDio = Dio(BaseOptions(
    baseUrl: _baseUrl,
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 10),
    headers: {'Content-Type': 'application/json'},
  ));
  final dio = Dio(BaseOptions(
  dio.interceptors.add(
    JwtInterceptor(ref: ref, refreshDio: refreshDio),
  );
