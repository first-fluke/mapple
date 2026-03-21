import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:forui/forui.dart';
import 'package:go_router/go_router.dart';

class NavigationShellNotifier extends Notifier<StatefulNavigationShell?> {
  @override
  StatefulNavigationShell? build() => null;

  void set(StatefulNavigationShell shell) => state = shell;
}

final navigationShellProvider =
    NotifierProvider<NavigationShellNotifier, StatefulNavigationShell?>(
  NavigationShellNotifier.new,
);

class AppShell extends ConsumerStatefulWidget {
  final StatefulNavigationShell navigationShell;

  const AppShell({required this.navigationShell, super.key});

  @override
  ConsumerState<AppShell> createState() => _AppShellState();
}

class _AppShellState extends ConsumerState<AppShell> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(navigationShellProvider.notifier).set(widget.navigationShell);
    });
  }

  @override
  void didUpdateWidget(AppShell oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.navigationShell != widget.navigationShell) {
      ref.read(navigationShellProvider.notifier).set(widget.navigationShell);
    }
  }

  @override
  Widget build(BuildContext context) {
    return FScaffold(
      content: Stack(
        children: [
          navigationShell,
          Positioned(
            top: Platform.isIOS ? 16 : null,
            bottom: Platform.isAndroid ? 16 : null,
            right: 16,
            child: FloatingActionButton(
              onPressed: () {},
              child: const Icon(Icons.add),
            ),
          ),
        ],
      ),
      content: widget.navigationShell,
      footer: FBottomNavigationBar(
        index: widget.navigationShell.currentIndex,
        onChange: (index) => widget.navigationShell.goBranch(
          index,
          initialLocation: index == widget.navigationShell.currentIndex,
        ),
        children: [
          FBottomNavigationBarItem(
            icon: FIcon(FAssets.icons.globe),
            label: const Text('Globe'),
          ),
          FBottomNavigationBarItem(
            icon: FIcon(FAssets.icons.chartLine),
            label: const Text('Graph'),
          ),
          FBottomNavigationBarItem(
            icon: FIcon(FAssets.icons.users),
            label: const Text('Contacts'),
          ),
          FBottomNavigationBarItem(
            icon: FIcon(FAssets.icons.settings),
            label: const Text('Settings'),
          ),
        ],
      ),
    );
  }
}
