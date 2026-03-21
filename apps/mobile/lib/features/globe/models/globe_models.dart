/// Pin data representing a contact on the globe.
class GlobePin {
  final String id;
  final String name;
  final String avatarUrl;
  final double lat;
  final double lng;

  const GlobePin({
    required this.id,
    required this.name,
    required this.avatarUrl,
    required this.lat,
    required this.lng,
  });

  factory GlobePin.fromJson(Map<String, dynamic> json) => GlobePin(
        id: json['id'] as String,
        name: json['name'] as String,
        avatarUrl: json['avatar_url'] as String? ?? json['avatarUrl'] as String? ?? '',
        lat: (json['lat'] as num).toDouble(),
        lng: (json['lng'] as num).toDouble(),
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'avatarUrl': avatarUrl,
        'lat': lat,
        'lng': lng,
      };
}

/// Arc data representing a connection between two locations.
class GlobeArc {
  final String id;
  final double startLat;
  final double startLng;
  final double endLat;
  final double endLng;
  final String type;
  final int frequency;

  const GlobeArc({
    required this.id,
    required this.startLat,
    required this.startLng,
    required this.endLat,
    required this.endLng,
    required this.type,
    required this.frequency,
  });

  factory GlobeArc.fromJson(Map<String, dynamic> json) => GlobeArc(
        id: json['id'] as String,
        startLat: (json['start_lat'] as num? ?? json['startLat'] as num).toDouble(),
        startLng: (json['start_lng'] as num? ?? json['startLng'] as num).toDouble(),
        endLat: (json['end_lat'] as num? ?? json['endLat'] as num).toDouble(),
        endLng: (json['end_lng'] as num? ?? json['endLng'] as num).toDouble(),
        type: json['type'] as String,
        frequency: json['frequency'] as int,
      );

  Map<String, dynamic> toJson() => {
        'startLat': startLat,
        'startLng': startLng,
        'endLat': endLat,
        'endLng': endLng,
        'type': type,
        'frequency': frequency,
      };
}

/// Response from GET /globe/data.
class GlobeData {
  final List<GlobePin> pins;
  final List<GlobeArc> arcs;

  const GlobeData({required this.pins, required this.arcs});

  factory GlobeData.fromJson(Map<String, dynamic> json) => GlobeData(
        pins: (json['pins'] as List)
            .map((e) => GlobePin.fromJson(e as Map<String, dynamic>))
            .toList(),
        arcs: (json['arcs'] as List)
            .map((e) => GlobeArc.fromJson(e as Map<String, dynamic>))
            .toList(),
      );
}
