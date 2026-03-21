import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/app.dart';

void main() {
  testWidgets('App renders with bottom navigation', (WidgetTester tester) async {
    await tester.pumpWidget(const ProviderScope(child: GlobeApp()));
    await tester.pumpAndSettle();

    expect(find.text('Globe'), findsWidgets);
    expect(find.text('Graph'), findsOneWidget);
    expect(find.text('Contacts'), findsOneWidget);
    expect(find.text('Settings'), findsOneWidget);
  });
}
