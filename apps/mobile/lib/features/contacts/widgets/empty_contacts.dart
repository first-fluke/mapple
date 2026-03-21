import 'package:flutter/widgets.dart';
import 'package:forui/forui.dart';

class EmptyContacts extends StatelessWidget {
  final bool isSearchResult;

  const EmptyContacts({this.isSearchResult = false, super.key});

  @override
  Widget build(BuildContext context) {
    final theme = context.theme;

    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            FIcon(
              FAssets.icons.users,
              size: 48,
              color: theme.colorScheme.mutedForeground,
            ),
            const SizedBox(height: 16),
            Text(
              isSearchResult ? '검색 결과가 없습니다' : '연락처가 없습니다',
              style: theme.typography.lg.copyWith(
                color: theme.colorScheme.foreground,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              isSearchResult
                  ? '다른 검색어를 시도해보세요'
                  : '새 연락처를 추가하여 시작하세요',
              style: theme.typography.sm.copyWith(
                color: theme.colorScheme.mutedForeground,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
