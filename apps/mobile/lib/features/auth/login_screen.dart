import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:forui/forui.dart';

import 'package:mobile/core/config.dart';
import 'package:mobile/features/auth/auth_provider.dart';
import 'package:mobile/features/auth/oauth_webview_screen.dart';

class LoginScreen extends ConsumerWidget {
  const LoginScreen({super.key});

  Future<void> _signIn(
    BuildContext context,
    WidgetRef ref,
    String provider,
  ) async {
    final code = await Navigator.of(context).push<String>(
      MaterialPageRoute(
        builder: (_) => OAuthWebViewScreen(provider: provider),
      ),
    );

    if (code == null || !context.mounted) return;

    try {
      await ref.read(authProvider.notifier).login(
            provider: provider,
            code: code,
            redirectUri: AppConfig.authCallbackUrl,
          );
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Login failed: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authProvider);
    final theme = context.theme;

    if (auth is AuthLoading) {
      return const FScaffold(
        content: Center(child: CircularProgressIndicator()),
      );
    }

    return FScaffold(
      content: Center(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              FIcon(FAssets.icons.globe, size: 64),
              const SizedBox(height: 16),
              Text(
                'Globe CRM',
                style: theme.typography.xl3.copyWith(
                  color: theme.colorScheme.foreground,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Sign in to continue',
                style: theme.typography.base.copyWith(
                  color: theme.colorScheme.mutedForeground,
                ),
              ),
              const SizedBox(height: 48),
              SizedBox(
                width: double.infinity,
                child: FButton(
                  onPress: () => _signIn(context, ref, 'google'),
                  label: const Text('Sign in with Google'),
                ),
              ),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: FButton(
                  style: FButtonStyle.outline,
                  onPress: () => _signIn(context, ref, 'github'),
                  label: const Text('Sign in with GitHub'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
