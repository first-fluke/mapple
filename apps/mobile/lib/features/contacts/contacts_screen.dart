import 'package:flutter/widgets.dart';
import 'package:forui/forui.dart';

class ContactsScreen extends StatelessWidget {
  const ContactsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = context.theme;

    return Center(
      child: Text(
        'Contacts',
        style: theme.typography.xl2.copyWith(
          color: theme.colorScheme.foreground,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }
}
