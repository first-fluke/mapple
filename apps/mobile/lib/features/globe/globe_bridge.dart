import 'package:flutter_inappwebview/flutter_inappwebview.dart';

import 'package:mobile/features/globe/globe_focus_provider.dart';

class GlobeBridge {
  InAppWebViewController? _controller;
  bool _isReady = false;

  bool get isReady => _isReady;

  void attach(InAppWebViewController controller) {
    _controller = controller;
    _isReady = true;
  }

  void detach() {
    _controller = null;
    _isReady = false;
  }

  Future<void> flyTo(GlobeFocus focus) async {
    if (!_isReady || _controller == null) return;

    final args = StringBuffer('${focus.latitude}, ${focus.longitude}');
    if (focus.zoom != null) {
      args.write(', ${focus.zoom}');
    }

    await _controller!.evaluateJavascript(
      source: 'window.flyTo?.($args)',
    );
  }
}
