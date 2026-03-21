import 'package:flutter/material.dart';
import 'package:forui/forui.dart';
import 'package:go_router/go_router.dart';

class AppShell extends StatelessWidget {
  final StatefulNavigationShell navigationShell;

  const AppShell({required this.navigationShell, super.key});

  @override
  Widget build(BuildContext context) {
    return FScaffold(
      content: navigationShell,
      footer: FBottomNavigationBar(
        index: navigationShell.currentIndex,
        onChange: (index) => navigationShell.goBranch(
          index,
          initialLocation: index == navigationShell.currentIndex,
        ),
        children: [
          FBottomNavigationBarItem(
            icon: FIcon(FAssets.icons.globe),
            label: Semantics(
              label: 'Globe tab',
              child: const Text('Globe'),
            ),
          ),
          FBottomNavigationBarItem(
            icon: FIcon(FAssets.icons.chartLine),
            label: Semantics(
              label: 'Graph tab',
              child: const Text('Graph'),
            ),
          ),
          FBottomNavigationBarItem(
            icon: FIcon(FAssets.icons.users),
            label: Semantics(
              label: 'Contacts tab',
              child: const Text('Contacts'),
            ),
          ),
          FBottomNavigationBarItem(
            icon: FIcon(FAssets.icons.settings),
            label: Semantics(
              label: 'Settings tab',
              child: const Text('Settings'),
            ),
          ),
        ],
      ),
    );
  }
}
