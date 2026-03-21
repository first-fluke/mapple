import 'package:flutter/material.dart';
import 'package:flutter_inappwebview/flutter_inappwebview.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:forui/forui.dart';

import 'package:mobile/features/contacts/contacts_provider.dart';
import 'package:mobile/models/contact.dart';
import 'package:mobile/services/js_bridge_service.dart';

class GlobeScreen extends ConsumerWidget {
  const GlobeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isAccessible = MediaQuery.of(context).accessibleNavigation;
    final contacts = ref.watch(contactsProvider);

    if (isAccessible) {
      return _GlobeFallbackList(contacts: contacts);
    }

    return _GlobeWebView(ref: ref);
  }
}

class _GlobeFallbackList extends StatelessWidget {
  final List<Contact> contacts;

  const _GlobeFallbackList({required this.contacts});

  @override
  Widget build(BuildContext context) {
    final theme = context.theme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: Semantics(
            header: true,
            child: Text(
              'Contacts',
              style: theme.typography.xl2.copyWith(
                color: theme.colorScheme.foreground,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
        Expanded(
          child: ListView.builder(
            itemCount: contacts.length,
            itemBuilder: (context, index) {
              final contact = contacts[index];
              return Semantics(
                label: contact.name,
                hint: contact.email ?? contact.phone ?? '',
                child: FTile(
                  prefixIcon: FIcon(FAssets.icons.user),
                  title: Text(contact.name),
                  subtitle: Text(contact.email ?? contact.phone ?? ''),
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}

class _GlobeWebView extends StatelessWidget {
  final WidgetRef ref;

  const _GlobeWebView({required this.ref});

  @override
  Widget build(BuildContext context) {
    return InAppWebView(
      initialSettings: InAppWebViewSettings(
        transparentBackground: true,
        javaScriptEnabled: true,
      ),
      onWebViewCreated: (controller) {
        JsBridgeService.registerHandlers(controller, ref);
      },
      onReceivedError: (controller, request, error) {
        // WebView request error — fallback handled by parent
      },
import 'package:flutter/widgets.dart';
import 'package:mobile/features/globe/globe_bridge.dart';
import 'package:mobile/features/globe/globe_focus_provider.dart';
import 'dart:io' show Platform;
import 'package:flutter/services.dart' show rootBundle;
import 'package:mobile/features/globe/models/globe_models.dart';
import 'package:mobile/features/globe/providers/globe_providers.dart';
import 'package:mobile/features/globe/services/globe_bridge.dart';
import 'package:mobile/features/globe/widgets/contact_bottom_sheet.dart';
import 'package:mobile/theme/theme_provider.dart';
class GlobeScreen extends ConsumerStatefulWidget {
  ConsumerState<GlobeScreen> createState() => _GlobeScreenState();
class _GlobeScreenState extends ConsumerState<GlobeScreen> {
  final _bridge = GlobeBridge();
  late final GlobeBridge _bridge;
  InAppWebViewController? _webViewController;
  bool _globeReady = false;
  List<GlobePin> _pins = [];
  /// iOS initial limit: 50 contacts, other platforms: 200.
  int get _contactLimit => Platform.isIOS ? 50 : 200;
  void initState() {
    super.initState();
    _bridge = ref.read(globeBridgeProvider);
    _bridge
      ..onReady = _onGlobeReady
      ..onPinTapped = _onPinTapped
      ..onClusterTapped = _onClusterTapped
      ..onLocationSelected = _onLocationSelected;
  void dispose() {
    _bridge.detach();
    super.dispose();
    ref.listen<GlobeFocus?>(globeFocusProvider, (_, next) {
      if (next != null) {
        _bridge.flyTo(next);
      }
    });
      initialData: InAppWebViewInitialData(data: _kShellHtml),
        _bridge.attach(controller);
      onLoadStop: (controller, url) async {
        final focus = ref.read(globeFocusProvider);
        if (focus != null) {
          await _bridge.flyTo(focus);
        }
  void _onGlobeReady(String version) {
    setState(() => _globeReady = true);
    _syncTheme();
    _loadGlobeData();
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
  void _onClusterTapped(
      List<String> contactIds, double lat, double lng, int count) {
    _bridge.flyTo(lat: lat, lng: lng, altitude: 1.5, durationMs: 800);
  void _onLocationSelected(double lat, double lng) {
    // Reserved for future use (select_location mode).
  void _syncTheme() {
    final themeMode = ref.read(themeModeProvider);
    final brightness = switch (themeMode) {
      ThemeMode.dark => Brightness.dark,
      ThemeMode.light => Brightness.light,
      ThemeMode.system =>
        WidgetsBinding.instance.platformDispatcher.platformBrightness,
    };
    _bridge.setTheme(brightness == Brightness.dark ? 'dark' : 'light');
  Future<void> _loadGlobeData() async {
    final data =
        await ref.read(globeDataProvider(_contactLimit).future);
    _pins = data.pins;
    await _bridge.setPins(data.pins);
    if (data.arcs.isNotEmpty) {
      await _bridge.setArcs(data.arcs);
    return Stack(
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
            await controller.loadData(
              data: html,
              mimeType: 'text/html',
              encoding: 'utf-8',
              baseUrl: WebUri('https://globe.local'),
          },
        if (!_globeReady)
          const Center(
            child: CircularProgressIndicator.adaptive(),
    );
  }
}

const _kShellHtml = '''
<!DOCTYPE html>
<html>
<head><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body>
<script>
  window.flyTo = function(lat, lng, zoom) {
    // Bridge target — replaced by CesiumJS / MapLibre in production
    console.log('flyTo', lat, lng, zoom);
  };
</script>
</body>
</html>
''';
