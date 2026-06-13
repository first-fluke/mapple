import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:forui/forui.dart';
import 'package:go_router/go_router.dart';

import 'package:mobile/features/contacts/models/contact.dart';
import 'package:mobile/features/contacts/providers/contacts_provider.dart';
import 'package:mobile/features/contacts/widgets/meetings_section.dart';
import 'package:mobile/features/contacts/widgets/profile_header.dart';
import 'package:mobile/features/contacts/widgets/social_links_section.dart';
import 'package:mobile/features/contacts/widgets/tags_section.dart';
import 'package:mobile/features/contacts/widgets/timeline_section.dart';
import 'package:mobile/l10n/app_localizations.dart';

class ContactDetailScreen extends ConsumerStatefulWidget {
  final String contactId;

  const ContactDetailScreen({required this.contactId, super.key});

  @override
  ConsumerState<ContactDetailScreen> createState() =>
      _ContactDetailScreenState();
}

class _ContactDetailScreenState extends ConsumerState<ContactDetailScreen> {
  bool _isDeleting = false;

  Future<void> _confirmDelete(Contact contact) async {
    final theme = context.theme;
    final l10n = AppLocalizations.of(context)!;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: theme.colorScheme.background,
        title: Text(
          l10n.contactDetailDeleteTitle,
          style: theme.typography.lg.copyWith(
            color: theme.colorScheme.foreground,
            fontWeight: FontWeight.bold,
          ),
        ),
        content: Text(
          l10n.contactDetailDeleteMessage(contact.name),
          style: theme.typography.sm.copyWith(
            color: theme.colorScheme.mutedForeground,
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(false),
            child: Text(
              l10n.contactDetailDeleteCancel,
              style: theme.typography.sm.copyWith(
                color: theme.colorScheme.mutedForeground,
              ),
            ),
          ),
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(true),
            child: Text(
              l10n.contactDetailDeleteConfirm,
              style: theme.typography.sm.copyWith(
                color: theme.colorScheme.destructive,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );

    if (confirmed != true) return;
    if (!mounted) return;

    setState(() => _isDeleting = true);
    try {
      await ref.read(contactsProvider.notifier).deleteContact(contact.id);
      if (!mounted) return;
      context.go('/contacts');
    } catch (e) {
      if (!mounted) return;
      setState(() => _isDeleting = false);
      final l10nInner = AppLocalizations.of(context)!;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(l10nInner.contactDetailDeleteFailed),
          backgroundColor: context.theme.colorScheme.destructive,
        ),
      );
    }
  }

  void _navigateToEdit(Contact contact) {
    // TODO(oma-deferred): implement edit-contact screen with pre-filled wizard
    final l10n = AppLocalizations.of(context)!;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(l10n.contactDetailEditComingSoon)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final contact = ref.watch(contactByIdProvider(widget.contactId));
    final theme = context.theme;
    final l10n = AppLocalizations.of(context)!;

    if (contact == null) {
      return Center(
        child: Text(
          l10n.contactDetailNotFound,
          style: theme.typography.lg.copyWith(
            color: theme.colorScheme.mutedForeground,
          ),
        ),
      );
    }

    if (_isDeleting) {
      return const Center(child: CircularProgressIndicator());
    }

    return Column(
      children: [
        // Top bar
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 8),
          child: Row(
            children: [
              FButton.icon(
                onPress: () => context.go('/contacts'),
                child: FIcon(FAssets.icons.chevronLeft),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  contact.name,
                  style: theme.typography.xl.copyWith(
                    color: theme.colorScheme.foreground,
                    fontWeight: FontWeight.bold,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              // Edit button
              FButton.icon(
                onPress: () => _navigateToEdit(contact),
                child: FIcon(
                  FAssets.icons.pencil,
                  color: theme.colorScheme.mutedForeground,
                ),
              ),
              // Delete button
              FButton.icon(
                onPress: () => _confirmDelete(contact),
                child: FIcon(
                  FAssets.icons.trash2,
                  color: theme.colorScheme.destructive,
                ),
              ),
            ],
          ),
        ),
        // Content
        Expanded(
          child: ListView(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            children: [
              ProfileHeader(contact: contact),
              const SizedBox(height: 24),
              if (contact.socialLinks.isNotEmpty) ...[
                SocialLinksSection(socialLinks: contact.socialLinks),
                const SizedBox(height: 24),
              ],
              if (contact.timeline.isNotEmpty) ...[
                TimelineSection(events: contact.timeline),
                const SizedBox(height: 24),
              ],
              if (contact.meetings.isNotEmpty) ...[
                MeetingsSection(meetings: contact.meetings),
                const SizedBox(height: 24),
              ],
              if (contact.tags.isNotEmpty) ...[
                TagsSection(tags: contact.tags),
                const SizedBox(height: 24),
              ],
              const SizedBox(height: 16),
            ],
          ),
        ),
      ],
    );
  }
}
