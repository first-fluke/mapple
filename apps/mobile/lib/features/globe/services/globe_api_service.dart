import 'package:dio/dio.dart';
import 'package:mobile/features/globe/models/globe_models.dart';

class GlobeApiService {
  final Dio _dio;

  GlobeApiService(this._dio);

  Future<GlobeData> fetchGlobeData({int limit = 200}) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/globe/data',
      queryParameters: {'limit': limit},
    );
    final data = response.data!['data'] as Map<String, dynamic>;
    return GlobeData.fromJson(data);
  }
}
