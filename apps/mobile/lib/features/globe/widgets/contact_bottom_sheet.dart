import 'package:flutter/material.dart';
import 'package:forui/forui.dart';

class ContactBottomSheet extends StatelessWidget {
  final String contactId;
  final String? contactName;
  final double lat;
  final double lng;

  const ContactBottomSheet({
    required this.contactId,
    this.contactName,
    required this.lat,
    required this.lng,
    super.key,
  });

  static Future<void> show(
    BuildContext context, {
    required String contactId,
    String? contactName,
    required double lat,
    required double lng,
  }) {
    return showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (context) => ContactBottomSheet(
        contactId: contactId,
        contactName: contactName,
        lat: lat,
        lng: lng,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = context.theme;

    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: theme.colorScheme.border,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 24),
            Row(
              children: [
                FAvatar(
                  size: 56,
                  child: Text(
                    contactName?.isNotEmpty == true
                        ? contactName![0].toUpperCase()
                        : '?',
                    style: theme.typography.xl.copyWith(
                      color: theme.colorScheme.foreground,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        contactName ?? 'Contact #$contactId',
                        style: theme.typography.lg.copyWith(
                          color: theme.colorScheme.foreground,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${lat.toStringAsFixed(4)}, ${lng.toStringAsFixed(4)}',
                        style: theme.typography.sm.copyWith(
                          color: theme.colorScheme.mutedForeground,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: FButton(
                label: const Text('View Profile'),
                onPress: () {
                  Navigator.of(context).pop();
                  // TODO: navigate to full contact detail
                },
              ),
            ),
            const SizedBox(height: 8),
          ],
        ),
      ),
    );
  }
}
