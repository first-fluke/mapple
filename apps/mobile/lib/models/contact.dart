class Contact {
  final int id;
  final String name;
  final String? email;
  final String? phone;

  const Contact({
    required this.id,
    required this.name,
    this.email,
    this.phone,
  });
}
