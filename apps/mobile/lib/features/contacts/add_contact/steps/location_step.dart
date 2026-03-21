import 'dart:convert';

import 'package:flutter/widgets.dart';
import 'package:flutter_inappwebview/flutter_inappwebview.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:forui/forui.dart';

import 'package:mobile/features/contacts/providers/add_contact_provider.dart';

const _mapHtml = '''
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, sans-serif; }
    #map {
      width: 100vw;
      height: 100vh;
      background: #f0f0f0;
      position: relative;
      overflow: hidden;
    }
    #map.dark { background: #1a1a1a; }
    #crosshair {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -100%);
      font-size: 32px;
      pointer-events: none;
      z-index: 10;
      filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
    }
    #grid {
      position: absolute;
      inset: 0;
      background-image:
        linear-gradient(rgba(128,128,128,0.15) 1px, transparent 1px),
        linear-gradient(90deg, rgba(128,128,128,0.15) 1px, transparent 1px);
      background-size: 50px 50px;
    }
    #coords {
      position: absolute;
      bottom: 16px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(0,0,0,0.7);
      color: white;
      padding: 8px 16px;
      border-radius: 20px;
      font-size: 13px;
      z-index: 10;
      white-space: nowrap;
    }
    #instructions {
      position: absolute;
      top: 16px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(0,0,0,0.7);
      color: white;
      padding: 8px 16px;
      border-radius: 20px;
      font-size: 13px;
      z-index: 10;
    }
  </style>
</head>
<body>
  <div id="map">
    <div id="grid"></div>
    <div id="crosshair">📍</div>
    <div id="instructions">Tap to place pin</div>
    <div id="coords">Lat: 37.5665, Lng: 126.9780</div>
  </div>
  <script>
    let lat = 37.5665;
    let lng = 126.9780;
    let offsetX = 0;
    let offsetY = 0;
    const scale = 0.0001;

    const crosshair = document.getElementById('crosshair');
    const coordsEl = document.getElementById('coords');
    const instructions = document.getElementById('instructions');
    const grid = document.getElementById('grid');

    function updateDisplay() {
      coordsEl.textContent = 'Lat: ' + lat.toFixed(4) + ', Lng: ' + lng.toFixed(4);
    }

    document.getElementById('map').addEventListener('click', function(e) {
      const rect = this.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      crosshair.style.left = x + 'px';
      crosshair.style.top = y + 'px';
      crosshair.style.transform = 'translate(-50%, -100%)';

      const dx = x - rect.width / 2;
      const dy = -(y - rect.height / 2);
      lng = 126.9780 + (offsetX + dx) * scale;
      lat = 37.5665 + (offsetY + dy) * scale;

      updateDisplay();
      instructions.style.display = 'none';

      window.flutter_inappwebview.callHandler('onPinPlaced', JSON.stringify({
        latitude: lat,
        longitude: lng
      }));
    });

    let isDragging = false;
    let startX, startY;

    document.getElementById('map').addEventListener('touchstart', function(e) {
      if (e.touches.length === 1) {
        isDragging = true;
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
      }
    });

    document.getElementById('map').addEventListener('touchmove', function(e) {
      if (isDragging && e.touches.length === 1) {
        e.preventDefault();
        const dx = e.touches[0].clientX - startX;
        const dy = e.touches[0].clientY - startY;
        grid.style.backgroundPosition = (offsetX + dx) + 'px ' + (offsetY + dy) + 'px';
      }
    }, { passive: false });

    document.getElementById('map').addEventListener('touchend', function(e) {
      isDragging = false;
    });

    updateDisplay();
  </script>
</body>
</html>
''';

class LocationStep extends ConsumerStatefulWidget {
  const LocationStep({super.key});

  @override
  ConsumerState<LocationStep> createState() => _LocationStepState();
}

class _LocationStepState extends ConsumerState<LocationStep> {
  late final TextEditingController _locationNameController;

  @override
  void initState() {
    super.initState();
    final state = ref.read(addContactProvider);
    _locationNameController =
        TextEditingController(text: state.locationName ?? '');
  }

  @override
  void dispose() {
    _locationNameController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = context.theme;
    final state = ref.watch(addContactProvider);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 4),
          child: Text(
            'Location',
            style: theme.typography.lg.copyWith(
              color: theme.colorScheme.foreground,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
          child: Text(
            'Tap on the map to place a pin where you met this contact',
            style: theme.typography.sm.copyWith(
              color: theme.colorScheme.mutedForeground,
            ),
          ),
        ),
        // Map WebView
        Expanded(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: InAppWebView(
                initialData: InAppWebViewInitialData(data: _mapHtml),
                initialSettings: InAppWebViewSettings(
                  javaScriptEnabled: true,
                  transparentBackground: true,
                  disableHorizontalScroll: false,
                  disableVerticalScroll: false,
                ),
                onWebViewCreated: (controller) {
                  controller.addJavaScriptHandler(
                    handlerName: 'onPinPlaced',
                    callback: (args) {
                      if (args.isNotEmpty) {
                        final data =
                            jsonDecode(args[0] as String) as Map<String, dynamic>;
                        final latitude = (data['latitude'] as num).toDouble();
                        final longitude = (data['longitude'] as num).toDouble();
                        ref.read(addContactProvider.notifier).setLocation(
                              latitude: latitude,
                              longitude: longitude,
                            );
                      }
                    },
                  );
                },
              ),
            ),
          ),
        ),
        const SizedBox(height: 12),
        // Location name field
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: FTextField(
            label: const Text('Location name'),
            hint: 'e.g. Seoul Office, Gangnam Cafe',
            controller: _locationNameController,
            onChange: (value) {
              ref.read(addContactProvider.notifier).setLocation(
                    latitude: state.latitude ?? 37.5665,
                    longitude: state.longitude ?? 126.9780,
                    locationName: value,
                  );
            },
          ),
        ),
        const SizedBox(height: 8),
        if (state.latitude != null)
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                FIcon(
                  FAssets.icons.mapPin,
                  size: 14,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(width: 4),
                Text(
                  'Pin: ${state.latitude!.toStringAsFixed(4)}, ${state.longitude!.toStringAsFixed(4)}',
                  style: theme.typography.xs.copyWith(
                    color: theme.colorScheme.mutedForeground,
                  ),
                ),
              ],
            ),
          ),
        const SizedBox(height: 8),
      ],
    );
  }
}
