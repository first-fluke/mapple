import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:forui/forui.dart';

import 'package:mobile/l10n/app_localizations.dart';
import 'package:mobile/router/router.dart';
import 'package:mobile/theme/theme_provider.dart';

class GlobeApp extends ConsumerWidget {
  const GlobeApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeMode = ref.watch(themeModeProvider);
    final router = ref.watch(routerProvider);

    final brightness = switch (themeMode) {
      ThemeMode.dark => Brightness.dark,
      ThemeMode.light => Brightness.light,
      ThemeMode.system =>
        WidgetsBinding.instance.platformDispatcher.platformBrightness,
    };

    final foruiTheme = brightness == Brightness.dark
        ? FThemes.zinc.dark
        : FThemes.zinc.light;

    return FTheme(
      data: foruiTheme,
      child: MaterialApp.router(
        title: 'Mapple',
        debugShowCheckedModeBanner: false,
        themeMode: themeMode,
        localizationsDelegates: const [
          AppLocalizations.delegate,
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        supportedLocales: AppLocalizations.supportedLocales,
        localeResolutionCallback: (locale, supportedLocales) {
          if (locale == null) return supportedLocales.first;
          for (final supported in supportedLocales) {
            if (supported.languageCode == locale.languageCode) return supported;
          }
          return supportedLocales.first;
        },
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(
            seedColor: const Color(0xFF292524),
            brightness: Brightness.light,
            surface: const Color(0xFFFFFBF5),
          ),
          useMaterial3: true,
        ),
        darkTheme: ThemeData(
          colorScheme: ColorScheme.fromSeed(
            seedColor: const Color(0xFF292524),
            brightness: Brightness.dark,
            surface: const Color(0xFF1C1917),
          ),
          useMaterial3: true,
        ),
        routerConfig: router,
      ),
    );
  }
}
