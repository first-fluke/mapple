import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:forui/forui.dart';

import 'package:mobile/theme/theme_provider.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeMode = ref.watch(themeModeProvider);
    final theme = context.theme;

    return ListView(
      padding: const EdgeInsets.symmetric(vertical: 16),
      children: [
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
      ],
    );
  }
}
