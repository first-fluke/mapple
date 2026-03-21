import 'package:flutter/widgets.dart';
import 'package:forui/forui.dart';

import 'package:mobile/features/contacts/models/contact.dart';

class MeetingsSection extends StatelessWidget {
  final List<Meeting> meetings;

  const MeetingsSection({required this.meetings, super.key});

  @override
  Widget build(BuildContext context) {
    final theme = context.theme;
    final sorted = [...meetings]..sort((a, b) => b.date.compareTo(a.date));

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Meetings',
          style: theme.typography.base.copyWith(
            color: theme.colorScheme.foreground,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        ...sorted.map((meeting) => Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: FTile(
                prefixIcon: FIcon(FAssets.icons.calendar, size: 18),
                title: Text(meeting.title),
                subtitle: Text(
                  [
                    _formatDate(meeting.date),
                    if (meeting.location != null) meeting.location,
                    if (meeting.description != null) meeting.description,
                  ].join(' · '),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            )),
      ],
    );
  }

  String _formatDate(DateTime date) {
    return '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
  }
}
