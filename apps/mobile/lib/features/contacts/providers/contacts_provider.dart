import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/features/contacts/models/contact.dart';

final contactsProvider =
    NotifierProvider<ContactsNotifier, List<Contact>>(ContactsNotifier.new);

class ContactsNotifier extends Notifier<List<Contact>> {
  @override
  List<Contact> build() => _sampleContacts;

  void addContact(Contact contact) {
    state = [...state, contact];
  }

  void removeContact(String id) {
    state = state.where((c) => c.id != id).toList();
  }

  void updateContact(Contact contact) {
    state = [
      for (final c in state)
        if (c.id == contact.id) contact else c,
    ];
  }

  Contact? getById(String id) {
    return state.where((c) => c.id == id).firstOrNull;
  }
}

final contactByIdProvider = Provider.family<Contact?, String>((ref, id) {
  final contacts = ref.watch(contactsProvider);
  return contacts.where((c) => c.id == id).firstOrNull;
});

// Sample data for development
final _sampleContacts = [
  Contact(
    id: '1',
    name: 'Alice Johnson',
    email: 'alice@example.com',
    phone: '+1 555-0101',
    company: 'Acme Corp',
    jobTitle: 'Product Manager',
    socialLinks: [
      const SocialLink(
        platform: SocialPlatform.linkedin,
        url: 'https://linkedin.com/in/alicejohnson',
      ),
      const SocialLink(
        platform: SocialPlatform.twitter,
        url: 'https://twitter.com/alicej',
      ),
    ],
    tags: ['client', 'tech', 'priority'],
    timeline: [
      TimelineEvent(
        id: 't1',
        title: 'Initial meeting',
        description: 'Discussed product roadmap',
        date: DateTime(2026, 3, 10),
        type: TimelineEventType.meeting,
      ),
      TimelineEvent(
        id: 't2',
        title: 'Follow-up call',
        date: DateTime(2026, 3, 15),
        type: TimelineEventType.call,
      ),
    ],
    meetings: [
      Meeting(
        id: 'm1',
        title: 'Q1 Review',
        description: 'Quarterly business review',
        date: DateTime(2026, 3, 20),
        location: 'Seoul Office',
      ),
    ],
    latitude: 37.5665,
    longitude: 126.9780,
    locationName: 'Seoul, South Korea',
    createdAt: DateTime(2026, 1, 15),
    updatedAt: DateTime(2026, 3, 15),
  ),
  Contact(
    id: '2',
    name: 'Bob Kim',
    email: 'bob.kim@example.com',
    phone: '+82 10-1234-5678',
    company: 'TechStart',
    jobTitle: 'CTO',
    socialLinks: [
      const SocialLink(
        platform: SocialPlatform.github,
        url: 'https://github.com/bobkim',
      ),
    ],
    tags: ['partner', 'engineering'],
    timeline: [
      TimelineEvent(
        id: 't3',
        title: 'Partnership discussion',
        date: DateTime(2026, 3, 5),
        type: TimelineEventType.meeting,
      ),
    ],
    meetings: [],
    latitude: 37.4979,
    longitude: 127.0276,
    locationName: 'Gangnam, Seoul',
    createdAt: DateTime(2026, 2, 1),
    updatedAt: DateTime(2026, 3, 5),
  ),
  Contact(
    id: '3',
    name: 'Carol Park',
    email: 'carol@design.co',
    company: 'DesignLab',
    jobTitle: 'Lead Designer',
    socialLinks: [
      const SocialLink(
        platform: SocialPlatform.instagram,
        url: 'https://instagram.com/carolpark',
      ),
    ],
    tags: ['freelancer', 'design'],
    timeline: [],
    meetings: [],
    createdAt: DateTime(2026, 3, 1),
    updatedAt: DateTime(2026, 3, 1),
  ),
];
import 'package:mobile/core/api/dio_client.dart';
import 'package:mobile/features/contacts/services/contacts_api.dart';
final contactsApiProvider = Provider<ContactsApi>((ref) {
  return ContactsApi(ref.watch(dioProvider));
enum ContactSort {
  createdAtDesc('created_at_desc', '최신순'),
  createdAtAsc('created_at_asc', '오래된순'),
  nameAsc('name_asc', '이름 A-Z'),
  nameDesc('name_desc', '이름 Z-A');
  final String value;
  final String label;
  const ContactSort(this.value, this.label);
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
    NotifierProvider<ContactsNotifier, ContactsState>(ContactsNotifier.new);
class ContactsNotifier extends Notifier<ContactsState> {
  ContactsState build() {
    _fetchContacts();
    return const ContactsState(isLoading: true);
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
    } catch (e) {
      state = state.copyWith(isLoading: false, error: () => e);
    }
  Future<void> loadMore() async {
    if (state.isLoadingMore || !state.hasMore || state.nextCursor == null) {
      return;
    state = state.copyWith(isLoadingMore: true);
        cursor: state.nextCursor,
        contacts: [...state.contacts, ...result.items],
        isLoadingMore: false,
      state = state.copyWith(isLoadingMore: false, error: () => e);
  Future<void> refresh() async {
    state = state.copyWith(
      isLoading: true,
      contacts: [],
      nextCursor: () => null,
      hasMore: true,
      error: () => null,
    await _fetchContacts();
  Future<void> search(String query) async {
      searchQuery: query,
  Future<void> setSort(ContactSort sort) async {
      sort: sort,
