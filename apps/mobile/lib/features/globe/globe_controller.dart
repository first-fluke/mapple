import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter_inappwebview/flutter_inappwebview.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/features/globe/globe_bridge.dart';

enum GlobeStatus { loading, ready, error }

class GlobeState {
  final GlobeStatus status;
  final String? errorMessage;

  const GlobeState({
    this.status = GlobeStatus.loading,
    this.errorMessage,
  });

  GlobeState copyWith({
    GlobeStatus? status,
    String? errorMessage,
  }) {
    return GlobeState(
      status: status ?? this.status,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }
}

class GlobeController extends Notifier<GlobeState> {
  InAppWebViewController? _webViewController;

  @override
  GlobeState build() => const GlobeState();

  void setWebViewController(InAppWebViewController controller) {
    _webViewController = controller;
    controller.addJavaScriptHandler(
      handlerName: 'onGlobeEvent',
      callback: _handleGlobeEvent,
    );
  }

  dynamic _handleGlobeEvent(List<dynamic> args) {
    if (args.isEmpty) return;
    final event = GlobeBridgeEvent.fromJson(args[0] as String);

    switch (event) {
      case GlobeReadyEvent():
        state = state.copyWith(status: GlobeStatus.ready);
      case GlobePointClickEvent():
        debugPrint('Globe point clicked: ${event.lat}, ${event.lng}');
      case GlobeUnknownEvent():
        debugPrint('Unknown globe event: ${event.type}');
    }
  }

  void onLoadError(String message) {
    state = state.copyWith(
      status: GlobeStatus.error,
      errorMessage: message,
    );
  }

  Future<void> sendCommand(GlobeBridgeCommand command) async {
    final controller = _webViewController;
    if (controller == null) return;

    await controller.evaluateJavascript(
      source: 'handleFlutterMessage(${jsonEncode(command.toJson())})',
    );
  }

  Future<void> setPoints(List<GlobePoint> points) async {
    await sendCommand(SetPointsCommand(points: points));
  }

  Future<void> setArcs(List<GlobeArc> arcs) async {
    await sendCommand(SetArcsCommand(arcs: arcs));
  }

  Future<void> focusPoint(
    double lat,
    double lng, {
    double altitude = 2.0,
  }) async {
    await sendCommand(
      FocusPointCommand(lat: lat, lng: lng, altitude: altitude),
    );
  }

  Future<void> setTheme(String theme) async {
    await sendCommand(SetThemeCommand(theme: theme));
  }

  Future<void> setAutoRotate({required bool enabled}) async {
    await sendCommand(SetAutoRotateCommand(enabled: enabled));
  }
}

final globeControllerProvider =
    NotifierProvider<GlobeController, GlobeState>(GlobeController.new);
