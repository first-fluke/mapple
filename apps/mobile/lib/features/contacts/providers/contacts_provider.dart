import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/core/api/dio_client.dart';
import 'package:mobile/features/contacts/models/contact.dart';
import 'package:mobile/features/contacts/services/contacts_api.dart';

// ---------------------------------------------------------------------------
// API provider
// ---------------------------------------------------------------------------

final contactsApiProvider = Provider<ContactsApi>((ref) {
  return ContactsApi(ref.watch(dioProvider));
});

// ---------------------------------------------------------------------------
// Sort enum
// ---------------------------------------------------------------------------

enum ContactSort {
  createdAtDesc('created_at_desc'),
  createdAtAsc('created_at_asc'),
  nameAsc('name_asc'),
  nameDesc('name_desc');

  final String value;

  const ContactSort(this.value);
}

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

class ContactsState {
  final List<Contact> contacts;
  final bool isLoading;
  final bool isLoadingMore;
  final String? nextCursor;
  final bool hasMore;
  final String searchQuery;
  final ContactSort sort;
  final Object? error;

  const ContactsState({
    this.contacts = const [],
    this.isLoading = false,
    this.isLoadingMore = false,
    this.nextCursor,
    this.hasMore = true,
    this.searchQuery = '',
    this.sort = ContactSort.createdAtDesc,
    this.error,
  });

  ContactsState copyWith({
    List<Contact>? contacts,
    bool? isLoading,
    bool? isLoadingMore,
    String? Function()? nextCursor,
    bool? hasMore,
    String? searchQuery,
    ContactSort? sort,
    Object? Function()? error,
  }) {
    return ContactsState(
      contacts: contacts ?? this.contacts,
      isLoading: isLoading ?? this.isLoading,
      isLoadingMore: isLoadingMore ?? this.isLoadingMore,
      nextCursor: nextCursor != null ? nextCursor() : this.nextCursor,
      hasMore: hasMore ?? this.hasMore,
      searchQuery: searchQuery ?? this.searchQuery,
      sort: sort ?? this.sort,
      error: error != null ? error() : this.error,
    );
  }
}

// ---------------------------------------------------------------------------
// Notifier
// ---------------------------------------------------------------------------

final contactsProvider =
    NotifierProvider<ContactsNotifier, ContactsState>(ContactsNotifier.new);

class ContactsNotifier extends Notifier<ContactsState> {
  @override
  ContactsState build() {
    // Defer so state is initialized before the async method reads it.
    Future.microtask(_fetchContacts);
    return const ContactsState(isLoading: true);
  }

  Future<void> _fetchContacts() async {
    final api = ref.read(contactsApiProvider);
    // Capture state fields before the async gap.
    final query = state.searchQuery;
    final sort = state.sort;
    try {
      final result = await api.list(
        search: query.isEmpty ? null : query,
        sort: sort.value,
      );
      state = state.copyWith(
        contacts: result.items,
        isLoading: false,
        nextCursor: () => result.nextCursor,
        hasMore: result.hasMore,
        error: () => null,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: () => e);
    }
  }

  Future<void> loadMore() async {
    if (state.isLoadingMore || !state.hasMore || state.nextCursor == null) {
      return;
    }
    state = state.copyWith(isLoadingMore: true);
    final api = ref.read(contactsApiProvider);
    try {
      final result = await api.list(
        cursor: state.nextCursor,
        search: state.searchQuery.isEmpty ? null : state.searchQuery,
        sort: state.sort.value,
      );
      state = state.copyWith(
        contacts: [...state.contacts, ...result.items],
        isLoadingMore: false,
        nextCursor: () => result.nextCursor,
        hasMore: result.hasMore,
        error: () => null,
      );
    } catch (e) {
      state = state.copyWith(isLoadingMore: false, error: () => e);
    }
  }

  Future<void> refresh() async {
    state = state.copyWith(
      isLoading: true,
      contacts: [],
      nextCursor: () => null,
      hasMore: true,
      error: () => null,
    );
    await _fetchContacts();
  }

  Future<void> search(String query) async {
    state = state.copyWith(
      searchQuery: query,
      isLoading: true,
      contacts: [],
      nextCursor: () => null,
      hasMore: true,
    );
    await _fetchContacts();
  }

  Future<void> setSort(ContactSort sort) async {
    state = state.copyWith(
      sort: sort,
      isLoading: true,
      contacts: [],
      nextCursor: () => null,
      hasMore: true,
    );
    await _fetchContacts();
  }

  /// Create a contact via the API and prepend it to the local list.
  Future<Contact> createContact(Map<String, dynamic> payload) async {
    final api = ref.read(contactsApiProvider);
    final created = await api.create(payload);
    state = state.copyWith(contacts: [created, ...state.contacts]);
    return created;
  }

  /// Update a contact via the API and replace it in the local list.
  Future<Contact> updateContact(
      String id, Map<String, dynamic> payload) async {
    final api = ref.read(contactsApiProvider);
    final updated = await api.update(id, payload);
    state = state.copyWith(
      contacts: [
        for (final c in state.contacts)
          if (c.id == updated.id) updated else c,
      ],
    );
    return updated;
  }

  /// Soft-delete a contact via the API and remove it from the local list.
  Future<void> deleteContact(String id) async {
    final api = ref.read(contactsApiProvider);
    await api.delete(id);
    state =
        state.copyWith(contacts: state.contacts.where((c) => c.id != id).toList());
  }
}

// ---------------------------------------------------------------------------
// Convenience family provider
// ---------------------------------------------------------------------------

final contactByIdProvider = Provider.family<Contact?, String>((ref, id) {
  final contacts = ref.watch(contactsProvider).contacts;
  return contacts.where((c) => c.id == id).firstOrNull;
});
