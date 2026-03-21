import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:forui/forui.dart';

import 'package:mobile/features/contacts/contacts_provider.dart';

class ContactsScreen extends ConsumerWidget {
  const ContactsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = context.theme;
    final contacts = ref.watch(contactsProvider);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: Semantics(
            header: true,
            child: Text(
              'Contacts',
              style: theme.typography.xl2.copyWith(
                color: theme.colorScheme.foreground,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
        Expanded(
          child: ListView.builder(
            itemCount: contacts.length,
            itemBuilder: (context, index) {
              final contact = contacts[index];
              return Semantics(
                label: contact.name,
                hint: [
                  if (contact.email != null) contact.email!,
                  if (contact.phone != null) contact.phone!,
                ].join(', '),
                child: FTile(
                  prefixIcon: FIcon(FAssets.icons.user),
                  title: Text(contact.name),
                  subtitle: Text(contact.email ?? contact.phone ?? ''),
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}
