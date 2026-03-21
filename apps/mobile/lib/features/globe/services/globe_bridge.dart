import 'dart:convert';

import 'package:flutter_inappwebview/flutter_inappwebview.dart';

import 'package:mobile/features/globe/models/globe_models.dart';

typedef OnPinTapped = void Function(String contactId, double lat, double lng);
typedef OnClusterTapped = void Function(
    List<String> contactIds, double lat, double lng, int count);
typedef OnLocationSelected = void Function(double lat, double lng);
typedef OnGlobeReady = void Function(String version);

class GlobeBridge {
  InAppWebViewController? _controller;

  OnGlobeReady? onReady;
  OnPinTapped? onPinTapped;
  OnClusterTapped? onClusterTapped;
  OnLocationSelected? onLocationSelected;

  void attach(InAppWebViewController controller) {
    _controller = controller;
  }

  void detach() {
    _controller = null;
  }

  /// Handle messages coming from the globe JS.
  void handleMessage(String rawMessage) {
    final msg = jsonDecode(rawMessage) as Map<String, dynamic>;
    final type = msg['type'] as String?;
    final payload = msg['payload'] as Map<String, dynamic>? ?? {};

    switch (type) {
      case 'READY':
        onReady?.call(payload['version'] as String? ?? '');
      case 'PIN_TAPPED':
        onPinTapped?.call(
          payload['contactId'] as String,
          (payload['lat'] as num).toDouble(),
          (payload['lng'] as num).toDouble(),
        );
      case 'CLUSTER_TAPPED':
        onClusterTapped?.call(
          (payload['contactIds'] as List).cast<String>(),
          (payload['lat'] as num).toDouble(),
          (payload['lng'] as num).toDouble(),
          payload['count'] as int,
        );
      case 'LOCATION_SELECTED':
        onLocationSelected?.call(
          (payload['lat'] as num).toDouble(),
          (payload['lng'] as num).toDouble(),
        );
    }
  }

  /// Send a message to the globe JS.
  Future<void> _send(Map<String, dynamic> message) async {
    final json = jsonEncode(message);
    await _controller?.evaluateJavascript(
      source: 'window.GlobeBridge.receive($json);',
    );
  }

  Future<void> setPins(List<GlobePin> pins) => _send({
        'type': 'SET_PINS',
        'payload': {'pins': pins.map((p) => p.toJson()).toList()},
      });

  Future<void> setArcs(List<GlobeArc> arcs) => _send({
        'type': 'SET_ARCS',
        'payload': {'arcs': arcs.map((a) => a.toJson()).toList()},
      });

  Future<void> setTheme(String theme) => _send({
        'type': 'SET_THEME',
        'payload': {'theme': theme},
      });

  Future<void> flyTo({
    required double lat,
    required double lng,
    double? altitude,
    int? durationMs,
  }) =>
      _send({
        'type': 'FLY_TO',
        'payload': {
          'lat': lat,
          'lng': lng,
          if (altitude != null) 'altitude': altitude,
          if (durationMs != null) 'durationMs': durationMs,
        },
      });

  Future<void> highlightContact(String contactId) => _send({
        'type': 'HIGHLIGHT_CONTACT',
        'payload': {'contactId': contactId},
      });

  Future<void> setMode(String mode) => _send({
        'type': 'SET_MODE',
        'payload': {'mode': mode},
      });
}
