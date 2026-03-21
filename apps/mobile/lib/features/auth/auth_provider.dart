import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/core/network/api_client.dart';
import 'package:mobile/features/auth/user_model.dart';

sealed class AuthState {
  const AuthState();
}

class AuthLoading extends AuthState {
  const AuthLoading();
}

class AuthAuthenticated extends AuthState {
  final User user;
  const AuthAuthenticated(this.user);
}

class AuthUnauthenticated extends AuthState {
  const AuthUnauthenticated();
}

final authProvider =
    NotifierProvider<AuthNotifier, AuthState>(AuthNotifier.new);

class AuthNotifier extends Notifier<AuthState> {
  @override
  AuthState build() {
    _checkAuth();
    return const AuthLoading();
  }

  Future<void> _checkAuth() async {
    final storage = ref.read(tokenStorageProvider);
    final token = await storage.getAccessToken();
    if (token == null) {
      state = const AuthUnauthenticated();
      return;
    }

    try {
      final dio = ref.read(apiClientProvider);
      final response = await dio.get('/auth/me');
      final data = response.data['data'] as Map<String, dynamic>;
      state = AuthAuthenticated(User.fromJson(data));
    } catch (_) {
      state = const AuthUnauthenticated();
    }
  }

  Future<void> login({
    required String provider,
    required String code,
    required String redirectUri,
  }) async {
    state = const AuthLoading();

    try {
      final dio = ref.read(apiClientProvider);
      final response = await dio.post('/auth/token', data: {
        'provider': provider,
        'code': code,
        'redirect_uri': redirectUri,
      });

      final data = response.data['data'] as Map<String, dynamic>;
      final storage = ref.read(tokenStorageProvider);
      await storage.saveTokens(
        accessToken: data['access_token'] as String,
        refreshToken: data['refresh_token'] as String,
      );

      await _checkAuth();
    } catch (_) {
      state = const AuthUnauthenticated();
      rethrow;
    }
  }

  Future<void> logout() async {
    final storage = ref.read(tokenStorageProvider);
    final refreshToken = await storage.getRefreshToken();

    if (refreshToken != null) {
      try {
        final dio = ref.read(apiClientProvider);
        await dio.delete('/auth/logout', data: {
          'refresh_token': refreshToken,
        });
      } catch (_) {
        // Best-effort server-side logout
      }
    }

    await storage.clear();
    state = const AuthUnauthenticated();
  }
}
