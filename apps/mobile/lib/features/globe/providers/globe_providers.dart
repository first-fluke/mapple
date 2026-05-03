import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/core/config.dart';
import 'package:mobile/features/globe/models/globe_models.dart';
import 'package:mobile/features/globe/services/globe_api_service.dart';
import 'package:mobile/features/globe/services/globe_bridge.dart';

final dioProvider = Provider<Dio>((ref) {
  return Dio(BaseOptions(
    baseUrl: AppConfig.apiBaseUrl,
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 10),
  ));
});

final globeApiServiceProvider = Provider<GlobeApiService>((ref) {
  return GlobeApiService(ref.watch(dioProvider));
});

final globeBridgeProvider = Provider<GlobeBridge>((ref) {
  return GlobeBridge();
});

final globeDataProvider = FutureProvider.family<GlobeData, int>((ref, limit) async {
  final service = ref.watch(globeApiServiceProvider);
  return service.fetchGlobeData(limit: limit);
});
