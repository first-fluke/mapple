import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:forui/forui.dart';

import 'package:mobile/features/contacts/models/contact.dart';
import 'package:mobile/features/contacts/providers/add_contact_provider.dart';

const _suggestedTags = [
  'client',
  'partner',
  'colleague',
  'friend',
  'tech',
  'design',
  'marketing',
  'sales',
  'engineering',
  'freelancer',
  'investor',
  'mentor',
];

class TagsCareerStep extends ConsumerStatefulWidget {
  const TagsCareerStep({super.key});

  @override
  ConsumerState<TagsCareerStep> createState() => _TagsCareerStepState();
}

class _TagsCareerStepState extends ConsumerState<TagsCareerStep> {
  final _tagController = TextEditingController();
  final _socialUrlController = TextEditingController();
  SocialPlatform _selectedPlatform = SocialPlatform.linkedin;

  @override
  void dispose() {
    _tagController.dispose();
    _socialUrlController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = context.theme;
    final state = ref.watch(addContactProvider);
    final notifier = ref.read(addContactProvider.notifier);

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(
          'Tags & Social',
          style: theme.typography.lg.copyWith(
            color: theme.colorScheme.foreground,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          'Add tags and social links to this contact',
          style: theme.typography.sm.copyWith(
            color: theme.colorScheme.mutedForeground,
          ),
        ),
        const SizedBox(height: 20),
        // Tags section
        Text(
          'Tags',
          style: theme.typography.base.copyWith(
            color: theme.colorScheme.foreground,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        // Selected tags
        if (state.tags.isNotEmpty) ...[
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: state.tags
                .map((tag) => GestureDetector(
                      onTap: () => notifier.removeTag(tag),
                      child: FBadge(
                        label: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(tag),
                            const SizedBox(width: 4),
                            FIcon(
                              FAssets.icons.x,
                              size: 12,
                              color: theme.colorScheme.primaryForeground,
                            ),
                          ],
                        ),
                      ),
                    ))
                .toList(),
          ),
          const SizedBox(height: 12),
        ],
        // Custom tag input
        Row(
          children: [
            Expanded(
              child: FTextField(
                hint: 'Add custom tag',
                controller: _tagController,
              ),
            ),
            const SizedBox(width: 8),
            FButton.icon(
              onPress: () {
                final tag = _tagController.text.trim();
                if (tag.isNotEmpty) {
                  notifier.addTag(tag);
                  _tagController.clear();
                }
              },
              child: FIcon(FAssets.icons.plus),
            ),
          ],
        ),
        const SizedBox(height: 12),
        // Suggested tags
        Text(
          'Suggested',
          style: theme.typography.xs.copyWith(
            color: theme.colorScheme.mutedForeground,
          ),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: _suggestedTags
              .where((tag) => !state.tags.contains(tag))
              .map((tag) => GestureDetector(
                    onTap: () => notifier.addTag(tag),
                    child: FBadge(
                      style: FBadgeStyle.outline,
                      label: Text(tag),
                    ),
                  ))
              .toList(),
        ),
        const SizedBox(height: 24),
        FDivider(),
        const SizedBox(height: 16),
        // Social links section
        Text(
          'Social Links',
          style: theme.typography.base.copyWith(
            color: theme.colorScheme.foreground,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        // Existing links
        ...state.socialLinks.asMap().entries.map((entry) => Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: FTile(
                prefixIcon: FIcon(
                  _iconForPlatform(entry.value.platform),
                  size: 18,
                ),
                title: Text(_labelForPlatform(entry.value.platform)),
                subtitle: Text(
                  entry.value.url,
                  overflow: TextOverflow.ellipsis,
                ),
                suffixIcon: GestureDetector(
                  onTap: () => notifier.removeSocialLink(entry.key),
                  child: FIcon(
                    FAssets.icons.trash2,
                    size: 16,
                    color: theme.colorScheme.destructive,
                  ),
                ),
              ),
            )),
        const SizedBox(height: 8),
        // Add social link
        Row(
          children: [
            // Platform picker - simple dropdown-like selector
            GestureDetector(
              onTap: () => _showPlatformPicker(context, theme),
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                decoration: BoxDecoration(
                  border: Border.all(color: theme.colorScheme.border),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    FIcon(
                      _iconForPlatform(_selectedPlatform),
                      size: 16,
                    ),
                    const SizedBox(width: 4),
                    FIcon(FAssets.icons.chevronDown, size: 14),
                  ],
                ),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: FTextField(
                hint: 'Profile URL',
                controller: _socialUrlController,
                keyboardType: TextInputType.url,
              ),
            ),
            const SizedBox(width: 8),
            FButton.icon(
              onPress: () {
                final url = _socialUrlController.text.trim();
                if (url.isNotEmpty) {
                  notifier.addSocialLink(
                    SocialLink(platform: _selectedPlatform, url: url),
                  );
                  _socialUrlController.clear();
                }
              },
              child: FIcon(FAssets.icons.plus),
            ),
          ],
        ),
      ],
    );
  }

  void _showPlatformPicker(BuildContext context, FThemeData theme) {
    showModalBottomSheet(
      context: context,
      builder: (context) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: SocialPlatform.values.map((platform) {
            return ListTile(
              leading: FIcon(_iconForPlatform(platform), size: 20),
              title: Text(
                _labelForPlatform(platform),
                style: theme.typography.base.copyWith(
                  color: theme.colorScheme.foreground,
                ),
              ),
              onTap: () {
                setState(() => _selectedPlatform = platform);
                Navigator.of(context).pop();
              },
            );
          }).toList(),
        ),
      ),
    );
  }

  SvgAsset _iconForPlatform(SocialPlatform platform) {
    return switch (platform) {
      SocialPlatform.linkedin => FAssets.icons.linkedin,
      SocialPlatform.twitter => FAssets.icons.twitter,
      SocialPlatform.instagram => FAssets.icons.instagram,
      SocialPlatform.facebook => FAssets.icons.facebook,
      SocialPlatform.github => FAssets.icons.github,
      SocialPlatform.website => FAssets.icons.globe,
    };
  }

  String _labelForPlatform(SocialPlatform platform) {
    return switch (platform) {
      SocialPlatform.linkedin => 'LinkedIn',
      SocialPlatform.twitter => 'Twitter',
      SocialPlatform.instagram => 'Instagram',
      SocialPlatform.facebook => 'Facebook',
      SocialPlatform.github => 'GitHub',
      SocialPlatform.website => 'Website',
    };
  }
}
