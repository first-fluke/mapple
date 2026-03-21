# Mobile App (Flutter)

Globe CRM mobile application built with Flutter.

## Tech Stack

| Layer       | Technology                     |
| ----------- | ------------------------------ |
| Framework   | Flutter 3                      |
| State       | Riverpod 3                     |
| Routing     | go_router (StatefulShellRoute) |
| UI          | Forui (shadcn/ui for Flutter)  |
| HTTP        | Dio                            |
| Database    | Drift (SQLite)                 |
| WebView     | flutter_inappwebview           |
| Connectivity| connectivity_plus              |

## Architecture

```
lib/
├── main.dart              # Entry point, ProviderScope
├── app.dart               # MaterialApp.router + FTheme
├── router/                # GoRouter configuration
│   └── router.dart        # StatefulShellRoute with 4 tabs
├── shell/                 # App shell (bottom nav)
│   └── app_shell.dart     # FScaffold + FBottomNavigationBar
├── theme/                 # Theme configuration
│   └── theme_provider.dart # ThemeMode Riverpod provider
└── features/              # Feature modules
    ├── globe/             # Globe tab
    ├── graph/             # Graph tab
    ├── contacts/          # Contacts tab
    └── settings/          # Settings tab
```

## Conventions

- Feature-first directory structure under `lib/features/`
- Use Riverpod providers for state management
- Use Forui widgets (`FScaffold`, `FTile`, `FBottomNavigationBar`, etc.) for UI
- Use `context.theme` for accessing Forui theme data
- Keep screens as `ConsumerWidget` when they need state, `StatelessWidget` otherwise
- Use absolute imports: `package:mobile/...`

## Commands

```bash
# Run app
flutter run

# Analyze
flutter analyze

# Test
flutter test

# Code generation (Riverpod, Drift)
dart run build_runner build --delete-conflicting-outputs
```
