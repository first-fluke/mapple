import 'dart:convert';
import 'dart:ui' show VoidCallback;

import 'package:flutter_inappwebview/flutter_inappwebview.dart';

class GraphNode {
  final String id;
  final String name;
  final String? avatarUrl;
  final String? group;

  const GraphNode({
    required this.id,
    required this.name,
    this.avatarUrl,
    this.group,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        if (avatarUrl != null) 'avatarUrl': avatarUrl,
        if (group != null) 'group': group,
      };
}

class GraphEdge {
  final String id;
  final String source;
  final String target;

  const GraphEdge({
    required this.id,
    required this.source,
    required this.target,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'source': source,
        'target': target,
      };
}

typedef NodeTappedCallback = void Function({
  required String nodeId,
  required String name,
  String? group,
  String? avatarUrl,
});

class GraphBridge {
  final InAppWebViewController controller;
  final NodeTappedCallback? onNodeTapped;
  final VoidCallback? onReady;

  GraphBridge({
    required this.controller,
    this.onNodeTapped,
    this.onReady,
  }) {
    controller.addJavaScriptHandler(
      handlerName: 'onGraphMessage',
      callback: _handleMessage,
    );
  }

  void _handleMessage(List<dynamic> args) {
    if (args.isEmpty) return;
    final msg = jsonDecode(args[0] as String) as Map<String, dynamic>;
    final type = msg['type'] as String?;

    switch (type) {
      case 'NODE_TAPPED':
        final payload = msg['payload'] as Map<String, dynamic>;
        onNodeTapped?.call(
          nodeId: payload['nodeId'] as String,
          name: payload['name'] as String,
          group: payload['group'] as String?,
          avatarUrl: payload['avatarUrl'] as String?,
        );
      case 'READY':
        onReady?.call();
    }
  }

  Future<void> setNodes(List<GraphNode> nodes) => _send({
        'type': 'SET_NODES',
        'payload': {
          'nodes': nodes.map((n) => n.toJson()).toList(),
        },
      });

  Future<void> setEdges(List<GraphEdge> edges) => _send({
        'type': 'SET_EDGES',
        'payload': {
          'edges': edges.map((e) => e.toJson()).toList(),
        },
      });

  Future<void> setTheme(String theme) => _send({
        'type': 'SET_THEME',
        'payload': {'theme': theme},
      });

  Future<void> highlightNode(String nodeId) => _send({
        'type': 'HIGHLIGHT_NODE',
        'payload': {'nodeId': nodeId},
      });

  Future<void> _send(Map<String, dynamic> message) async {
    final json = jsonEncode(message);
    await controller.evaluateJavascript(
      source: 'window.graphBridge.receive($json)',
    );
  }
}

