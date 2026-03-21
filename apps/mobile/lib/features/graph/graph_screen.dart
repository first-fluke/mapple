import 'package:flutter/widgets.dart';
import 'package:forui/forui.dart';

class GraphScreen extends StatelessWidget {
  const GraphScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = context.theme;

    return Center(
      child: Text(
        'Graph',
        style: theme.typography.xl2.copyWith(
          color: theme.colorScheme.foreground,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }
}
