import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/models/contact.dart';

final contactsProvider = Provider<List<Contact>>((ref) {
  return const [
    Contact(id: 1, name: 'Alice Johnson', email: 'alice@example.com', phone: '+1-555-0101'),
    Contact(id: 2, name: 'Bob Smith', email: 'bob@example.com', phone: '+1-555-0102'),
    Contact(id: 3, name: 'Carol Williams', email: 'carol@example.com'),
    Contact(id: 4, name: 'David Brown', email: 'david@example.com', phone: '+1-555-0104'),
    Contact(id: 5, name: 'Eve Davis', phone: '+1-555-0105'),
  ];
});
