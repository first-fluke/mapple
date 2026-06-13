import 'package:flutter/widgets.dart';
import 'package:forui/forui.dart';

import 'package:mobile/l10n/app_localizations.dart';

class StaleDataBanner extends StatelessWidget {
  final DateTime? lastSyncedAt;

  const StaleDataBanner({required this.lastSyncedAt, super.key});

  @override
  Widget build(BuildContext context) {
    final theme = context.theme;
    final l10n = AppLocalizations.of(context)!;

    final label = lastSyncedAt != null
        ? l10n.offlineWithCache(_formatTime(lastSyncedAt!, l10n))
        : l10n.offlineNoCache;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        color: theme.colorScheme.muted,
        border: Border(
          bottom: BorderSide(color: theme.colorScheme.border),
        ),
      ),
      child: Row(
        children: [
          FIcon(
            FAssets.icons.wifiOff,
            size: 14,
            color: theme.colorScheme.mutedForeground,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              label,
              style: theme.typography.sm.copyWith(
                color: theme.colorScheme.mutedForeground,
              ),
            ),
          ),
        ],
      ),
    );
  }

  String _formatTime(DateTime time, AppLocalizations l10n) {
    final now = DateTime.now();
    final diff = now.difference(time);

    if (diff.inMinutes < 1) return l10n.timeAgoJustNow;
    if (diff.inMinutes < 60) return l10n.timeAgoMinutes(diff.inMinutes);
    if (diff.inHours < 24) return l10n.timeAgoHours(diff.inHours);
    return l10n.timeAgoDays(diff.inDays);
  }
}
