import 'package:flutter/foundation.dart';

enum SocialPlatform {
  linkedin,
  twitter,
  instagram,
  facebook,
  github,
  website,
}

@immutable
class SocialLink {
  final SocialPlatform platform;
  final String url;

  const SocialLink({required this.platform, required this.url});

  SocialLink copyWith({SocialPlatform? platform, String? url}) {
    return SocialLink(
      platform: platform ?? this.platform,
      url: url ?? this.url,
    );
  }

  Map<String, dynamic> toJson() => {
        'platform': platform.name,
        'url': url,
      };

  factory SocialLink.fromJson(Map<String, dynamic> json) {
    return SocialLink(
      platform: SocialPlatform.values.firstWhere(
        (p) => p.name == json['platform'],
        orElse: () => SocialPlatform.website,
      ),
      url: json['url'] as String,
    );
  }
}

enum TimelineEventType {
  meeting,
  call,
  email,
  note,
}

@immutable
class TimelineEvent {
  final String id;
  final String title;
  final String? description;
  final DateTime date;
  final TimelineEventType type;

  const TimelineEvent({
    required this.id,
    required this.title,
    this.description,
    required this.date,
    required this.type,
  });
}

@immutable
class Meeting {
  final String id;
  final String title;
  final String? description;
  final DateTime date;
  final String? location;

  const Meeting({
    required this.id,
    required this.title,
    this.description,
    required this.date,
    this.location,
  });
}

@immutable
class Contact {
  final String id;
  final int? userId;
  final String name;
  final String? email;
  final String? phone;
  final String? company;
  final String? jobTitle;
  final String? avatarUrl;
  final String? memo;
  final List<SocialLink> socialLinks;
  final List<String> tags;
  final List<TimelineEvent> timeline;
  final List<Meeting> meetings;
  final double? latitude;
  final double? longitude;
  final String? locationName;
  final DateTime createdAt;
  final DateTime updatedAt;

  const Contact({
    required this.id,
    this.userId,
    required this.name,
    this.email,
    this.phone,
    this.company,
    this.jobTitle,
    this.avatarUrl,
    this.memo,
    this.socialLinks = const [],
    this.tags = const [],
    this.timeline = const [],
    this.meetings = const [],
    this.latitude,
    this.longitude,
    this.locationName,
    required this.createdAt,
    required this.updatedAt,
  });

  Contact copyWith({
    String? id,
    int? userId,
    String? name,
    String? email,
    String? phone,
    String? company,
    String? jobTitle,
    String? avatarUrl,
    String? memo,
    List<SocialLink>? socialLinks,
    List<String>? tags,
    List<TimelineEvent>? timeline,
    List<Meeting>? meetings,
    double? latitude,
    double? longitude,
    String? locationName,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Contact(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      name: name ?? this.name,
      email: email ?? this.email,
      phone: phone ?? this.phone,
      company: company ?? this.company,
      jobTitle: jobTitle ?? this.jobTitle,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      memo: memo ?? this.memo,
      socialLinks: socialLinks ?? this.socialLinks,
      tags: tags ?? this.tags,
      timeline: timeline ?? this.timeline,
      meetings: meetings ?? this.meetings,
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      locationName: locationName ?? this.locationName,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  String get initials {
    final parts = name.trim().split(RegExp(r'\s+'));
    if (parts.length >= 2) {
      return '${parts.first[0]}${parts.last[0]}'.toUpperCase();
    }
    return name.isNotEmpty ? name[0].toUpperCase() : '?';
  }

  /// Serialise for POST /contacts and PATCH /contacts/:id.
  Map<String, dynamic> toJson() {
    return {
      'name': name,
      if (email != null) 'email': email,
      if (phone != null) 'phone': phone,
      if (company != null) 'company': company,
      if (jobTitle != null) 'job_title': jobTitle,
      if (avatarUrl != null) 'avatar_url': avatarUrl,
      if (memo != null) 'memo': memo,
      if (latitude != null) 'latitude': latitude,
      if (longitude != null) 'longitude': longitude,
      if (locationName != null) 'location_name': locationName,
      'tags': tags,
      'social_links': socialLinks.map((s) => s.toJson()).toList(),
    };
  }

  factory Contact.fromJson(Map<String, dynamic> json) {
    return Contact(
      id: json['id'].toString(),
      userId: json['user_id'] as int?,
      name: json['name'] as String,
      email: json['email'] as String?,
      phone: json['phone'] as String?,
      company: json['company'] as String?,
      jobTitle: json['job_title'] as String?,
      avatarUrl: json['avatar_url'] as String?,
      memo: json['memo'] as String?,
      latitude: (json['latitude'] as num?)?.toDouble(),
      longitude: (json['longitude'] as num?)?.toDouble(),
      locationName: json['location_name'] as String?,
      tags: (json['tags'] as List?)?.cast<String>() ?? const [],
      socialLinks: (json['social_links'] as List?)
              ?.map((e) => SocialLink.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      timeline: const [],
      meetings: const [],
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }
}
