import 'package:dio/dio.dart';

import 'package:mobile/features/contacts/models/contact.dart';

class ContactsApi {
  final Dio _dio;

  ContactsApi(this._dio);

  Future<({List<Contact> items, String? nextCursor, bool hasMore})> list({
    String? cursor,
    int perPage = 20,
    String? search,
    String sort = 'created_at_desc',
  }) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/contacts',
      queryParameters: {
        'cursor': ?cursor,
        'per_page': perPage,
        if (search != null && search.isNotEmpty) 'search': search,
        'sort': sort,
      },
    );

    final data = response.data!;
    final items = (data['data'] as List)
        .map((e) => Contact.fromJson(e as Map<String, dynamic>))
        .toList();
    final meta = data['meta'] as Map<String, dynamic>?;

    return (
      items: items,
      nextCursor: meta?['next_cursor'] as String?,
      hasMore: meta?['has_more'] as bool? ?? false,
    );
  }

  Future<Contact> create(Map<String, dynamic> payload) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/contacts',
      data: payload,
    );
    return Contact.fromJson(response.data!['data'] as Map<String, dynamic>);
  }

  Future<Contact> update(String id, Map<String, dynamic> payload) async {
    final response = await _dio.patch<Map<String, dynamic>>(
      '/contacts/$id',
      data: payload,
    );
    return Contact.fromJson(response.data!['data'] as Map<String, dynamic>);
  }

  /// Soft-delete — the API marks the record as deleted without removing it.
  Future<void> delete(String id) async {
    await _dio.delete<void>('/contacts/$id');
  }
}
