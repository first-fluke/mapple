import 'package:dio/dio.dart';

import 'package:mobile/features/graph/models/graph_models.dart';

class GraphApiService {
  final Dio _dio;

  GraphApiService(this._dio);

  Future<List<GraphApiEdge>> fetchEdges(GraphEdgeType type) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/graph/edges',
      queryParameters: {'type': type.name},
    );
    final data = response.data!['data'] as List;
    return data
        .map((e) => GraphApiEdge.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<List<GraphApiCluster>> fetchClusters(GraphEdgeType type) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/graph/clusters',
      queryParameters: {'type': type.name},
    );
    final data = response.data!['data'] as List;
    return data
        .map((e) => GraphApiCluster.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  /// Fetch edges and clusters for a given edge type in parallel.
  Future<GraphData> fetchGraphData(GraphEdgeType type) async {
    final results = await Future.wait([
      fetchEdges(type),
      fetchClusters(type),
    ]);
    return GraphData(
      edges: results[0] as List<GraphApiEdge>,
      clusters: results[1] as List<GraphApiCluster>,
    );
  }
}
