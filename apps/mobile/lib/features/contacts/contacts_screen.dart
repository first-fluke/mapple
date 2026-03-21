import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:forui/forui.dart';
import 'package:go_router/go_router.dart';

import 'package:mobile/features/contacts/models/contact.dart';
import 'package:mobile/features/contacts/providers/contacts_provider.dart';

class ContactsScreen extends ConsumerWidget {
  const ContactsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final contacts = ref.watch(contactsProvider);
    final theme = context.theme;

    return Stack(
      children: [
        if (contacts.isEmpty)
          Center(
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
                  'No contacts yet',
                  style: theme.typography.lg.copyWith(
                    color: theme.colorScheme.mutedForeground,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Tap + to add your first contact',
                  style: theme.typography.sm.copyWith(
                    color: theme.colorScheme.mutedForeground,
                  ),
                ),
              ],
            ),
          )
        else
          ListView.builder(
            padding: const EdgeInsets.only(top: 8, bottom: 80),
            itemCount: contacts.length,
            itemBuilder: (context, index) {
              final contact = contacts[index];
              return _ContactListItem(contact: contact);
            },
          ),
        Positioned(
          right: 16,
          bottom: 16,
          child: FloatingActionButton(
            onPressed: () => context.go('/contacts/add'),
            backgroundColor: theme.colorScheme.primary,
            foregroundColor: theme.colorScheme.primaryForeground,
            child: const Icon(Icons.add),
          ),
        ),
      ],
    );
  }
}

class _ContactListItem extends StatelessWidget {
  final Contact contact;

  const _ContactListItem({required this.contact});

  @override
  Widget build(BuildContext context) {
    final theme = context.theme;

    return FTile(
      prefixIcon: CircleAvatar(
        radius: 20,
        backgroundColor: theme.colorScheme.secondary,
        child: Text(
          contact.initials,
          style: theme.typography.sm.copyWith(
            color: theme.colorScheme.secondaryForeground,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
      title: Text(contact.name),
      subtitle: Text(
        [contact.jobTitle, contact.company]
            .where((s) => s != null && s.isNotEmpty)
            .join(' · '),
      ),
      suffixIcon: FIcon(
        FAssets.icons.chevronRight,
        color: theme.colorScheme.mutedForeground,
      ),
      onPress: () => context.go('/contacts/${contact.id}'),
    );
  }
}
