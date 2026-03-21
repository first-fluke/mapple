import 'dart:io';

import 'package:flutter/material.dart';
import 'package:forui/forui.dart';
import 'package:go_router/go_router.dart';

class AppShell extends StatelessWidget {
  final StatefulNavigationShell navigationShell;

  const AppShell({required this.navigationShell, super.key});

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
      footer: FBottomNavigationBar(
        index: navigationShell.currentIndex,
        onChange: (index) => navigationShell.goBranch(
          index,
          initialLocation: index == navigationShell.currentIndex,
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
