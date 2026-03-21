class User {
  final int id;
  final String provider;
  final String email;
  final String? name;
  final String? avatarUrl;

  const User({
    required this.id,
    required this.provider,
    required this.email,
    this.name,
    this.avatarUrl,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as int,
      provider: json['provider'] as String,
      email: json['email'] as String,
      name: json['name'] as String?,
      avatarUrl: json['avatar_url'] as String?,
    );
  }
}
