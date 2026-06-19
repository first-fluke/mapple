// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Korean (`ko`).
class AppLocalizationsKo extends AppLocalizations {
  AppLocalizationsKo([String locale = 'ko']) : super(locale);

  @override
  String get appTitle => 'Mapple';

  @override
  String get navGlobe => 'Globe';

  @override
  String get navGraph => 'Graph';

  @override
  String get navContacts => '연락처';

  @override
  String get navSettings => '설정';

  @override
  String get navGlobeSemantics => 'Globe 탭';

  @override
  String get navGraphSemantics => 'Graph 탭';

  @override
  String get navContactsSemantics => '연락처 탭';

  @override
  String get navSettingsSemantics => '설정 탭';

  @override
  String get contactsTitle => '연락처';

  @override
  String get contactsSearchHint => '이름으로 검색...';

  @override
  String get contactsSortLabel => '정렬:';

  @override
  String get contactsErrorOccurred => '오류가 발생했습니다';

  @override
  String get contactsRetry => '다시 시도';

  @override
  String get contactsSortCreatedDesc => '최신순';

  @override
  String get contactsSortCreatedAsc => '오래된순';

  @override
  String get contactsSortNameAsc => '이름 A-Z';

  @override
  String get contactsSortNameDesc => '이름 Z-A';

  @override
  String get emptyContactsTitle => '연락처가 없습니다';

  @override
  String get emptyContactsSubtitle => '새 연락처를 추가하여 시작하세요';

  @override
  String get emptySearchTitle => '검색 결과가 없습니다';

  @override
  String get emptySearchSubtitle => '다른 검색어를 시도해보세요';

  @override
  String get contactDetailDeleteTitle => '연락처 삭제';

  @override
  String contactDetailDeleteMessage(String name) {
    return '$name을(를) 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다.';
  }

  @override
  String get contactDetailDeleteConfirm => '삭제';

  @override
  String get contactDetailDeleteCancel => '취소';

  @override
  String get contactDetailDeleteFailed => '삭제에 실패했습니다. 다시 시도해주세요.';

  @override
  String get contactDetailNotFound => '연락처를 찾을 수 없습니다';

  @override
  String get contactDetailEditComingSoon => '편집 기능은 곧 추가될 예정입니다.';

  @override
  String get addContactTitle => '새 연락처';

  @override
  String get addContactStepBasic => 'Basic';

  @override
  String get addContactStepLocation => 'Location';

  @override
  String get addContactStepTags => 'Tags';

  @override
  String get addContactPrevious => '이전';

  @override
  String get addContactNext => '다음';

  @override
  String get addContactSave => '저장';

  @override
  String get addContactSaveFailed => '연락처 저장에 실패했습니다. 다시 시도해주세요.';

  @override
  String get addContactDismiss => '닫기';

  @override
  String get validationNameRequired => '이름을 입력해주세요.';

  @override
  String get validationEmailInvalid => '올바른 이메일 형식이 아닙니다.';

  @override
  String get basicInfoSectionTitle => 'Basic Information';

  @override
  String get basicInfoSectionSubtitle => 'Enter the contact\'s basic details';

  @override
  String get basicInfoNameLabel => '이름 *';

  @override
  String get basicInfoNameHint => 'Full name';

  @override
  String get basicInfoEmailLabel => '이메일';

  @override
  String get basicInfoPhoneLabel => '전화번호';

  @override
  String get basicInfoCompanyLabel => '회사';

  @override
  String get basicInfoJobTitleLabel => '직함';

  @override
  String get basicInfoJobTitleHint => '예) 프로덕트 매니저';

  @override
  String get basicInfoMemoLabel => '메모';

  @override
  String get basicInfoMemoHint => '이 연락처에 대한 메모';

  @override
  String get locationSectionTitle => '위치';

  @override
  String get locationSectionSubtitle => '지도에서 이 연락처를 만난 위치를 선택하세요';

  @override
  String get locationNameLabel => '장소명';

  @override
  String get locationNameHint => '예) 서울 사무실, 강남 카페';

  @override
  String get tagsAndSocialTitle => '태그 및 소셜';

  @override
  String get tagsAndSocialSubtitle => '이 연락처에 태그와 소셜 링크를 추가하세요';

  @override
  String get tagsSectionTitle => '태그';

  @override
  String get tagsAddCustomHint => '커스텀 태그 추가';

  @override
  String get tagsSuggestedLabel => '추천';

  @override
  String get socialLinksSectionTitle => '소셜 링크';

  @override
  String get socialProfileUrlHint => '프로필 URL';

  @override
  String get settingsAccountSection => '계정';

  @override
  String get settingsAppearanceSection => '외관';

  @override
  String get settingsThemeLabel => '테마';

  @override
  String settingsThemeSemantics(String mode) {
    return '테마: $mode';
  }

  @override
  String get settingsThemeHint => '두 번 탭하여 테마 전환';

  @override
  String get settingsSignOut => '로그아웃';

  @override
  String get settingsNotificationsSection => '알림';

  @override
  String get settingsNotificationsLabel => '푸시 알림';

  @override
  String get settingsNotificationsSubtitle => '새 연락처 및 업데이트 알림 받기';

  @override
  String get settingsNotificationsPermissionRequired => '알림 권한이 필요합니다';

  @override
  String get loginSignInSubtitle => '계속하려면 로그인하세요';

  @override
  String get loginSignInWithGoogle => 'Google로 로그인';

  @override
  String get loginSignInWithGitHub => 'GitHub로 로그인';

  @override
  String loginFailed(String error) {
    return '로그인에 실패했습니다: $error';
  }

  @override
  String get globeViewProfile => '프로필 보기';

  @override
  String offlineWithCache(String time) {
    return '오프라인 — $time 캐시 데이터 표시 중';
  }

  @override
  String get offlineNoCache => '오프라인 — 캐시 데이터 없음';

  @override
  String get timeAgoJustNow => '방금 전';

  @override
  String timeAgoMinutes(int minutes) {
    return '$minutes분 전';
  }

  @override
  String timeAgoHours(int hours) {
    return '$hours시간 전';
  }

  @override
  String timeAgoDays(int days) {
    return '$days일 전';
  }

  @override
  String get graphLoadError => '그래프를 불러오지 못했습니다';

  @override
  String get graphEmptyState => '관계 데이터가 없습니다';
}
