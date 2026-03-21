import 'package:flutter/widgets.dart';
import 'package:flutter_inappwebview/flutter_inappwebview.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/features/globe/globe_bridge.dart';
import 'package:mobile/features/globe/globe_focus_provider.dart';

class GlobeScreen extends ConsumerStatefulWidget {
  const GlobeScreen({super.key});

  @override
  ConsumerState<GlobeScreen> createState() => _GlobeScreenState();
}

class _GlobeScreenState extends ConsumerState<GlobeScreen> {
  final _bridge = GlobeBridge();

  @override
  void dispose() {
    _bridge.detach();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    ref.listen<GlobeFocus?>(globeFocusProvider, (_, next) {
      if (next != null) {
        _bridge.flyTo(next);
      }
    });

    return InAppWebView(
      initialData: InAppWebViewInitialData(data: _kShellHtml),
      initialSettings: InAppWebViewSettings(
        javaScriptEnabled: true,
        transparentBackground: true,
      ),
      onWebViewCreated: (controller) {
        _bridge.attach(controller);
      },
      onLoadStop: (controller, url) async {
        final focus = ref.read(globeFocusProvider);
        if (focus != null) {
          await _bridge.flyTo(focus);
        }
      },
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
