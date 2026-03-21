import 'dart:io';

import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';

part 'database.g.dart';

class CachedContacts extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get remoteId => text().unique()();
  TextColumn get name => text()();
  TextColumn get email => text().nullable()();
  TextColumn get phone => text().nullable()();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
  DateTimeColumn get updatedAt => dateTime().withDefault(currentDateAndTime)();
}

class CachedRelationships extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get remoteId => text().unique()();
  @ReferenceName('fromRelationships')
  IntColumn get fromContactId =>
      integer().references(CachedContacts, #id)();
  @ReferenceName('toRelationships')
  IntColumn get toContactId =>
      integer().references(CachedContacts, #id)();
  TextColumn get type => text()();
  TextColumn get notes => text().nullable()();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
}

class SyncMetadata extends Table {
  TextColumn get entity => text()();
  DateTimeColumn get lastSyncedAt => dateTime()();

  @override
  Set<Column> get primaryKey => {entity};
}

@DriftDatabase(tables: [CachedContacts, CachedRelationships, SyncMetadata])
class AppDatabase extends _$AppDatabase {
  AppDatabase() : super(_openConnection());

  AppDatabase.forTesting(super.e);

  @override
  int get schemaVersion => 1;

  Future<DateTime?> getLastSyncTime(String entity) async {
    final row = await (select(syncMetadata)
          ..where((t) => t.entity.equals(entity)))
        .getSingleOrNull();
    return row?.lastSyncedAt;
  }

  Future<void> updateSyncTime(String entity) async {
    await into(syncMetadata).insertOnConflictUpdate(
      SyncMetadataCompanion.insert(
        entity: entity,
        lastSyncedAt: DateTime.now(),
      ),
    );
  }

  Future<List<CachedContact>> getAllContacts() {
    return select(cachedContacts).get();
  }

  Stream<List<CachedContact>> watchAllContacts() {
    return select(cachedContacts).watch();
  }

  Future<void> upsertContact(CachedContactsCompanion contact) async {
    await into(cachedContacts).insertOnConflictUpdate(contact);
  }

  Future<void> upsertContacts(List<CachedContactsCompanion> contacts) async {
    await batch((batch) {
      for (final contact in contacts) {
        batch.insert(cachedContacts, contact, onConflict: DoUpdate((_) => contact));
      }
    });
  }

  Future<List<CachedRelationship>> getAllRelationships() {
    return select(cachedRelationships).get();
  }

  Stream<List<CachedRelationship>> watchAllRelationships() {
    return select(cachedRelationships).watch();
  }

  Future<void> upsertRelationships(
      List<CachedRelationshipsCompanion> relationships) async {
    await batch((batch) {
      for (final rel in relationships) {
        batch.insert(cachedRelationships, rel,
            onConflict: DoUpdate((_) => rel));
      }
    });
  }
}

LazyDatabase _openConnection() {
  return LazyDatabase(() async {
    final dbFolder = await getApplicationDocumentsDirectory();
    final file = File(p.join(dbFolder.path, 'globe_crm.sqlite'));
    return NativeDatabase.createInBackground(file);
  });
}
