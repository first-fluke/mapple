import 'package:flutter/widgets.dart';
import 'package:forui/forui.dart';

import 'package:mobile/l10n/app_localizations.dart';

class EmptyContacts extends StatelessWidget {
  final bool isSearchResult;

  const EmptyContacts({this.isSearchResult = false, super.key});

  @override
  Widget build(BuildContext context) {
    final theme = context.theme;
    final l10n = AppLocalizations.of(context)!;

    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            FIcon(
              FAssets.icons.users,
              size: 48,
              color: theme.colorScheme.mutedForeground,
            ),
            const SizedBox(height: 16),
            Text(
              isSearchResult ? l10n.emptySearchTitle : l10n.emptyContactsTitle,
              style: theme.typography.lg.copyWith(
                color: theme.colorScheme.foreground,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              isSearchResult
                  ? l10n.emptySearchSubtitle
                  : l10n.emptyContactsSubtitle,
              style: theme.typography.sm.copyWith(
                color: theme.colorScheme.mutedForeground,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
