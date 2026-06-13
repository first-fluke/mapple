// Provider-level unit tests — run headlessly without network or platform plugins.
// Full-app widget smoke test is deferred: GlobeApp requires GoRouter + Auth +
// flutter_inappwebview which cannot settle in a headless test environment.

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:mobile/features/contacts/models/contact.dart';
import 'package:mobile/features/contacts/providers/add_contact_provider.dart';
import 'package:mobile/features/contacts/providers/contacts_provider.dart';
import 'package:mobile/features/contacts/services/contacts_api.dart';
import 'package:mobile/features/graph/models/graph_models.dart';
import 'package:mobile/features/graph/providers/graph_providers.dart';
import 'package:mobile/features/graph/services/graph_api_service.dart';

// ---------------------------------------------------------------------------
// Stub ContactsApi — no network
// ---------------------------------------------------------------------------

class _StubContactsApi implements ContactsApi {
  final List<Contact> _initialContacts;
  bool createCalled = false;
  bool deleteCalled = false;
  String? lastDeletedId;
  Map<String, dynamic>? lastCreatedPayload;

  _StubContactsApi(this._initialContacts);

  @override
  Future<({bool hasMore, List<Contact> items, String? nextCursor})> list({
    String? cursor,
    int perPage = 20,
    String? search,
    String sort = 'created_at_desc',
  }) async {
    return (items: _initialContacts, nextCursor: null, hasMore: false);
  }

  @override
  Future<Contact> create(Map<String, dynamic> payload) async {
    createCalled = true;
    lastCreatedPayload = payload;
    final now = DateTime.now();
    return Contact(
      id: 'new-1',
      name: payload['name'] as String,
      email: payload['email'] as String?,
      createdAt: now,
      updatedAt: now,
    );
  }

  @override
  Future<Contact> update(String id, Map<String, dynamic> payload) async {
    final now = DateTime.now();
    return Contact(id: id, name: 'Updated', createdAt: now, updatedAt: now);
  }

  @override
  Future<void> delete(String id) async {
    deleteCalled = true;
    lastDeletedId = id;
  }
}

// ---------------------------------------------------------------------------
// Stub GraphApiService — no network
// ---------------------------------------------------------------------------

class _StubGraphApiService implements GraphApiService {
  final GraphData _data;
  final Exception? _error;

  _StubGraphApiService({required GraphData data, Exception? error})
      : _data = data,
        _error = error;

  @override
  Future<GraphData> fetchGraphData(GraphEdgeType type) async {
    if (_error != null) throw _error;
    return _data;
  }

  @override
  Future<List<GraphApiEdge>> fetchEdges(GraphEdgeType type) async {
    if (_error != null) throw _error;
    return _data.edges;
  }

  @override
  Future<List<GraphApiCluster>> fetchClusters(GraphEdgeType type) async {
    if (_error != null) throw _error;
    return _data.clusters;
  }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

Contact _makeContact({String id = '1', String name = 'Alice'}) {
  final now = DateTime.now();
  return Contact(id: id, name: name, createdAt: now, updatedAt: now);
}

/// Waits until the provider's isLoading becomes false.
Future<void> _waitForLoad(
  ProviderContainer container,
  NotifierProvider<ContactsNotifier, ContactsState> provider,
) async {
  // Poll until the notifier leaves its loading state.
  for (var i = 0; i < 50; i++) {
    await Future<void>.delayed(const Duration(milliseconds: 10));
    if (!container.read(provider).isLoading) break;
  }
}

Future<void> _waitForGraphLoad(
  ProviderContainer container,
) async {
  for (var i = 0; i < 50; i++) {
    await Future<void>.delayed(const Duration(milliseconds: 10));
    if (!container.read(graphScreenProvider).isLoading) break;
  }
}

// ---------------------------------------------------------------------------
// Tests: AddContactNotifier (pure state — no async issues)
// ---------------------------------------------------------------------------

void main() {
  group('AddContactNotifier — state logic', () {
    test('initial state has empty name and step 0', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      final state = container.read(addContactProvider);
      expect(state.name, '');
      expect(state.currentStep, 0);
      expect(state.isSaving, false);
    });

    test('setName updates name and isBasicInfoValid becomes true', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      container.read(addContactProvider.notifier).setName('Bob');
      expect(container.read(addContactProvider).name, 'Bob');
      expect(container.read(addContactProvider).isBasicInfoValid, true);
    });

    test('nextStep increments currentStep', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      container.read(addContactProvider.notifier).nextStep();
      expect(container.read(addContactProvider).currentStep, 1);
    });

