import 'package:flutter/material.dart';
import 'package:flutter_inappwebview/flutter_inappwebview.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/theme/theme_provider.dart';

class JsBridgeService {
  static void registerHandlers(
    InAppWebViewController controller,
    WidgetRef ref,
  ) {
    controller.addJavaScriptHandler(
      handlerName: 'SET_THEME',
      callback: (args) {
        if (args.isEmpty) return;

        final theme = args.first as String;
        final mode = switch (theme) {
          'dark' => ThemeMode.dark,
          'light' => ThemeMode.light,
          _ => ThemeMode.system,
        };

        ref.read(themeModeProvider.notifier).setThemeMode(mode);
      },
    );
  }
}
