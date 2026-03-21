import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/connectivity/connectivity_provider.dart';
import 'package:mobile/database/database.dart';
import 'package:mobile/features/contacts/contacts_repository.dart';

final contactsStreamProvider = StreamProvider<List<CachedContact>>((ref) {
  final repo = ref.watch(contactsRepositoryProvider);
  final isOnline = ref.watch(isOnlineProvider);

  if (isOnline) {
    repo.syncContacts().ignore();
  }

  return repo.watchContacts();
});

final lastSyncTimeProvider = FutureProvider<DateTime?>((ref) {
  final repo = ref.watch(contactsRepositoryProvider);
  return repo.getLastSyncTime();
});
