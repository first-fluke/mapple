import 'package:flutter/widgets.dart';
import 'package:forui/forui.dart';

import 'package:mobile/features/contacts/models/contact.dart';

class TimelineSection extends StatelessWidget {
  final List<TimelineEvent> events;

  const TimelineSection({required this.events, super.key});

  @override
  Widget build(BuildContext context) {
    final theme = context.theme;
    final sorted = [...events]..sort((a, b) => b.date.compareTo(a.date));

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Timeline',
          style: theme.typography.base.copyWith(
            color: theme.colorScheme.foreground,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        ...sorted.map((event) => Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: FTile(
                prefixIcon: FIcon(
                  _iconForType(event.type),
                  size: 18,
                ),
                title: Text(event.title),
                subtitle: Text(
                  [
                    _formatDate(event.date),
                    if (event.description != null) event.description,
                  ].join(' · '),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            )),
      ],
    );
  }

  SvgAsset _iconForType(TimelineEventType type) {
    return switch (type) {
      TimelineEventType.meeting => FAssets.icons.users,
      TimelineEventType.call => FAssets.icons.phone,
      TimelineEventType.email => FAssets.icons.mail,
      TimelineEventType.note => FAssets.icons.fileText,
    };
  }

  String _formatDate(DateTime date) {
    return '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
  }
}
