import 'package:flutter/widgets.dart';
import 'package:forui/forui.dart';

import 'package:mobile/features/contacts/models/contact.dart';

class SocialLinksSection extends StatelessWidget {
  final List<SocialLink> socialLinks;

  const SocialLinksSection({required this.socialLinks, super.key});

  @override
  Widget build(BuildContext context) {
    final theme = context.theme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Social',
          style: theme.typography.base.copyWith(
            color: theme.colorScheme.foreground,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        ...socialLinks.map((link) => Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: FTile(
                prefixIcon: FIcon(
                  _iconForPlatform(link.platform),
                  size: 18,
                ),
                title: Text(_labelForPlatform(link.platform)),
                subtitle: Text(
                  link.url,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            )),
      ],
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
