import 'dart:io' show Platform;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:flutter_inappwebview/flutter_inappwebview.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/features/globe/models/globe_models.dart';
import 'package:mobile/features/globe/providers/globe_providers.dart';
import 'package:mobile/features/globe/services/globe_bridge.dart';
import 'package:mobile/features/globe/widgets/contact_bottom_sheet.dart';
import 'package:mobile/theme/theme_provider.dart';

class GlobeScreen extends ConsumerStatefulWidget {
  const GlobeScreen({super.key});

  @override
  ConsumerState<GlobeScreen> createState() => _GlobeScreenState();
}

class _GlobeScreenState extends ConsumerState<GlobeScreen> {
  late final GlobeBridge _bridge;
  InAppWebViewController? _webViewController;
  bool _globeReady = false;
  List<GlobePin> _pins = [];

  /// iOS initial limit: 50 contacts, other platforms: 200.
  int get _contactLimit => Platform.isIOS ? 50 : 200;

  @override
  void initState() {
    super.initState();
    _bridge = ref.read(globeBridgeProvider);
    _bridge
      ..onReady = _onGlobeReady
      ..onPinTapped = _onPinTapped
      ..onClusterTapped = _onClusterTapped
      ..onLocationSelected = _onLocationSelected;
  }

  @override
  void dispose() {
    _bridge.detach();
    super.dispose();
  }

  void _onGlobeReady(String version) {
    setState(() => _globeReady = true);
    _syncTheme();
    _loadGlobeData();
  }

  void _onPinTapped(String contactId, double lat, double lng) {
    final name = _pins
        .cast<GlobePin?>()
        .firstWhere((p) => p!.id == contactId, orElse: () => null)
        ?.name;

    ContactBottomSheet.show(
      context,
      contactId: contactId,
      contactName: name,
      lat: lat,
      lng: lng,
    );
  }

  void _onClusterTapped(
      List<String> contactIds, double lat, double lng, int count) {
    _bridge.flyTo(lat: lat, lng: lng, altitude: 1.5, durationMs: 800);
  }

  void _onLocationSelected(double lat, double lng) {
    // Reserved for future use (select_location mode).
  }

  void _syncTheme() {
    final themeMode = ref.read(themeModeProvider);
    final brightness = switch (themeMode) {
      ThemeMode.dark => Brightness.dark,
      ThemeMode.light => Brightness.light,
      ThemeMode.system =>
        WidgetsBinding.instance.platformDispatcher.platformBrightness,
    };
    _bridge.setTheme(brightness == Brightness.dark ? 'dark' : 'light');
  }

  Future<void> _loadGlobeData() async {
    final data =
        await ref.read(globeDataProvider(_contactLimit).future);
    _pins = data.pins;
    await _bridge.setPins(data.pins);
    if (data.arcs.isNotEmpty) {
      await _bridge.setArcs(data.arcs);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        InAppWebView(
          initialSettings: InAppWebViewSettings(
            transparentBackground: true,
            javaScriptEnabled: true,
            allowFileAccessFromFileURLs: true,
            allowUniversalAccessFromFileURLs: true,
            useWideViewPort: false,
            supportZoom: false,
            disableHorizontalScroll: true,
            disableVerticalScroll: true,
          ),
          onWebViewCreated: (controller) async {
            _webViewController = controller;
            _bridge.attach(controller);

            controller.addJavaScriptHandler(
              handlerName: 'GlobeBridgeChannel',
              callback: (args) {
                if (args.isNotEmpty) {
                  _bridge.handleMessage(args[0] as String);
                }
              },
            );

            final html = await rootBundle.loadString(
              'assets/globe/index.html',
            );
            await controller.loadData(
              data: html,
              mimeType: 'text/html',
              encoding: 'utf-8',
              baseUrl: WebUri('https://globe.local'),
            );
          },
        ),
        if (!_globeReady)
          const Center(
            child: CircularProgressIndicator.adaptive(),
          ),
      ],
    );
  }
}
