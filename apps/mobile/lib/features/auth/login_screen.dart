import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:forui/forui.dart';

import 'package:mobile/core/config.dart';
import 'package:mobile/features/auth/auth_provider.dart';
import 'package:mobile/features/auth/oauth_webview_screen.dart';
import 'package:mobile/l10n/app_localizations.dart';

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
        final l10n = AppLocalizations.of(context)!;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.loginFailed(e.toString()))),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authProvider);
    final theme = context.theme;
    final l10n = AppLocalizations.of(context)!;

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
                l10n.appTitle,
                style: theme.typography.xl3.copyWith(
                  color: theme.colorScheme.foreground,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                l10n.loginSignInSubtitle,
                style: theme.typography.base.copyWith(
                  color: theme.colorScheme.mutedForeground,
                ),
              ),
              const SizedBox(height: 48),
              SizedBox(
                width: double.infinity,
                child: FButton(
                  onPress: () => _signIn(context, ref, 'google'),
                  label: Text(l10n.loginSignInWithGoogle),
                ),
              ),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: FButton(
                  style: FButtonStyle.outline,
                  onPress: () => _signIn(context, ref, 'github'),
                  label: Text(l10n.loginSignInWithGitHub),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
