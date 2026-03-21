import 'package:flutter/material.dart';
import 'package:forui/forui.dart';

void showProfileBottomSheet({
  required BuildContext context,
  required String nodeId,
  required String name,
  String? group,
  String? avatarUrl,
}) {
  final theme = context.theme;

  showModalBottomSheet(
    context: context,
    useRootNavigator: true,
    backgroundColor: Colors.transparent,
    builder: (_) {
      return Container(
        decoration: BoxDecoration(
          color: theme.colorScheme.background,
          borderRadius:
              const BorderRadius.vertical(top: Radius.circular(16)),
        ),
        padding: const EdgeInsets.fromLTRB(24, 12, 24, 32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Drag handle
            Container(
              width: 36,
              height: 4,
              margin: const EdgeInsets.only(bottom: 20),
              decoration: BoxDecoration(
                color: theme.colorScheme.border,
                borderRadius: BorderRadius.circular(2),
              ),
            ),

            // Avatar
            CircleAvatar(
              radius: 32,
              backgroundColor: theme.colorScheme.muted,
              backgroundImage:
                  avatarUrl != null ? NetworkImage(avatarUrl) : null,
              child: avatarUrl == null
                  ? Text(
                      name.isNotEmpty ? name[0].toUpperCase() : '?',
                      style: theme.typography.xl2.copyWith(
                        color: theme.colorScheme.mutedForeground,
                        fontWeight: FontWeight.bold,
                      ),
                    )
                  : null,
            ),
            const SizedBox(height: 12),

            // Name
            Text(
              name,
              style: theme.typography.xl.copyWith(
                color: theme.colorScheme.foreground,
                fontWeight: FontWeight.bold,
              ),
            ),

            // Group
            if (group != null) ...[
              const SizedBox(height: 4),
              Text(
                group,
                style: theme.typography.sm.copyWith(
                  color: theme.colorScheme.mutedForeground,
                ),
              ),
            ],

            const SizedBox(height: 16),
          ],
        ),
      );
    },
  );
}
