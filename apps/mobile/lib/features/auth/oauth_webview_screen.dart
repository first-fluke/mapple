import 'package:flutter/material.dart';
import 'package:flutter_inappwebview/flutter_inappwebview.dart';
import 'package:forui/forui.dart';

import 'package:mobile/core/config.dart';

class OAuthWebViewScreen extends StatelessWidget {
  final String provider;

  const OAuthWebViewScreen({required this.provider, super.key});

  String get _authUrl {
    final callbackUrl = Uri.encodeFull(AppConfig.authCallbackUrl);

    return switch (provider) {
      'google' =>
        'https://accounts.google.com/o/oauth2/v2/auth'
            '?client_id=${AppConfig.googleClientId}'
            '&redirect_uri=$callbackUrl'
            '&response_type=code'
            '&scope=email%20profile',
      'github' =>
        'https://github.com/login/oauth/authorize'
            '?client_id=${AppConfig.githubClientId}'
            '&redirect_uri=$callbackUrl'
            '&scope=user:email',
      _ => throw ArgumentError('Unsupported provider: $provider'),
    };
  }

  @override
  Widget build(BuildContext context) {
    return FScaffold(
      content: Column(
        children: [
          FHeader.nested(
            title: Text(
              'Sign in with ${provider[0].toUpperCase()}${provider.substring(1)}',
            ),
            prefixActions: [
              FHeaderAction(
                icon: FIcon(FAssets.icons.arrowLeft),
                onPress: () => Navigator.of(context).pop(),
              ),
            ],
          ),
          Expanded(
            child: InAppWebView(
              initialUrlRequest: URLRequest(url: WebUri(_authUrl)),
              initialSettings: InAppWebViewSettings(
                useShouldOverrideUrlLoading: true,
                clearCache: true,
              ),
              shouldOverrideUrlLoading: (controller, action) async {
                final url = action.request.url;
                if (url != null &&
                    url
                        .toString()
                        .startsWith(AppConfig.authCallbackUrl)) {
                  final code = url.queryParameters['code'];
                  if (code != null && context.mounted) {
                    Navigator.of(context).pop(code);
                  }
                  return NavigationActionPolicy.CANCEL;
                }
                return NavigationActionPolicy.ALLOW;
              },
            ),
          ),
        ],
      ),
    );
  }
}
