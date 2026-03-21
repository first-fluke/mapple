import 'package:flutter_riverpod/flutter_riverpod.dart';

class AuthTokens {
  final String accessToken;
  final String refreshToken;
  final int expiresIn;

  const AuthTokens({
    required this.accessToken,
    required this.refreshToken,
    required this.expiresIn,
  });

  AuthTokens copyWith({
    String? accessToken,
    String? refreshToken,
    int? expiresIn,
  }) {
    return AuthTokens(
      accessToken: accessToken ?? this.accessToken,
      refreshToken: refreshToken ?? this.refreshToken,
      expiresIn: expiresIn ?? this.expiresIn,
    );
  }
}

final authTokenProvider =
    NotifierProvider<AuthTokenNotifier, AuthTokens?>(AuthTokenNotifier.new);

class AuthTokenNotifier extends Notifier<AuthTokens?> {
  @override
  AuthTokens? build() => null;

  void setTokens(AuthTokens tokens) {
    state = tokens;
  }

  void updateAccessToken(String accessToken, int expiresIn) {
    if (state != null) {
      state = state!.copyWith(accessToken: accessToken, expiresIn: expiresIn);
    }
  }

  void clear() {
    state = null;
  }
}
