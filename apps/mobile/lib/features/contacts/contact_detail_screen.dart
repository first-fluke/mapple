import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:forui/forui.dart';
import 'package:go_router/go_router.dart';

import 'package:mobile/features/contacts/providers/contacts_provider.dart';
import 'package:mobile/features/contacts/widgets/meetings_section.dart';
import 'package:mobile/features/contacts/widgets/profile_header.dart';
import 'package:mobile/features/contacts/widgets/social_links_section.dart';
import 'package:mobile/features/contacts/widgets/tags_section.dart';
import 'package:mobile/features/contacts/widgets/timeline_section.dart';

class ContactDetailScreen extends ConsumerWidget {
  final String contactId;

  const ContactDetailScreen({required this.contactId, super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final contact = ref.watch(contactByIdProvider(contactId));
    final theme = context.theme;

    if (contact == null) {
      return Center(
        child: Text(
          'Contact not found',
          style: theme.typography.lg.copyWith(
            color: theme.colorScheme.mutedForeground,
          ),
        ),
      );
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
