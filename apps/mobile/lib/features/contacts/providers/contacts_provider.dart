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
