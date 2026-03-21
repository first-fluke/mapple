import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:forui/forui.dart';
import 'package:go_router/go_router.dart';

import 'package:mobile/features/contacts/models/contact.dart';
import 'package:mobile/features/contacts/providers/contacts_provider.dart';
import 'package:mobile/connectivity/connectivity_provider.dart';
import 'package:mobile/features/contacts/contacts_provider.dart';
import 'package:mobile/widgets/stale_data_banner.dart';
import 'package:flutter/material.dart';

class ContactsScreen extends ConsumerWidget {
  const ContactsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final contacts = ref.watch(contactsProvider);
    final theme = context.theme;

    return Stack(
      children: [
        if (contacts.isEmpty)
          Center(
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
                  'No contacts yet',
                  style: theme.typography.lg.copyWith(
                    color: theme.colorScheme.mutedForeground,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Tap + to add your first contact',
                  style: theme.typography.sm.copyWith(
                    color: theme.colorScheme.mutedForeground,
                  ),
                ),
              ],
            ),
          )
        else
          ListView.builder(
            padding: const EdgeInsets.only(top: 8, bottom: 80),
            itemCount: contacts.length,
            itemBuilder: (context, index) {
              final contact = contacts[index];
              return _ContactListItem(contact: contact);
            },
          ),
        Positioned(
          right: 16,
          bottom: 16,
          child: FloatingActionButton(
            onPressed: () => context.go('/contacts/add'),
            backgroundColor: theme.colorScheme.primary,
            foregroundColor: theme.colorScheme.primaryForeground,
            child: const Icon(Icons.add),
          ),
        ),
      ],
    );
  }
}

class _ContactListItem extends StatelessWidget {
  final Contact contact;

  const _ContactListItem({required this.contact});

