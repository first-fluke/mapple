import 'package:flutter_riverpod/flutter_riverpod.dart';

class GlobeFocus {
  final double latitude;
  final double longitude;
  final double? zoom;
  final String? entityId;

  const GlobeFocus({
    required this.latitude,
    required this.longitude,
    this.zoom,
    this.entityId,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is GlobeFocus &&
          latitude == other.latitude &&
          longitude == other.longitude &&
          zoom == other.zoom &&
          entityId == other.entityId;

  @override
  int get hashCode => Object.hash(latitude, longitude, zoom, entityId);
}

class GlobeFocusNotifier extends Notifier<GlobeFocus?> {
  @override
  GlobeFocus? build() => null;

  void set(GlobeFocus focus) => state = focus;

  void clear() => state = null;
}

final globeFocusProvider =
    NotifierProvider<GlobeFocusNotifier, GlobeFocus?>(GlobeFocusNotifier.new);
