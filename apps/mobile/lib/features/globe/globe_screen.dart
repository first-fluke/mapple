import 'package:flutter/widgets.dart';
import 'package:forui/forui.dart';

class GlobeScreen extends StatelessWidget {
  const GlobeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = context.theme;

    return Center(
      child: Text(
        'Globe',
        style: theme.typography.xl2.copyWith(
          color: theme.colorScheme.foreground,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }
}
