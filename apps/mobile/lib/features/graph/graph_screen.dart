import 'package:flutter/material.dart';
import 'package:flutter_inappwebview/flutter_inappwebview.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/features/graph/graph_bridge.dart';
import 'package:mobile/features/graph/profile_bottom_sheet.dart';
import 'package:mobile/theme/theme_provider.dart';

class GraphScreen extends ConsumerStatefulWidget {
  const GraphScreen({super.key});

  @override
  ConsumerState<GraphScreen> createState() => _GraphScreenState();
}

class _GraphScreenState extends ConsumerState<GraphScreen> {
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
  }

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
    ]);
  }

  @override
  Widget build(BuildContext context) {
    ref.listen<ThemeMode>(themeModeProvider, (_, _) {
      _bridge?.setTheme(_resolveTheme());
    });

    return InAppWebView(
      initialFile: 'assets/graph/index.html',
      initialSettings: InAppWebViewSettings(
        transparentBackground: true,
        supportZoom: false,
        disableHorizontalScroll: true,
        disableVerticalScroll: true,
        javaScriptEnabled: true,
      ),
      onWebViewCreated: (controller) {
        _bridge = GraphBridge(
          controller: controller,
          onNodeTapped: _onNodeTapped,
        );
      },
      onLoadStop: (controller, url) {
        _bridge?.setTheme(_resolveTheme());
        _loadSampleData();
      },
    );
  }
}
