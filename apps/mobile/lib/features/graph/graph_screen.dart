import 'package:flutter/widgets.dart';
import 'package:flutter_inappwebview/flutter_inappwebview.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/features/globe/globe_focus_provider.dart';
import 'package:mobile/shell/app_shell.dart';
import 'package:flutter/material.dart';
import 'package:mobile/features/graph/graph_bridge.dart';
import 'package:mobile/features/graph/profile_bottom_sheet.dart';
import 'package:mobile/theme/theme_provider.dart';

class GraphScreen extends ConsumerStatefulWidget {
  const GraphScreen({super.key});

  @override
  ConsumerState<GraphScreen> createState() => _GraphScreenState();
}

class _GraphScreenState extends ConsumerState<GraphScreen> {
  @override
  Widget build(BuildContext context) {
    return InAppWebView(
      initialData: InAppWebViewInitialData(data: _kShellHtml),
      initialSettings: InAppWebViewSettings(
        javaScriptEnabled: true,
        transparentBackground: true,
      ),
      onWebViewCreated: (controller) {
        controller.addJavaScriptHandler(
          handlerName: 'onEntitySelected',
          callback: (args) {
            final data = args[0] as Map<String, dynamic>;
            final lat = (data['lat'] as num).toDouble();
            final lng = (data['lng'] as num).toDouble();

            ref.read(globeFocusProvider.notifier).set(GlobeFocus(
              latitude: lat,
              longitude: lng,
              entityId: data['id'] as String?,
            ));

            // Switch to Globe tab via StatefulShellRoute.goBranch
            ref.read(navigationShellProvider)?.goBranch(0);
          },
        );
      },
  GraphBridge? _bridge;
  void _onNodeTapped({
    required String nodeId,
    required String name,
    String? group,
    String? avatarUrl,
  }) {
    if (!mounted) return;
    showProfileBottomSheet(
      context: context,
      nodeId: nodeId,
      name: name,
      group: group,
      avatarUrl: avatarUrl,
    );
  }
  String _resolveTheme() {
    final themeMode = ref.read(themeModeProvider);
    return switch (themeMode) {
      ThemeMode.dark => 'dark',
      ThemeMode.light => 'light',
      ThemeMode.system =>
        WidgetsBinding.instance.platformDispatcher.platformBrightness ==
                Brightness.dark
            ? 'dark'
            : 'light',
    };
  void _loadSampleData() {
    final bridge = _bridge;
    if (bridge == null) return;
    // Sample data — replace with API-driven data in production
    bridge.setNodes(const [
      GraphNode(id: '1', name: 'Alice', group: 'Engineering'),
      GraphNode(id: '2', name: 'Bob', group: 'Engineering'),
      GraphNode(id: '3', name: 'Carol', group: 'Design'),
      GraphNode(id: '4', name: 'Dave', group: 'Marketing'),
      GraphNode(id: '5', name: 'Eve', group: 'Engineering'),
      GraphNode(id: '6', name: 'Frank', group: 'Design'),
    ]);
    bridge.setEdges(const [
      GraphEdge(id: 'e1', source: '1', target: '2'),
      GraphEdge(id: 'e2', source: '1', target: '3'),
      GraphEdge(id: 'e3', source: '2', target: '5'),
      GraphEdge(id: 'e4', source: '3', target: '6'),
      GraphEdge(id: 'e5', source: '4', target: '1'),
      GraphEdge(id: 'e6', source: '4', target: '6'),
      GraphEdge(id: 'e7', source: '5', target: '3'),
    ref.listen<ThemeMode>(themeModeProvider, (_, _) {
      _bridge?.setTheme(_resolveTheme());
    });
      initialFile: 'assets/graph/index.html',
        supportZoom: false,
        disableHorizontalScroll: true,
        disableVerticalScroll: true,
        _bridge = GraphBridge(
          controller: controller,
          onNodeTapped: _onNodeTapped,
      onLoadStop: (controller, url) {
        _bridge?.setTheme(_resolveTheme());
        _loadSampleData();
    );
  }
}

const _kShellHtml = '''
<!DOCTYPE html>
<html>
<head><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body>
<script>
  function selectEntity(id, lat, lng) {
    window.flutter_inappwebview.callHandler('onEntitySelected', {id, lat, lng});
  }
</script>
</body>
</html>
''';
