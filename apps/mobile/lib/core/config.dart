class AppConfig {
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000',
  );

  static const String googleClientId = String.fromEnvironment(
    'GOOGLE_CLIENT_ID',
    defaultValue: '',
  );

  static const String githubClientId = String.fromEnvironment(
    'GITHUB_CLIENT_ID',
    defaultValue: '',
  );

  static String get authCallbackUrl => '$apiBaseUrl/auth/callback';
}
