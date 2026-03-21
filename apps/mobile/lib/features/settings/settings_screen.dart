import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:forui/forui.dart';

import 'package:mobile/features/auth/auth_provider.dart';
import 'package:mobile/theme/theme_provider.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeMode = ref.watch(themeModeProvider);
    final auth = ref.watch(authProvider);
    final theme = context.theme;

    return ListView(
      padding: const EdgeInsets.symmetric(vertical: 16),
      children: [
        if (auth is AuthAuthenticated) ...[
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Text(
              'Account',
              style: theme.typography.lg.copyWith(
                color: theme.colorScheme.foreground,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          FTile(
            prefixIcon: FIcon(FAssets.icons.user),
            title: Text(auth.user.name ?? auth.user.email),
            subtitle: Text(auth.user.email),
          ),
        ],
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Text(
            'Appearance',
            style: theme.typography.lg.copyWith(
              color: theme.colorScheme.foreground,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        FTile(
          prefixIcon: FIcon(FAssets.icons.sun),
          title: const Text('Theme'),
          suffixIcon: FIcon(
            themeMode == ThemeMode.dark
                ? FAssets.icons.moon
                : FAssets.icons.sun,
          ),
          onPress: () => ref.read(themeModeProvider.notifier).toggle(),
        ),
        const SizedBox(height: 16),
        FTile(
          prefixIcon: FIcon(FAssets.icons.logOut),
          title: const Text('Sign Out'),
          onPress: () => ref.read(authProvider.notifier).logout(),
        ),
      ],
    );
  }
}
