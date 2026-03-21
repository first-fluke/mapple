import 'package:flutter/material.dart';
import 'package:flutter_inappwebview/flutter_inappwebview.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:forui/forui.dart';

import 'package:mobile/features/contacts/contacts_provider.dart';
import 'package:mobile/models/contact.dart';
import 'package:mobile/services/js_bridge_service.dart';

class GlobeScreen extends ConsumerWidget {
  const GlobeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isAccessible = MediaQuery.of(context).accessibleNavigation;
    final contacts = ref.watch(contactsProvider);

    if (isAccessible) {
      return _GlobeFallbackList(contacts: contacts);
    }

    return _GlobeWebView(ref: ref);
  }
}

class _GlobeFallbackList extends StatelessWidget {
  final List<Contact> contacts;

  const _GlobeFallbackList({required this.contacts});

  @override
  Widget build(BuildContext context) {
    final theme = context.theme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: Semantics(
            header: true,
            child: Text(
              'Contacts',
              style: theme.typography.xl2.copyWith(
                color: theme.colorScheme.foreground,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
        Expanded(
          child: ListView.builder(
            itemCount: contacts.length,
            itemBuilder: (context, index) {
              final contact = contacts[index];
              return Semantics(
                label: contact.name,
                hint: contact.email ?? contact.phone ?? '',
                child: FTile(
                  prefixIcon: FIcon(FAssets.icons.user),
                  title: Text(contact.name),
                  subtitle: Text(contact.email ?? contact.phone ?? ''),
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}

class _GlobeWebView extends StatelessWidget {
  final WidgetRef ref;

  const _GlobeWebView({required this.ref});

  @override
  Widget build(BuildContext context) {
    return InAppWebView(
      initialSettings: InAppWebViewSettings(
        transparentBackground: true,
        javaScriptEnabled: true,
      ),
      onWebViewCreated: (controller) {
        JsBridgeService.registerHandlers(controller, ref);
      },
      onReceivedError: (controller, request, error) {
        // WebView request error — fallback handled by parent
      },
    );
  }
}
