// Locale resolution unit tests — no platform plugins required.
//
// Tests the localeResolutionCallback logic that is wired in app.dart and
// verifies that AppLocalizations.supportedLocales contains the expected
// locales (ko and en).

import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:mobile/l10n/app_localizations.dart';

// Mirrors the exact localeResolutionCallback defined in app.dart so we can
// test it in isolation without spinning up a full widget tree.
Locale? _resolveLocale(Locale? locale, Iterable<Locale> supportedLocales) {
  if (locale == null) return supportedLocales.first;
  for (final supported in supportedLocales) {
    if (supported.languageCode == locale.languageCode) return supported;
  }
  return supportedLocales.first;
}

void main() {
  final supported = AppLocalizations.supportedLocales;

  group('AppLocalizations.supportedLocales', () {
    test('contains Korean locale', () {
      expect(
        supported.any((l) => l.languageCode == 'ko'),
        isTrue,
        reason: 'ko must be a supported locale',
      );
    });

    test('contains English locale', () {
      expect(
        supported.any((l) => l.languageCode == 'en'),
        isTrue,
        reason: 'en must be a supported locale',
      );
    });

    test('has exactly 2 supported locales', () {
      expect(supported.length, 2);
    });
  });

  group('localeResolutionCallback', () {
    test('returns ko for a Korean device locale', () {
      final result = _resolveLocale(const Locale('ko'), supported);
      expect(result?.languageCode, 'ko');
    });

    test('returns en for an English device locale', () {
      final result = _resolveLocale(const Locale('en'), supported);
      expect(result?.languageCode, 'en');
    });

    test('falls back to first supported locale for unsupported locale', () {
      final result = _resolveLocale(const Locale('ja'), supported);
      expect(result, supported.first);
    });

    test('falls back to first supported locale when device locale is null', () {
      final result = _resolveLocale(null, supported);
      expect(result, supported.first);
    });

    test('matches by languageCode only (ignores country code)', () {
      final result = _resolveLocale(const Locale('ko', 'KR'), supported);
      expect(result?.languageCode, 'ko');
    });
  });
}