  @override
  Widget build(BuildContext context) {
    final theme = context.theme;
    final isOnline = ref.watch(isOnlineProvider);
    final contactsAsync = ref.watch(contactsStreamProvider);
    final lastSync = ref.watch(lastSyncTimeProvider);

    return FTile(
      prefixIcon: CircleAvatar(
        radius: 20,
        backgroundColor: theme.colorScheme.secondary,
        child: Text(
          contact.initials,
          style: theme.typography.sm.copyWith(
            color: theme.colorScheme.secondaryForeground,
            fontWeight: FontWeight.bold,
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
    final contacts = ref.watch(contactsProvider);
      crossAxisAlignment: CrossAxisAlignment.start,
        Padding(
          padding: const EdgeInsets.all(16),
          child: Semantics(
            header: true,
            child: Text(
              'Contacts',
              style: theme.typography.xl2.copyWith(
                color: theme.colorScheme.foreground,
                fontWeight: FontWeight.bold,
              ),
          ),
        ),
      ],
        Expanded(
          child: ListView.builder(
            itemCount: contacts.length,
            itemBuilder: (context, index) {
              final contact = contacts[index];
              return Semantics(
                label: contact.name,
                hint: [
                  if (contact.email != null) contact.email!,
                  if (contact.phone != null) contact.phone!,
                ].join(', '),
                child: FTile(
                  prefixIcon: FIcon(FAssets.icons.user),
                  title: Text(contact.name),
                  subtitle: Text(contact.email ?? contact.phone ?? ''),
                ),
              );
            },
          ),
        ),
import 'package:mobile/features/contacts/providers/contacts_provider.dart';
import 'package:mobile/features/contacts/widgets/contact_tile.dart';
import 'package:mobile/features/contacts/widgets/empty_contacts.dart';
class ContactsScreen extends ConsumerStatefulWidget {
  ConsumerState<ContactsScreen> createState() => _ContactsScreenState();
}
class _ContactsScreenState extends ConsumerState<ContactsScreen> {
  final _scrollController = ScrollController();
  final _searchController = TextEditingController();
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
  }
  void dispose() {
    _scrollController.dispose();
    _searchController.dispose();
    super.dispose();
  void _onScroll() {
    if (_scrollController.position.pixels >=
        _scrollController.position.maxScrollExtent - 200) {
      ref.read(contactsProvider.notifier).loadMore();
    }
  Widget build(BuildContext context) {
    final state = ref.watch(contactsProvider);
        // Header
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '연락처',
                style: theme.typography.xl2.copyWith(
                  color: theme.colorScheme.foreground,
                  fontWeight: FontWeight.bold,
              const SizedBox(height: 12),
              // Search bar
              SizedBox(
                height: 40,
                child: TextField(
                  controller: _searchController,
                  onChanged: (value) {
                    ref.read(contactsProvider.notifier).search(value);
                  },
                  style: theme.typography.sm.copyWith(
                    color: theme.colorScheme.foreground,
                  ),
                  decoration: InputDecoration(
                    hintText: '이름으로 검색...',
                    hintStyle: theme.typography.sm.copyWith(
                      color: theme.colorScheme.mutedForeground,
                    ),
                    prefixIcon: Icon(
                      Icons.search,
                      size: 20,
                    suffixIcon: _searchController.text.isNotEmpty
                        ? GestureDetector(
                            onTap: () {
                              _searchController.clear();
                              ref.read(contactsProvider.notifier).search('');
                            },
                            child: Icon(
                              Icons.close,
                              size: 18,
                              color: theme.colorScheme.mutedForeground,
                            ),
                          )
                        : null,
                    contentPadding: const EdgeInsets.symmetric(horizontal: 12),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                      borderSide: BorderSide(color: theme.colorScheme.border),
                    enabledBorder: OutlineInputBorder(
                    focusedBorder: OutlineInputBorder(
                      borderSide: BorderSide(color: theme.colorScheme.primary),
                    filled: true,
                    fillColor: theme.colorScheme.background,
              const SizedBox(height: 8),
              // Sort row
              Row(
                children: [
                  Text(
                    '정렬:',
                    style: theme.typography.xs.copyWith(
                  const SizedBox(width: 8),
                  ...ContactSort.values.map((sort) {
                    final isSelected = state.sort == sort;
                    return Padding(
                      padding: const EdgeInsets.only(right: 4),
                      child: GestureDetector(
                        onTap: () {
                          ref.read(contactsProvider.notifier).setSort(sort);
                        },
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 10,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: isSelected
                                ? theme.colorScheme.primary
                                : theme.colorScheme.muted,
                            borderRadius: BorderRadius.circular(12),
                          child: Text(
                            sort.label,
                            style: theme.typography.xs.copyWith(
                              color: isSelected
                                  ? theme.colorScheme.primaryForeground
                                  : theme.colorScheme.mutedForeground,
                              fontWeight: isSelected
                                  ? FontWeight.w600
                                  : FontWeight.normal,
                        ),
                      ),
                    );
                  }),
                ],
            ],
        // Content
          child: _buildContent(state),
    );
  Widget _buildContent(ContactsState state) {
    if (state.isLoading) {
      return const Center(child: CircularProgressIndicator());
    if (state.error != null && state.contacts.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              '오류가 발생했습니다',
              style: context.theme.typography.base.copyWith(
                color: context.theme.colorScheme.destructive,
            const SizedBox(height: 8),
            GestureDetector(
              onTap: () => ref.read(contactsProvider.notifier).refresh(),
              child: Text(
                '다시 시도',
                style: context.theme.typography.sm.copyWith(
                  color: context.theme.colorScheme.primary,
                  fontWeight: FontWeight.w600,
          ],
      );
    if (state.contacts.isEmpty) {
      return EmptyContacts(
        isSearchResult: state.searchQuery.isNotEmpty,
    return RefreshIndicator(
      onRefresh: () => ref.read(contactsProvider.notifier).refresh(),
      child: ListView.builder(
        controller: _scrollController,
        physics: const AlwaysScrollableScrollPhysics(),
        itemCount: state.contacts.length + (state.hasMore ? 1 : 0),
        itemBuilder: (context, index) {
          if (index >= state.contacts.length) {
            return const Padding(
              padding: EdgeInsets.all(16),
              child: Center(child: CircularProgressIndicator()),
            );
          }
          return RepaintBoundary(
            child: ContactTile(contact: state.contacts[index]),
          );
        },
      ),
      title: Text(contact.name),
      subtitle: Text(
        [contact.jobTitle, contact.company]
            .where((s) => s != null && s.isNotEmpty)
            .join(' · '),
      ),
      suffixIcon: FIcon(
        FAssets.icons.chevronRight,
        color: theme.colorScheme.mutedForeground,
      ),
      onPress: () => context.go('/contacts/${contact.id}'),
    );
  }
}
