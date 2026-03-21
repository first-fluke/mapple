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
}
