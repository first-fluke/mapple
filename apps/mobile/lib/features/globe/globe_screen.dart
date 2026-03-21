import 'package:flutter/foundation.dart';
import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter_inappwebview/flutter_inappwebview.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:forui/forui.dart';

import 'package:mobile/features/globe/globe_controller.dart';

class GlobeScreen extends ConsumerWidget {
  const GlobeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final globeState = ref.watch(globeControllerProvider);
    final controller = ref.read(globeControllerProvider.notifier);
    final theme = context.theme;

    return PopScope(
      canPop: false,
      child: Stack(
        children: [
          InAppWebView(
            initialFile: 'assets/globe/index.html',
            initialSettings: InAppWebViewSettings(
              transparentBackground: true,
              javaScriptEnabled: true,
              mediaPlaybackRequiresUserGesture: false,
              allowsInlineMediaPlayback: true,
              supportZoom: false,
              useHybridComposition: true,
              hardwareAcceleration: true,
            ),
            gestureRecognizers: {
              Factory<OneSequenceGestureRecognizer>(
                EagerGestureRecognizer.new,
              ),
            },
            onWebViewCreated: (webViewController) {
              controller.setWebViewController(webViewController);
            },
            onLoadStop: (webViewController, url) async {
              final brightness = Theme.of(context).brightness;
              await controller.setTheme(
                brightness == Brightness.dark ? 'dark' : 'light',
              );
            },
            onReceivedError: (webViewController, request, error) {
              controller.onLoadError(error.description);
            },
          ),
          if (globeState.status == GlobeStatus.loading)
            Positioned.fill(
              child: ColoredBox(
                color: theme.colorScheme.background,
                child: Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const CircularProgressIndicator.adaptive(),
                      const SizedBox(height: 16),
                      Text(
                        'Loading Globe...',
                        style: theme.typography.base.copyWith(
                          color: theme.colorScheme.mutedForeground,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          if (globeState.status == GlobeStatus.error)
            Positioned.fill(
              child: ColoredBox(
                color: theme.colorScheme.background,
                child: Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      FIcon(
                        FAssets.icons.triangleAlert,
                        color: theme.colorScheme.destructive,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        globeState.errorMessage ?? 'Failed to load globe',
                        style: theme.typography.base.copyWith(
                          color: theme.colorScheme.mutedForeground,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
