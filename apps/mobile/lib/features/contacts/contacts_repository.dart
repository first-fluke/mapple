import 'package:dio/dio.dart';
import 'package:drift/drift.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/database/database.dart';
import 'package:mobile/database/database_provider.dart';

final contactsRepositoryProvider = Provider<ContactsRepository>((ref) {
  return ContactsRepository(
    db: ref.watch(databaseProvider),
    dio: Dio(BaseOptions(baseUrl: 'http://localhost:8000')),
  );
});

class ContactsRepository {
  final AppDatabase db;
  final Dio dio;

  ContactsRepository({required this.db, required this.dio});

  Stream<List<CachedContact>> watchContacts() => db.watchAllContacts();

  Future<DateTime?> getLastSyncTime() => db.getLastSyncTime('contacts');

  Future<void> syncContacts() async {
    final response = await dio.get<List<dynamic>>('/contacts');
    final data = response.data;
    if (data == null) return;

    final contacts = data.map((json) {
      final map = json as Map<String, dynamic>;
      return CachedContactsCompanion.insert(
        remoteId: map['id'].toString(),
        name: map['name'] as String,
        email: Value(map['email'] as String?),
        phone: Value(map['phone'] as String?),
      );
    }).toList();

    await db.upsertContacts(contacts);
    await db.updateSyncTime('contacts');
  }

  Future<void> syncRelationships() async {
    final response = await dio.get<List<dynamic>>('/relationships');
    final data = response.data;
    if (data == null) return;

    final relationships = data.map((json) {
      final map = json as Map<String, dynamic>;
      return CachedRelationshipsCompanion.insert(
        remoteId: map['id'].toString(),
        fromContactId: map['from_contact_id'] as int,
        toContactId: map['to_contact_id'] as int,
        type: map['type'] as String,
        notes: Value(map['notes'] as String?),
      );
    }).toList();

    await db.upsertRelationships(relationships);
    await db.updateSyncTime('relationships');
  }
}
