import 'package:flutter/material.dart';
import 'package:forui/forui.dart';

import 'package:mobile/features/contacts/models/contact.dart';

class ProfileHeader extends StatelessWidget {
  final Contact contact;

  const ProfileHeader({required this.contact, super.key});

  @override
  Widget build(BuildContext context) {
    final theme = context.theme;

    return Column(
      children: [
        CircleAvatar(
          radius: 40,
          backgroundColor: theme.colorScheme.secondary,
          child: Text(
            contact.initials,
            style: theme.typography.xl2.copyWith(
              color: theme.colorScheme.secondaryForeground,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        const SizedBox(height: 12),
        if (contact.jobTitle != null || contact.company != null)
          Text(
            [contact.jobTitle, contact.company]
                .where((s) => s != null && s.isNotEmpty)
                .join(' at '),
            style: theme.typography.sm.copyWith(
              color: theme.colorScheme.mutedForeground,
            ),
            textAlign: TextAlign.center,
          ),
        const SizedBox(height: 16),
        // Contact info row
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (contact.email != null) ...[
              _InfoChip(
                icon: FAssets.icons.mail,
                label: contact.email!,
                theme: theme,
              ),
              const SizedBox(width: 12),
            ],
            if (contact.phone != null)
              _InfoChip(
                icon: FAssets.icons.phone,
                label: contact.phone!,
                theme: theme,
              ),
          ],
        ),
        if (contact.locationName != null) ...[
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              FIcon(
                FAssets.icons.mapPin,
                size: 14,
                color: theme.colorScheme.mutedForeground,
              ),
              const SizedBox(width: 4),
              Text(
                contact.locationName!,
                style: theme.typography.xs.copyWith(
                  color: theme.colorScheme.mutedForeground,
                ),
              ),
            ],
          ),
        ],
        if (contact.memo != null && contact.memo!.isNotEmpty) ...[
          const SizedBox(height: 12),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: theme.colorScheme.secondary,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              contact.memo!,
              style: theme.typography.sm.copyWith(
                color: theme.colorScheme.secondaryForeground,
              ),
            ),
          ),
        ],
      ],
    );
  }
}

class _InfoChip extends StatelessWidget {
  final SvgAsset icon;
  final String label;
  final FThemeData theme;

  const _InfoChip({
    required this.icon,
    required this.label,
    required this.theme,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        FIcon(icon, size: 14, color: theme.colorScheme.mutedForeground),
        const SizedBox(width: 4),
        Flexible(
          child: Text(
            label,
            style: theme.typography.xs.copyWith(
              color: theme.colorScheme.mutedForeground,
            ),
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ],
    );
  }
}
