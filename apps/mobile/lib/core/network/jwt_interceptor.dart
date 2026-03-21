import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/core/network/auth_token_provider.dart';

class JwtInterceptor extends QueuedInterceptor {
  final Ref _ref;
  final Dio _refreshDio;

  JwtInterceptor({required Ref ref, required Dio refreshDio})
      : _ref = ref,
        _refreshDio = refreshDio;

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    final tokens = _ref.read(authTokenProvider);
    if (tokens != null) {
      options.headers['Authorization'] = 'Bearer ${tokens.accessToken}';
    }
    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode != 401) {
      return handler.next(err);
    }

    final tokens = _ref.read(authTokenProvider);
    if (tokens == null) {
      return handler.next(err);
    }

    try {
      final response = await _refreshDio.post(
        '/auth/refresh',
        data: {'refresh_token': tokens.refreshToken},
      );

      final data = response.data['data'] as Map<String, dynamic>;
      final newAccessToken = data['access_token'] as String;
      final expiresIn = data['expires_in'] as int;

      _ref
          .read(authTokenProvider.notifier)
          .updateAccessToken(newAccessToken, expiresIn);

      final retryOptions = err.requestOptions;
      retryOptions.headers['Authorization'] = 'Bearer $newAccessToken';

      final retryResponse = await _refreshDio.fetch(retryOptions);
      handler.resolve(retryResponse);
    } on DioException {
      _ref.read(authTokenProvider.notifier).clear();
      handler.next(err);
    }
  }
}