    test('previousStep decrements currentStep', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      final notifier = container.read(addContactProvider.notifier);
      notifier.nextStep();
      notifier.previousStep();
      expect(container.read(addContactProvider).currentStep, 0);
    });

    test('setLocation persists lat/lng/locationName into state', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      container.read(addContactProvider.notifier).setLocation(
            latitude: 37.5665,
            longitude: 126.9780,
            locationName: 'Seoul Office',
          );

      final state = container.read(addContactProvider);
      expect(state.latitude, 37.5665);
      expect(state.longitude, 126.9780);
      expect(state.locationName, 'Seoul Office');
    });

    test('toPayload includes location fields when set', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      final notifier = container.read(addContactProvider.notifier);
      notifier.setName('Test Contact');
      notifier.setEmail('test@example.com');
      notifier.setLocation(
        latitude: 37.5665,
        longitude: 126.9780,
        locationName: 'Seoul',
      );

      final payload = container.read(addContactProvider).toPayload();
      expect(payload['name'], 'Test Contact');
      expect(payload['email'], 'test@example.com');
      expect(payload['latitude'], 37.5665);
      expect(payload['longitude'], 126.9780);
      expect(payload['location_name'], 'Seoul');
    });

    test('reset clears all state to defaults', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      final notifier = container.read(addContactProvider.notifier);
      notifier.setName('To be cleared');
      notifier.nextStep();
      notifier.reset();

      final state = container.read(addContactProvider);
      expect(state.name, '');
      expect(state.currentStep, 0);
    });

    test('setSaving sets isSaving=true and clears error', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      final notifier = container.read(addContactProvider.notifier);
      notifier.setSaveError('previous error');
      notifier.setSaving(saving: true);

      final state = container.read(addContactProvider);
      expect(state.isSaving, true);
      expect(state.saveError, isNull);
    });

    test('setSaveError records message and sets isSaving=false', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      container.read(addContactProvider.notifier).setSaveError('Network error');
      final state = container.read(addContactProvider);
      expect(state.saveError, 'Network error');
      expect(state.isSaving, false);
    });
  });

  // ---------------------------------------------------------------------------
  // Tests: AddContactState pure logic
  // ---------------------------------------------------------------------------

  group('AddContactState validation', () {
    test('isBasicInfoValid is false for whitespace-only name', () {
      const state = AddContactState(name: '   ');
      expect(state.isBasicInfoValid, false);
    });

    test('isBasicInfoValid is true for non-empty name', () {
      const state = AddContactState(name: 'Charlie');
      expect(state.isBasicInfoValid, true);
    });

    test('toPayload omits null optional fields', () {
      const state = AddContactState(name: 'Dana');
      final payload = state.toPayload();
      expect(payload.containsKey('email'), false);
      expect(payload.containsKey('phone'), false);
      expect(payload.containsKey('latitude'), false);
    });

    test('toPayload omits blank email', () {
      const state = AddContactState(name: 'Eve', email: '  ');
      final payload = state.toPayload();
      expect(payload.containsKey('email'), false);
    });

    test('toPayload name is trimmed', () {
      const state = AddContactState(name: '  Frank  ');
      final payload = state.toPayload();
      expect(payload['name'], 'Frank');
    });
  });

  // ---------------------------------------------------------------------------
  // Tests: ContactsNotifier with stubbed API
  // ---------------------------------------------------------------------------

  group('ContactsNotifier — API operations', () {
    test('createContact calls API stub and prepends contact to list', () async {
      final alice = _makeContact(id: '1', name: 'Alice');
      final stub = _StubContactsApi([alice]);

      final container = ProviderContainer(
        overrides: [contactsApiProvider.overrideWithValue(stub)],
      );
      addTearDown(container.dispose);

      // Subscribe to trigger the provider build, then wait for async fetch.
      container.listen(contactsProvider, (_, _) {});
      await _waitForLoad(container, contactsProvider);

      final created = await container
          .read(contactsProvider.notifier)
          .createContact({'name': 'Bob', 'email': 'bob@example.com'});

      expect(created.id, 'new-1');
      expect(created.name, 'Bob');
      expect(stub.createCalled, isTrue);
      expect(stub.lastCreatedPayload?['name'], 'Bob');

      // Newly created contact should be at the front of the list.
      final contacts = container.read(contactsProvider).contacts;
      expect(contacts.first.id, 'new-1');
    });

    test('deleteContact calls API stub and removes contact from list',
        () async {
      final alice = _makeContact(id: '42', name: 'Alice');
      final stub = _StubContactsApi([alice]);

      final container = ProviderContainer(
        overrides: [contactsApiProvider.overrideWithValue(stub)],
      );
      addTearDown(container.dispose);

      container.listen(contactsProvider, (_, _) {});
      await _waitForLoad(container, contactsProvider);

      await container.read(contactsProvider.notifier).deleteContact('42');

      expect(stub.deleteCalled, isTrue);
      expect(stub.lastDeletedId, '42');

      final remaining =
          container.read(contactsProvider).contacts.where((c) => c.id == '42');
      expect(remaining, isEmpty);
    });
  });

  // ---------------------------------------------------------------------------
  // Tests: GraphScreenNotifier with stubbed service
  // ---------------------------------------------------------------------------

  group('GraphScreenNotifier — data loading', () {
    test('loads graph data successfully and populates state', () async {
      final testData = GraphData(
        edges: [
          const GraphApiEdge(
            sourceContactId: 1,
            targetContactId: 2,
            type: GraphEdgeType.company,
            label: 'Acme Corp',
          ),
        ],
        clusters: [],
      );

      final container = ProviderContainer(
        overrides: [
          graphApiServiceProvider
              .overrideWithValue(_StubGraphApiService(data: testData)),
        ],
      );
      addTearDown(container.dispose);

      container.listen(graphScreenProvider, (_, _) {});
      await _waitForGraphLoad(container);

      final state = container.read(graphScreenProvider);
      expect(state.isLoading, false);
      expect(state.error, isNull);
      expect(state.data?.edges.length, 1);
      expect(state.data?.edges.first.label, 'Acme Corp');
    });

    test('sets error state when API throws', () async {
      final container = ProviderContainer(
        overrides: [
          graphApiServiceProvider.overrideWithValue(
            _StubGraphApiService(
              data: GraphData.empty,
              error: Exception('Network failure'),
            ),
          ),
        ],
      );
      addTearDown(container.dispose);

      container.listen(graphScreenProvider, (_, _) {});
      await _waitForGraphLoad(container);

      final state = container.read(graphScreenProvider);
      expect(state.isLoading, false);
      expect(state.error, isNotNull);
      expect(state.data, isNull);
    });

    test('selectType triggers reload and updates selectedType', () async {
      final testData = GraphData(
        edges: [
          const GraphApiEdge(
            sourceContactId: 10,
            targetContactId: 20,
            type: GraphEdgeType.tag,
            label: 'flutter',
          ),
        ],
        clusters: [],
      );

      final container = ProviderContainer(
        overrides: [
          graphApiServiceProvider
              .overrideWithValue(_StubGraphApiService(data: testData)),
        ],
      );
      addTearDown(container.dispose);

      container.listen(graphScreenProvider, (_, _) {});
      await _waitForGraphLoad(container);

      await container
          .read(graphScreenProvider.notifier)
          .selectType(GraphEdgeType.tag);
      await _waitForGraphLoad(container);

      final state = container.read(graphScreenProvider);
      expect(state.selectedType, GraphEdgeType.tag);
      expect(state.isLoading, false);
      expect(state.data?.edges.first.label, 'flutter');
    });
  });
}
