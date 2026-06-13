import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/app.dart';

// TODO(oma-deferred): provision Firebase (google-services.json /
// GoogleService-Info.plist) and enable the Firebase init block below.
// Steps:
//   1. Add google-services.json to android/app/
//   2. Add GoogleService-Info.plist to ios/Runner/
//   3. Run `flutterfire configure` — this generates lib/firebase_options.dart
//   4. Uncomment the import + init block below
//   5. Build with --dart-define=FIREBASE_CONFIGURED=true
//      (or set _kFirebaseConfigured = true in notifications_service.dart)
//
// import 'package:firebase_core/firebase_core.dart';
// import 'firebase_options.dart';
// import 'package:mobile/features/notifications/notifications_service.dart';
// import 'package:mobile/features/notifications/notifications_provider.dart';
//
// After WidgetsFlutterBinding.ensureInitialized() add:
//   await Firebase.initializeApp(
//     options: DefaultFirebaseOptions.currentPlatform,
//   );
//
// Then inside ProviderScope create a temporary container to init the service:
//   final container = ProviderContainer();
//   final service = container.read(notificationsServiceProvider);
//   await initNotificationsService(service);
//   runApp(UncontrolledProviderScope(container: container, child: const GlobeApp()));

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const ProviderScope(child: GlobeApp()));
}
