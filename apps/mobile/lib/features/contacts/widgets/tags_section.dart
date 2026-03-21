import 'package:flutter/widgets.dart';
import 'package:forui/forui.dart';

class TagsSection extends StatelessWidget {
  final List<String> tags;

  const TagsSection({required this.tags, super.key});

  @override
  Widget build(BuildContext context) {
    final theme = context.theme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Tags',
          style: theme.typography.base.copyWith(
            color: theme.colorScheme.foreground,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: tags.map((tag) => FBadge(label: Text(tag))).toList(),
        ),
      ],
    );
  }
}
