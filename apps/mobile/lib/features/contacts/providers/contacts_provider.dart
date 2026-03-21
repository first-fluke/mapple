import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/core/api/dio_client.dart';
import 'package:mobile/features/contacts/models/contact.dart';
import 'package:mobile/features/contacts/services/contacts_api.dart';

final contactsApiProvider = Provider<ContactsApi>((ref) {
  return ContactsApi(ref.watch(dioProvider));
});

enum ContactSort {
  createdAtDesc('created_at_desc', '최신순'),
  createdAtAsc('created_at_asc', '오래된순'),
  nameAsc('name_asc', '이름 A-Z'),
  nameDesc('name_desc', '이름 Z-A');

  final String value;
  final String label;
  const ContactSort(this.value, this.label);
}

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

final contactsProvider =
    NotifierProvider<ContactsNotifier, ContactsState>(ContactsNotifier.new);

class ContactsNotifier extends Notifier<ContactsState> {
  @override
  ContactsState build() {
    _fetchContacts();
    return const ContactsState(isLoading: true);
  }

  Future<void> _fetchContacts() async {
    final api = ref.read(contactsApiProvider);
    try {
      final result = await api.list(
        search: state.searchQuery.isEmpty ? null : state.searchQuery,
        sort: state.sort.value,
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
}
