import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:forui/forui.dart';

import 'package:mobile/connectivity/connectivity_provider.dart';
import 'package:mobile/features/contacts/contacts_provider.dart';
import 'package:mobile/widgets/stale_data_banner.dart';

class ContactsScreen extends ConsumerWidget {
  const ContactsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = context.theme;
    final isOnline = ref.watch(isOnlineProvider);
    final contactsAsync = ref.watch(contactsStreamProvider);
    final lastSync = ref.watch(lastSyncTimeProvider);

    return Column(
      children: [
        if (!isOnline)
          StaleDataBanner(
            lastSyncedAt: lastSync.value,
          ),
        Expanded(
          child: contactsAsync.when(
            data: (contacts) {
              if (contacts.isEmpty) {
                return Center(
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
                        isOnline
                            ? 'No contacts yet'
                            : 'No cached contacts',
                        style: theme.typography.lg.copyWith(
                          color: theme.colorScheme.mutedForeground,
                        ),
                      ),
                    ],
                  ),
                );
              }

              return ListView.builder(
                itemCount: contacts.length,
                itemBuilder: (context, index) {
                  final contact = contacts[index];
                  return FTile(
                    prefixIcon: FIcon(FAssets.icons.user),
                    title: Text(contact.name),
                    subtitle: contact.email != null
                        ? Text(contact.email!)
                        : null,
                    details: contact.phone != null
                        ? Text(contact.phone!)
                        : null,
                  );
                },
              );
            },
            loading: () => Center(
              child: FProgress(value: 0),
            ),
            error: (error, _) => Center(
              child: Text(
                'Failed to load contacts',
                style: theme.typography.base.copyWith(
                  color: theme.colorScheme.destructive,
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}
