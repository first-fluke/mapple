import 'package:flutter/widgets.dart';
import 'package:flutter_inappwebview/flutter_inappwebview.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/features/globe/globe_focus_provider.dart';
import 'package:mobile/shell/app_shell.dart';

class GraphScreen extends ConsumerStatefulWidget {
  const GraphScreen({super.key});

  @override
  ConsumerState<GraphScreen> createState() => _GraphScreenState();
}

class _GraphScreenState extends ConsumerState<GraphScreen> {
  @override
  Widget build(BuildContext context) {
    return InAppWebView(
      initialData: InAppWebViewInitialData(data: _kShellHtml),
      initialSettings: InAppWebViewSettings(
        javaScriptEnabled: true,
        transparentBackground: true,
      ),
      onWebViewCreated: (controller) {
        controller.addJavaScriptHandler(
          handlerName: 'onEntitySelected',
          callback: (args) {
            final data = args[0] as Map<String, dynamic>;
            final lat = (data['lat'] as num).toDouble();
            final lng = (data['lng'] as num).toDouble();

            ref.read(globeFocusProvider.notifier).set(GlobeFocus(
              latitude: lat,
              longitude: lng,
              entityId: data['id'] as String?,
            ));

            // Switch to Globe tab via StatefulShellRoute.goBranch
            ref.read(navigationShellProvider)?.goBranch(0);
          },
        );
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
  function selectEntity(id, lat, lng) {
    window.flutter_inappwebview.callHandler('onEntitySelected', {id, lat, lng});
  }
</script>
</body>
</html>
''';
