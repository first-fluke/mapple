import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:forui/forui.dart';
import 'package:go_router/go_router.dart';

import 'package:mobile/l10n/app_localizations.dart';

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
    final l10n = AppLocalizations.of(context)!;

    return FScaffold(
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
            label: Semantics(
              label: l10n.navGlobeSemantics,
              child: Text(l10n.navGlobe),
            ),
          ),
          FBottomNavigationBarItem(
            icon: FIcon(FAssets.icons.chartLine),
            label: Semantics(
              label: l10n.navGraphSemantics,
              child: Text(l10n.navGraph),
            ),
          ),
          FBottomNavigationBarItem(
            icon: FIcon(FAssets.icons.users),
            label: Semantics(
              label: l10n.navContactsSemantics,
              child: Text(l10n.navContacts),
            ),
          ),
          FBottomNavigationBarItem(
            icon: FIcon(FAssets.icons.settings),
            label: Semantics(
              label: l10n.navSettingsSemantics,
              child: Text(l10n.navSettings),
            ),
          ),
        ],
      ),
    );
  }
}
