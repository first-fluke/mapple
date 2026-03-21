import 'package:flutter/widgets.dart';
import 'package:forui/forui.dart';

class StaleDataBanner extends StatelessWidget {
  final DateTime? lastSyncedAt;

  const StaleDataBanner({required this.lastSyncedAt, super.key});

  @override
  Widget build(BuildContext context) {
    final theme = context.theme;

    final label = lastSyncedAt != null
        ? 'Offline — showing cached data from ${_formatTime(lastSyncedAt!)}'
        : 'Offline — no cached data available';

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

  String _formatTime(DateTime time) {
    final now = DateTime.now();
    final diff = now.difference(time);

    if (diff.inMinutes < 1) return 'just now';
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    return '${diff.inDays}d ago';
  }
}
