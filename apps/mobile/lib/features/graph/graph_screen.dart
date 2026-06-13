import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:flutter_inappwebview/flutter_inappwebview.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:forui/forui.dart';

import 'package:mobile/features/globe/globe_focus_provider.dart';
import 'package:mobile/features/graph/graph_bridge.dart';
import 'package:mobile/features/graph/models/graph_models.dart';
import 'package:mobile/features/graph/profile_bottom_sheet.dart';
import 'package:mobile/features/graph/providers/graph_providers.dart';
import 'package:mobile/l10n/app_localizations.dart';
import 'package:mobile/shell/app_shell.dart';
import 'package:mobile/theme/theme_provider.dart';

class GraphScreen extends ConsumerStatefulWidget {
  const GraphScreen({super.key});

  @override
  ConsumerState<GraphScreen> createState() => _GraphScreenState();
}

class _GraphScreenState extends ConsumerState<GraphScreen> {
  GraphBridge? _bridge;

  @override
  void dispose() {
    _bridge = null;
    super.dispose();
  }

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

  void _pushGraphData(GraphData data) {
    final bridge = _bridge;
    if (bridge == null) return;

    // Build unique node IDs from edges and clusters.
    final nodeIds = <int>{};
    for (final e in data.edges) {
      nodeIds.add(e.sourceContactId);
      nodeIds.add(e.targetContactId);
    }
    for (final c in data.clusters) {
      nodeIds.addAll(c.contactIds);
    }

    // Use cluster labels for groups where available.
    final idToGroup = <int, String>{};
    for (final c in data.clusters) {
      for (final id in c.contactIds) {
        idToGroup[id] = c.label;
      }
    }

    final nodes = nodeIds.map((id) {
      return GraphNode(
        id: id.toString(),
        name: 'Contact $id',
        group: idToGroup[id],
      );
    }).toList();

    final edges = data.edges.asMap().entries.map((entry) {
      final i = entry.key;
      final e = entry.value;
      return GraphEdge(
        id: 'e$i',
        source: e.sourceContactId.toString(),
        target: e.targetContactId.toString(),
      );
    }).toList();

    bridge.setNodes(nodes);
    bridge.setEdges(edges);
  }

  @override
  Widget build(BuildContext context) {
    final graphState = ref.watch(graphScreenProvider);
    final theme = context.theme;

    // Re-push data when API data changes and bridge is ready.
    ref.listen<GraphScreenState>(graphScreenProvider, (_, next) {
      if (!next.isLoading && next.error == null && next.data != null) {
        _pushGraphData(next.data!);
      }
    });

    ref.listen<ThemeMode>(themeModeProvider, (_, next) {
      _bridge?.setTheme(_resolveTheme());
    });

    return Stack(
      children: [
        InAppWebView(
          initialSettings: InAppWebViewSettings(
            javaScriptEnabled: true,
            transparentBackground: true,
            supportZoom: false,
            disableHorizontalScroll: true,
            disableVerticalScroll: true,
            allowFileAccessFromFileURLs: true,
            allowUniversalAccessFromFileURLs: true,
          ),
          onWebViewCreated: (controller) async {
            _bridge = GraphBridge(
              controller: controller,
              onNodeTapped: _onNodeTapped,
              onReady: () {
                _bridge?.setTheme(_resolveTheme());
                final data = ref.read(graphScreenProvider).data;
                if (data != null) _pushGraphData(data);
              },
            );

            controller.addJavaScriptHandler(
              handlerName: 'onEntitySelected',
              callback: (args) {
                if (args.isEmpty) return;
                final data = args[0] as Map<String, dynamic>;
                final lat = (data['lat'] as num?)?.toDouble();
                final lng = (data['lng'] as num?)?.toDouble();
                if (lat == null || lng == null) return;

                ref.read(globeFocusProvider.notifier).set(GlobeFocus(
                      latitude: lat,
                      longitude: lng,
                      entityId: data['id'] as String?,
                    ));
                ref.read(navigationShellProvider)?.goBranch(0);
              },
            );

            final html =
                await rootBundle.loadString('assets/graph/index.html');
            await controller.loadData(
              data: html,
              mimeType: 'text/html',
              encoding: 'utf-8',
              baseUrl: WebUri('https://graph.local'),
            );
          },
          onLoadStop: (controller, url) {
            _bridge?.setTheme(_resolveTheme());
            final data = ref.read(graphScreenProvider).data;
            if (data != null) _pushGraphData(data);
          },
        ),

        // Edge type filter chips at top
        Positioned(
          top: 12,
          left: 12,
          right: 12,
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: GraphEdgeType.values.map((type) {
                final isSelected = graphState.selectedType == type;
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: GestureDetector(
                    onTap: () => ref
                        .read(graphScreenProvider.notifier)
                        .selectType(type),
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: isSelected
                            ? theme.colorScheme.primary
                            : theme.colorScheme.background
                                .withValues(alpha: 0.85),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(
                          color: isSelected
                              ? theme.colorScheme.primary
                              : theme.colorScheme.border,
                        ),
                      ),
                      child: Text(
                        type.name,
                        style: theme.typography.xs.copyWith(
                          color: isSelected
                              ? theme.colorScheme.primaryForeground
                              : theme.colorScheme.foreground,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
        ),

        // Loading overlay
        if (graphState.isLoading)
          Positioned.fill(
            child: ColoredBox(
              color:
                  theme.colorScheme.background.withValues(alpha: 0.7),
              child: const Center(child: CircularProgressIndicator.adaptive()),
            ),
          ),

        // Error overlay
        if (graphState.error != null && !graphState.isLoading)
          Positioned.fill(
            child: ColoredBox(
              color: theme.colorScheme.background,
              child: Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    FIcon(
                      FAssets.icons.triangleAlert,
                      size: 48,
                      color: theme.colorScheme.destructive,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      AppLocalizations.of(context)!.graphLoadError,
                      style: theme.typography.base.copyWith(
                        color: theme.colorScheme.foreground,
                      ),
                    ),
                    const SizedBox(height: 12),
                    GestureDetector(
                      onTap: () =>
                          ref.read(graphScreenProvider.notifier).refresh(),
                      child: Text(
                        AppLocalizations.of(context)!.contactsRetry,
                        style: theme.typography.sm.copyWith(
                          color: theme.colorScheme.primary,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),

        // Empty state (loaded but no edges)
        if (!graphState.isLoading &&
            graphState.error == null &&
            (graphState.data?.edges.isEmpty ?? false))
          Positioned.fill(
            child: ColoredBox(
              color: theme.colorScheme.background,
              child: Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    FIcon(
                      FAssets.icons.chartLine,
                      size: 48,
                      color: theme.colorScheme.mutedForeground,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      AppLocalizations.of(context)!.graphEmptyState,
                      style: theme.typography.base.copyWith(
                        color: theme.colorScheme.mutedForeground,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
      ],
    );
  }
}
