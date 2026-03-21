import 'package:flutter/widgets.dart';
import 'package:forui/forui.dart';

import 'package:mobile/features/contacts/models/contact.dart';

class ContactTile extends StatelessWidget {
  final Contact contact;
  final VoidCallback? onTap;

  const ContactTile({required this.contact, this.onTap, super.key});

  @override
  Widget build(BuildContext context) {
    final theme = context.theme;
    final initials = contact.name.isNotEmpty
        ? contact.name.substring(0, 1).toUpperCase()
        : '?';

    return FTile(
      prefixIcon: Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          color: theme.colorScheme.muted,
          shape: BoxShape.circle,
        ),
        alignment: Alignment.center,
        child: Text(
          initials,
          style: theme.typography.base.copyWith(
            color: theme.colorScheme.mutedForeground,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      title: Text(
        contact.name,
        style: theme.typography.sm.copyWith(
          color: theme.colorScheme.foreground,
          fontWeight: FontWeight.w500,
        ),
      ),
      subtitle: Text(
        contact.email ?? contact.phone ?? '',
        style: theme.typography.xs.copyWith(
          color: theme.colorScheme.mutedForeground,
        ),
      ),
      onPress: onTap,
    );
  }
}
