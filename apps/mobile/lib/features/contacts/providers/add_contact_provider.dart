import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/features/contacts/models/contact.dart';

@immutable
class AddContactState {
  final int currentStep;
  // Step 1: Basic info
  final String name;
  final String? email;
  final String? phone;
  final String? company;
  final String? jobTitle;
  final String? memo;
  // Step 2: Location
  final double? latitude;
  final double? longitude;
  final String? locationName;
  // Step 3: Tags & Career
  final List<String> tags;
  final List<SocialLink> socialLinks;

  const AddContactState({
    this.currentStep = 0,
    this.name = '',
    this.email,
    this.phone,
    this.company,
    this.jobTitle,
    this.memo,
    this.latitude,
    this.longitude,
    this.locationName,
    this.tags = const [],
    this.socialLinks = const [],
  });

  AddContactState copyWith({
    int? currentStep,
    String? name,
    String? email,
    String? phone,
    String? company,
    String? jobTitle,
    String? memo,
    double? latitude,
    double? longitude,
    String? locationName,
    List<String>? tags,
    List<SocialLink>? socialLinks,
  }) {
    return AddContactState(
      currentStep: currentStep ?? this.currentStep,
      name: name ?? this.name,
      email: email ?? this.email,
      phone: phone ?? this.phone,
      company: company ?? this.company,
      jobTitle: jobTitle ?? this.jobTitle,
      memo: memo ?? this.memo,
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      locationName: locationName ?? this.locationName,
      tags: tags ?? this.tags,
      socialLinks: socialLinks ?? this.socialLinks,
    );
  }

  bool get isBasicInfoValid => name.trim().isNotEmpty;

  Contact toContact() {
    final now = DateTime.now();
    return Contact(
      id: now.millisecondsSinceEpoch.toString(),
      name: name.trim(),
      email: email?.trim(),
      phone: phone?.trim(),
      company: company?.trim(),
      jobTitle: jobTitle?.trim(),
      memo: memo?.trim(),
      latitude: latitude,
      longitude: longitude,
      locationName: locationName,
      tags: tags,
      socialLinks: socialLinks,
      createdAt: now,
      updatedAt: now,
    );
  }
}

final addContactProvider =
    NotifierProvider<AddContactNotifier, AddContactState>(
        AddContactNotifier.new);

class AddContactNotifier extends Notifier<AddContactState> {
  @override
  AddContactState build() => const AddContactState();

  void reset() {
    state = const AddContactState();
  }

  void nextStep() {
    if (state.currentStep < 2) {
      state = state.copyWith(currentStep: state.currentStep + 1);
    }
  }

  void previousStep() {
    if (state.currentStep > 0) {
      state = state.copyWith(currentStep: state.currentStep - 1);
    }
  }

  void goToStep(int step) {
    if (step >= 0 && step <= 2) {
      state = state.copyWith(currentStep: step);
    }
  }

  // Step 1: Basic info
  void setName(String name) => state = state.copyWith(name: name);
  void setEmail(String email) => state = state.copyWith(email: email);
  void setPhone(String phone) => state = state.copyWith(phone: phone);
  void setCompany(String company) => state = state.copyWith(company: company);
  void setJobTitle(String jobTitle) =>
      state = state.copyWith(jobTitle: jobTitle);
  void setMemo(String memo) => state = state.copyWith(memo: memo);

  // Step 2: Location
  void setLocation({
    required double latitude,
    required double longitude,
    String? locationName,
  }) {
    state = state.copyWith(
      latitude: latitude,
      longitude: longitude,
      locationName: locationName,
    );
  }

  // Step 3: Tags & Career
  void setTags(List<String> tags) => state = state.copyWith(tags: tags);

  void addTag(String tag) {
    if (!state.tags.contains(tag)) {
      state = state.copyWith(tags: [...state.tags, tag]);
    }
  }

  void removeTag(String tag) {
    state = state.copyWith(tags: state.tags.where((t) => t != tag).toList());
  }

  void setSocialLinks(List<SocialLink> links) =>
      state = state.copyWith(socialLinks: links);

  void addSocialLink(SocialLink link) {
    state = state.copyWith(socialLinks: [...state.socialLinks, link]);
  }

  void removeSocialLink(int index) {
    final links = [...state.socialLinks];
    links.removeAt(index);
    state = state.copyWith(socialLinks: links);
  }
}
