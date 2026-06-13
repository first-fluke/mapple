/// Edge types matching the API EdgeType enum.
enum GraphEdgeType {
  company,
  school,
  tag,
  region,
  meeting;

  static GraphEdgeType fromString(String value) {
    return GraphEdgeType.values.firstWhere(
      (e) => e.name == value,
      orElse: () => GraphEdgeType.tag,
    );
  }
}

/// Matches EdgeOut from the API.
class GraphApiEdge {
  final int sourceContactId;
  final int targetContactId;
  final GraphEdgeType type;
  final String label;

  const GraphApiEdge({
    required this.sourceContactId,
    required this.targetContactId,
    required this.type,
    required this.label,
  });

  factory GraphApiEdge.fromJson(Map<String, dynamic> json) => GraphApiEdge(
        sourceContactId: json['source_contact_id'] as int,
        targetContactId: json['target_contact_id'] as int,
        type: GraphEdgeType.fromString(json['type'] as String),
        label: json['label'] as String,
      );
}

/// Matches ClusterOut from the API.
class GraphApiCluster {
  final int id;
  final GraphEdgeType type;
  final String label;
  final List<int> contactIds;

  const GraphApiCluster({
    required this.id,
    required this.type,
    required this.label,
    required this.contactIds,
  });

  factory GraphApiCluster.fromJson(Map<String, dynamic> json) =>
      GraphApiCluster(
        id: json['id'] as int,
        type: GraphEdgeType.fromString(json['type'] as String),
        label: json['label'] as String,
        contactIds: (json['contact_ids'] as List).cast<int>(),
      );
}

/// Aggregated graph data ready for the bridge.
class GraphData {
  final List<GraphApiEdge> edges;
  final List<GraphApiCluster> clusters;

  const GraphData({required this.edges, required this.clusters});

  static const empty = GraphData(edges: [], clusters: []);
}
