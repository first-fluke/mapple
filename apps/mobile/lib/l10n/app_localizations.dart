import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_en.dart';
import 'app_localizations_ko.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'l10n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
    : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
        delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
      ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('en'),
    Locale('ko'),
  ];

  /// Application title
  ///
  /// In ko, this message translates to:
  /// **'Mapple'**
  String get appTitle;

  /// Bottom navigation tab: globe
  ///
  /// In ko, this message translates to:
  /// **'Globe'**
  String get navGlobe;

  /// Bottom navigation tab: graph
  ///
  /// In ko, this message translates to:
  /// **'Graph'**
  String get navGraph;

  /// Bottom navigation tab: contacts
  ///
  /// In ko, this message translates to:
  /// **'연락처'**
  String get navContacts;

  /// Bottom navigation tab: settings
  ///
  /// In ko, this message translates to:
  /// **'설정'**
  String get navSettings;

  /// Semantics label for globe tab
  ///
  /// In ko, this message translates to:
  /// **'Globe 탭'**
  String get navGlobeSemantics;

  /// Semantics label for graph tab
  ///
  /// In ko, this message translates to:
  /// **'Graph 탭'**
  String get navGraphSemantics;

  /// Semantics label for contacts tab
  ///
  /// In ko, this message translates to:
  /// **'연락처 탭'**
  String get navContactsSemantics;

  /// Semantics label for settings tab
  ///
  /// In ko, this message translates to:
  /// **'설정 탭'**
  String get navSettingsSemantics;

  /// Contacts screen heading
  ///
  /// In ko, this message translates to:
  /// **'연락처'**
  String get contactsTitle;

  /// Search field hint text
  ///
  /// In ko, this message translates to:
  /// **'이름으로 검색...'**
  String get contactsSearchHint;

  /// Sort prefix label
  ///
  /// In ko, this message translates to:
  /// **'정렬:'**
  String get contactsSortLabel;

  /// Generic error message in contacts list
  ///
  /// In ko, this message translates to:
  /// **'오류가 발생했습니다'**
  String get contactsErrorOccurred;

  /// Retry button text
  ///
  /// In ko, this message translates to:
  /// **'다시 시도'**
  String get contactsRetry;

  /// Sort option: newest first
  ///
  /// In ko, this message translates to:
  /// **'최신순'**
  String get contactsSortCreatedDesc;

  /// Sort option: oldest first
  ///
  /// In ko, this message translates to:
  /// **'오래된순'**
  String get contactsSortCreatedAsc;

  /// Sort option: name ascending
  ///
  /// In ko, this message translates to:
  /// **'이름 A-Z'**
  String get contactsSortNameAsc;

  /// Sort option: name descending
  ///
  /// In ko, this message translates to:
  /// **'이름 Z-A'**
  String get contactsSortNameDesc;

  /// Empty state title when no contacts
  ///
  /// In ko, this message translates to:
  /// **'연락처가 없습니다'**
  String get emptyContactsTitle;

  /// Empty state subtitle prompting user to add a contact
  ///
  /// In ko, this message translates to:
  /// **'새 연락처를 추가하여 시작하세요'**
  String get emptyContactsSubtitle;

  /// Empty state title when search has no results
  ///
  /// In ko, this message translates to:
  /// **'검색 결과가 없습니다'**
  String get emptySearchTitle;

  /// Empty state subtitle for empty search results
  ///
  /// In ko, this message translates to:
  /// **'다른 검색어를 시도해보세요'**
  String get emptySearchSubtitle;

  /// Dialog title for delete confirmation
  ///
  /// In ko, this message translates to:
  /// **'연락처 삭제'**
  String get contactDetailDeleteTitle;

  /// Dialog message for delete confirmation
  ///
  /// In ko, this message translates to:
  /// **'{name}을(를) 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다.'**
  String contactDetailDeleteMessage(String name);

  /// Confirm delete button label
  ///
  /// In ko, this message translates to:
  /// **'삭제'**
  String get contactDetailDeleteConfirm;

  /// Cancel delete button label
  ///
  /// In ko, this message translates to:
  /// **'취소'**
  String get contactDetailDeleteCancel;

  /// Snackbar message when delete fails
  ///
  /// In ko, this message translates to:
  /// **'삭제에 실패했습니다. 다시 시도해주세요.'**
  String get contactDetailDeleteFailed;

  /// Message when contact is not found
  ///
  /// In ko, this message translates to:
  /// **'연락처를 찾을 수 없습니다'**
  String get contactDetailNotFound;

  /// Snackbar when edit is tapped (not yet implemented)
  ///
  /// In ko, this message translates to:
  /// **'편집 기능은 곧 추가될 예정입니다.'**
  String get contactDetailEditComingSoon;

  /// Add contact screen title
  ///
  /// In ko, this message translates to:
  /// **'새 연락처'**
  String get addContactTitle;

  /// Step indicator label: basic info
  ///
  /// In ko, this message translates to:
  /// **'Basic'**
  String get addContactStepBasic;

  /// Step indicator label: location
  ///
  /// In ko, this message translates to:
  /// **'Location'**
  String get addContactStepLocation;

  /// Step indicator label: tags
  ///
  /// In ko, this message translates to:
  /// **'Tags'**
  String get addContactStepTags;

  /// Previous step button
  ///
  /// In ko, this message translates to:
  /// **'이전'**
  String get addContactPrevious;

  /// Next step button
  ///
  /// In ko, this message translates to:
  /// **'다음'**
  String get addContactNext;

  /// Save button
  ///
  /// In ko, this message translates to:
  /// **'저장'**
  String get addContactSave;

  /// Snackbar when contact save fails
  ///
  /// In ko, this message translates to:
  /// **'연락처 저장에 실패했습니다. 다시 시도해주세요.'**
  String get addContactSaveFailed;

  /// Dismiss snackbar action
  ///
  /// In ko, this message translates to:
  /// **'닫기'**
  String get addContactDismiss;

  /// Validation: name is required
  ///
  /// In ko, this message translates to:
  /// **'이름을 입력해주세요.'**
  String get validationNameRequired;

  /// Validation: email format is wrong
  ///
  /// In ko, this message translates to:
  /// **'올바른 이메일 형식이 아닙니다.'**
  String get validationEmailInvalid;

  /// Basic info step section title
  ///
  /// In ko, this message translates to:
  /// **'Basic Information'**
  String get basicInfoSectionTitle;

  /// Basic info step section subtitle
  ///
  /// In ko, this message translates to:
  /// **'Enter the contact\'s basic details'**
  String get basicInfoSectionSubtitle;

  /// Name field label
  ///
  /// In ko, this message translates to:
  /// **'이름 *'**
  String get basicInfoNameLabel;

  /// Name field hint
  ///
  /// In ko, this message translates to:
  /// **'Full name'**
  String get basicInfoNameHint;

  /// Email field label
  ///
  /// In ko, this message translates to:
  /// **'이메일'**
  String get basicInfoEmailLabel;

  /// Phone field label
  ///
  /// In ko, this message translates to:
  /// **'전화번호'**
  String get basicInfoPhoneLabel;

  /// Company field label
  ///
  /// In ko, this message translates to:
  /// **'회사'**
  String get basicInfoCompanyLabel;

  /// Job title field label
  ///
  /// In ko, this message translates to:
  /// **'직함'**
  String get basicInfoJobTitleLabel;

  /// Job title field hint
  ///
  /// In ko, this message translates to:
  /// **'예) 프로덕트 매니저'**
  String get basicInfoJobTitleHint;

  /// Memo field label
  ///
  /// In ko, this message translates to:
  /// **'메모'**
  String get basicInfoMemoLabel;

  /// Memo field hint
  ///
  /// In ko, this message translates to:
  /// **'이 연락처에 대한 메모'**
  String get basicInfoMemoHint;

  /// Location step title
  ///
  /// In ko, this message translates to:
  /// **'위치'**
  String get locationSectionTitle;

  /// Location step subtitle
  ///
  /// In ko, this message translates to:
  /// **'지도에서 이 연락처를 만난 위치를 선택하세요'**
  String get locationSectionSubtitle;

  /// Location name field label
  ///
  /// In ko, this message translates to:
  /// **'장소명'**
  String get locationNameLabel;

  /// Location name field hint
  ///
  /// In ko, this message translates to:
  /// **'예) 서울 사무실, 강남 카페'**
  String get locationNameHint;

  /// Tags & social step title
  ///
  /// In ko, this message translates to:
  /// **'태그 및 소셜'**
  String get tagsAndSocialTitle;

  /// Tags & social step subtitle
  ///
  /// In ko, this message translates to:
  /// **'이 연락처에 태그와 소셜 링크를 추가하세요'**
  String get tagsAndSocialSubtitle;

  /// Tags section header
  ///
  /// In ko, this message translates to:
  /// **'태그'**
  String get tagsSectionTitle;

  /// Custom tag input hint
  ///
  /// In ko, this message translates to:
  /// **'커스텀 태그 추가'**
  String get tagsAddCustomHint;

  /// Suggested tags label
  ///
  /// In ko, this message translates to:
  /// **'추천'**
  String get tagsSuggestedLabel;

  /// Social links section header
  ///
  /// In ko, this message translates to:
  /// **'소셜 링크'**
  String get socialLinksSectionTitle;

  /// Social link URL input hint
  ///
  /// In ko, this message translates to:
  /// **'프로필 URL'**
  String get socialProfileUrlHint;

  /// Settings: account section title
  ///
  /// In ko, this message translates to:
  /// **'계정'**
  String get settingsAccountSection;

  /// Settings: appearance section title
  ///
  /// In ko, this message translates to:
  /// **'외관'**
  String get settingsAppearanceSection;

  /// Settings: theme tile label
  ///
  /// In ko, this message translates to:
  /// **'테마'**
  String get settingsThemeLabel;

  /// Semantics label for theme tile
  ///
  /// In ko, this message translates to:
  /// **'테마: {mode}'**
  String settingsThemeSemantics(String mode);

  /// Semantics hint for theme tile
  ///
  /// In ko, this message translates to:
  /// **'두 번 탭하여 테마 전환'**
  String get settingsThemeHint;

  /// Sign out tile label
  ///
  /// In ko, this message translates to:
  /// **'로그아웃'**
  String get settingsSignOut;

  /// Settings: notifications section title
  ///
  /// In ko, this message translates to:
  /// **'알림'**
  String get settingsNotificationsSection;

  /// Settings: push notifications tile label
  ///
  /// In ko, this message translates to:
  /// **'푸시 알림'**
  String get settingsNotificationsLabel;

  /// Settings: push notifications tile subtitle
  ///
  /// In ko, this message translates to:
  /// **'새 연락처 및 업데이트 알림 받기'**
  String get settingsNotificationsSubtitle;

  /// Snackbar when notification permission is denied
  ///
  /// In ko, this message translates to:
  /// **'알림 권한이 필요합니다'**
  String get settingsNotificationsPermissionRequired;

  /// Login screen subtitle
  ///
  /// In ko, this message translates to:
  /// **'계속하려면 로그인하세요'**
  String get loginSignInSubtitle;

  /// Google sign in button
  ///
  /// In ko, this message translates to:
  /// **'Google로 로그인'**
  String get loginSignInWithGoogle;

  /// GitHub sign in button
  ///
  /// In ko, this message translates to:
  /// **'GitHub로 로그인'**
  String get loginSignInWithGitHub;

  /// Login failed snackbar message
  ///
  /// In ko, this message translates to:
  /// **'로그인에 실패했습니다: {error}'**
  String loginFailed(String error);

  /// Button to view contact profile from globe bottom sheet
  ///
  /// In ko, this message translates to:
  /// **'프로필 보기'**
  String get globeViewProfile;

  /// Offline banner when cached data is available
  ///
  /// In ko, this message translates to:
  /// **'오프라인 — {time} 캐시 데이터 표시 중'**
  String offlineWithCache(String time);

  /// Offline banner when no cached data is available
  ///
  /// In ko, this message translates to:
  /// **'오프라인 — 캐시 데이터 없음'**
  String get offlineNoCache;

  /// Time ago: just now
  ///
  /// In ko, this message translates to:
  /// **'방금 전'**
  String get timeAgoJustNow;

  /// Time ago: N minutes
  ///
  /// In ko, this message translates to:
  /// **'{minutes}분 전'**
  String timeAgoMinutes(int minutes);

  /// Time ago: N hours
  ///
  /// In ko, this message translates to:
  /// **'{hours}시간 전'**
  String timeAgoHours(int hours);

  /// Time ago: N days
  ///
  /// In ko, this message translates to:
  /// **'{days}일 전'**
  String timeAgoDays(int days);

  /// Error message shown when graph data fails to load
  ///
  /// In ko, this message translates to:
  /// **'그래프를 불러오지 못했습니다'**
  String get graphLoadError;

  /// Empty state message when graph has no relationship data
  ///
  /// In ko, this message translates to:
  /// **'관계 데이터가 없습니다'**
  String get graphEmptyState;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['en', 'ko'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'en':
      return AppLocalizationsEn();
    case 'ko':
      return AppLocalizationsKo();
  }

  throw FlutterError(
    'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.',
  );
}
