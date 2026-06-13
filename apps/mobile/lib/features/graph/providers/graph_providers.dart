import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/core/api/dio_client.dart';
import 'package:mobile/features/graph/models/graph_models.dart';
import 'package:mobile/features/graph/services/graph_api_service.dart';

final graphApiServiceProvider = Provider<GraphApiService>((ref) {
  return GraphApiService(ref.watch(dioProvider));
});

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

class GraphScreenState {
  final GraphEdgeType selectedType;
  final GraphData? data;
  final bool isLoading;
  final Object? error;

  const GraphScreenState({
    this.selectedType = GraphEdgeType.company,
    this.data,
    this.isLoading = false,
    this.error,
  });

  GraphScreenState copyWith({
    GraphEdgeType? selectedType,
    GraphData? data,
    bool? isLoading,
    Object? Function()? error,
  }) {
    return GraphScreenState(
      selectedType: selectedType ?? this.selectedType,
      data: data ?? this.data,
      isLoading: isLoading ?? this.isLoading,
      error: error != null ? error() : this.error,
    );
  }
}

// ---------------------------------------------------------------------------
// Notifier
// ---------------------------------------------------------------------------

final graphScreenProvider =
    NotifierProvider<GraphScreenNotifier, GraphScreenState>(
        GraphScreenNotifier.new);

class GraphScreenNotifier extends Notifier<GraphScreenState> {
  @override
  GraphScreenState build() {
    // Defer so state is initialized before the async method writes it.
    Future.microtask(() => _load(GraphEdgeType.company));
    return const GraphScreenState(isLoading: true);
  }

  Future<void> _load(GraphEdgeType type) async {
    state = state.copyWith(isLoading: true, error: () => null);
    try {
      final service = ref.read(graphApiServiceProvider);
      final data = await service.fetchGraphData(type);
      state = state.copyWith(
        data: data,
        isLoading: false,
        selectedType: type,
        error: () => null,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: () => e);
    }
  }

  Future<void> selectType(GraphEdgeType type) => _load(type);

  Future<void> refresh() => _load(state.selectedType);
}
