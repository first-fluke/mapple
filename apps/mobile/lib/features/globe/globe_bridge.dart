import 'dart:convert';

/// Commands sent from Flutter to the Globe.gl WebView via JS bridge.
sealed class GlobeBridgeCommand {
  String get type;
  Map<String, dynamic> get payload;

  String toJson() => jsonEncode({'type': type, 'payload': payload});
}

class SetPointsCommand extends GlobeBridgeCommand {
  final List<GlobePoint> points;

  SetPointsCommand({required this.points});

  @override
  String get type => 'setPoints';

  @override
  Map<String, dynamic> get payload => {
        'points': points.map((p) => p.toMap()).toList(),
      };
}

class SetArcsCommand extends GlobeBridgeCommand {
  final List<GlobeArc> arcs;

  SetArcsCommand({required this.arcs});

  @override
  String get type => 'setArcs';

  @override
  Map<String, dynamic> get payload => {
        'arcs': arcs.map((a) => a.toMap()).toList(),
      };
}

class FocusPointCommand extends GlobeBridgeCommand {
  final double lat;
  final double lng;
  final double altitude;

  FocusPointCommand({
    required this.lat,
    required this.lng,
    this.altitude = 2.0,
  });

  @override
  String get type => 'focusPoint';

  @override
  Map<String, dynamic> get payload => {
        'lat': lat,
        'lng': lng,
        'altitude': altitude,
      };
}

class SetThemeCommand extends GlobeBridgeCommand {
  final String theme;

  SetThemeCommand({required this.theme});

  @override
  String get type => 'setTheme';

  @override
  Map<String, dynamic> get payload => {'theme': theme};
}

class SetAutoRotateCommand extends GlobeBridgeCommand {
  final bool enabled;

  SetAutoRotateCommand({required this.enabled});

  @override
  String get type => 'setAutoRotate';

  @override
  Map<String, dynamic> get payload => {'enabled': enabled};
}

/// Events received from the Globe.gl WebView via JS bridge.
sealed class GlobeBridgeEvent {
  factory GlobeBridgeEvent.fromJson(String json) {
    final map = jsonDecode(json) as Map<String, dynamic>;
    final type = map['type'] as String;
    final payload = map['payload'] as Map<String, dynamic>? ?? {};

    return switch (type) {
      'ready' => GlobeReadyEvent(),
      'pointClick' => GlobePointClickEvent(
          lat: (payload['lat'] as num).toDouble(),
          lng: (payload['lng'] as num).toDouble(),
          id: payload['id'] as String?,
        ),
      _ => GlobeUnknownEvent(type: type, payload: payload),
    };
  }
}

class GlobeReadyEvent implements GlobeBridgeEvent {}

class GlobePointClickEvent implements GlobeBridgeEvent {
  final double lat;
  final double lng;
  final String? id;

  GlobePointClickEvent({
    required this.lat,
    required this.lng,
    this.id,
  });
}

class GlobeUnknownEvent implements GlobeBridgeEvent {
  final String type;
  final Map<String, dynamic> payload;

  GlobeUnknownEvent({required this.type, required this.payload});
}

/// A point on the globe.
class GlobePoint {
  final String? id;
  final double lat;
  final double lng;
  final double altitude;
  final double radius;
  final String? label;

  const GlobePoint({
    this.id,
    required this.lat,
    required this.lng,
    this.altitude = 0.01,
    this.radius = 0.5,
    this.label,
  });

  Map<String, dynamic> toMap() => {
        if (id != null) 'id': id,
        'lat': lat,
        'lng': lng,
        'altitude': altitude,
        'radius': radius,
        if (label != null) 'label': label,
      };
}

/// An arc connecting two points on the globe.
class GlobeArc {
  final double startLat;
  final double startLng;
  final double endLat;
  final double endLng;
  final List<String>? color;

  const GlobeArc({
    required this.startLat,
    required this.startLng,
    required this.endLat,
    required this.endLng,
    this.color,
  });

  Map<String, dynamic> toMap() => {
        'startLat': startLat,
        'startLng': startLng,
        'endLat': endLat,
        'endLng': endLng,
        if (color != null) 'color': color,
      };
}
