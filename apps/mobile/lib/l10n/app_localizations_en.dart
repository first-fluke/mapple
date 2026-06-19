// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appTitle => 'Mapple';

  @override
  String get navGlobe => 'Globe';

  @override
  String get navGraph => 'Graph';

  @override
  String get navContacts => 'Contacts';

  @override
  String get navSettings => 'Settings';

  @override
  String get navGlobeSemantics => 'Globe tab';

  @override
  String get navGraphSemantics => 'Graph tab';

  @override
  String get navContactsSemantics => 'Contacts tab';

  @override
  String get navSettingsSemantics => 'Settings tab';

  @override
  String get contactsTitle => 'Contacts';

  @override
  String get contactsSearchHint => 'Search by name...';

  @override
  String get contactsSortLabel => 'Sort:';

  @override
  String get contactsErrorOccurred => 'An error occurred';

  @override
  String get contactsRetry => 'Retry';

  @override
  String get contactsSortCreatedDesc => 'Newest';

  @override
  String get contactsSortCreatedAsc => 'Oldest';

  @override
  String get contactsSortNameAsc => 'Name A-Z';

  @override
  String get contactsSortNameDesc => 'Name Z-A';

  @override
  String get emptyContactsTitle => 'No contacts';

  @override
  String get emptyContactsSubtitle => 'Add a new contact to get started';

  @override
  String get emptySearchTitle => 'No results';

  @override
  String get emptySearchSubtitle => 'Try a different search term';

  @override
  String get contactDetailDeleteTitle => 'Delete Contact';

  @override
  String contactDetailDeleteMessage(String name) {
    return 'Delete $name?\nThis action cannot be undone.';
  }

  @override
  String get contactDetailDeleteConfirm => 'Delete';

  @override
  String get contactDetailDeleteCancel => 'Cancel';

  @override
  String get contactDetailDeleteFailed => 'Failed to delete. Please try again.';

  @override
  String get contactDetailNotFound => 'Contact not found';

  @override
  String get contactDetailEditComingSoon => 'Edit feature coming soon.';

  @override
  String get addContactTitle => 'New Contact';

  @override
  String get addContactStepBasic => 'Basic';

  @override
  String get addContactStepLocation => 'Location';

  @override
  String get addContactStepTags => 'Tags';

  @override
  String get addContactPrevious => 'Previous';

  @override
  String get addContactNext => 'Next';

  @override
  String get addContactSave => 'Save';

  @override
  String get addContactSaveFailed =>
      'Failed to save contact. Please try again.';

  @override
  String get addContactDismiss => 'Dismiss';

  @override
  String get validationNameRequired => 'Name is required.';

  @override
  String get validationEmailInvalid => 'Invalid email address.';

  @override
  String get basicInfoSectionTitle => 'Basic Information';

  @override
  String get basicInfoSectionSubtitle => 'Enter the contact\'s basic details';

  @override
  String get basicInfoNameLabel => 'Name *';

  @override
  String get basicInfoNameHint => 'Full name';

  @override
  String get basicInfoEmailLabel => 'Email';

  @override
  String get basicInfoPhoneLabel => 'Phone';

  @override
  String get basicInfoCompanyLabel => 'Company';

  @override
  String get basicInfoJobTitleLabel => 'Job Title';

  @override
  String get basicInfoJobTitleHint => 'e.g. Product Manager';

  @override
  String get basicInfoMemoLabel => 'Memo';

  @override
  String get basicInfoMemoHint => 'Notes about this contact';

  @override
  String get locationSectionTitle => 'Location';

  @override
  String get locationSectionSubtitle =>
      'Tap on the map to place a pin where you met this contact';

  @override
  String get locationNameLabel => 'Location name';

  @override
  String get locationNameHint => 'e.g. Seoul Office, Gangnam Cafe';

  @override
  String get tagsAndSocialTitle => 'Tags & Social';

  @override
  String get tagsAndSocialSubtitle =>
      'Add tags and social links to this contact';

  @override
  String get tagsSectionTitle => 'Tags';

  @override
  String get tagsAddCustomHint => 'Add custom tag';

  @override
  String get tagsSuggestedLabel => 'Suggested';

  @override
  String get socialLinksSectionTitle => 'Social Links';

  @override
  String get socialProfileUrlHint => 'Profile URL';

  @override
  String get settingsAccountSection => 'Account';

  @override
  String get settingsAppearanceSection => 'Appearance';

  @override
  String get settingsThemeLabel => 'Theme';

  @override
  String settingsThemeSemantics(String mode) {
    return 'Theme: $mode';
  }

  @override
  String get settingsThemeHint => 'Double tap to toggle theme';

  @override
  String get settingsSignOut => 'Sign Out';

  @override
  String get settingsNotificationsSection => 'Notifications';

  @override
  String get settingsNotificationsLabel => 'Push Notifications';

  @override
  String get settingsNotificationsSubtitle =>
      'Receive alerts for new contacts and updates';

  @override
  String get settingsNotificationsPermissionRequired =>
      'Notification permission is required';

  @override
  String get loginSignInSubtitle => 'Sign in to continue';

  @override
  String get loginSignInWithGoogle => 'Sign in with Google';

  @override
  String get loginSignInWithGitHub => 'Sign in with GitHub';

  @override
  String loginFailed(String error) {
    return 'Login failed: $error';
  }

  @override
  String get globeViewProfile => 'View Profile';

  @override
  String offlineWithCache(String time) {
    return 'Offline — showing cached data from $time';
  }

  @override
  String get offlineNoCache => 'Offline — no cached data available';

  @override
  String get timeAgoJustNow => 'just now';

  @override
  String timeAgoMinutes(int minutes) {
    return '${minutes}m ago';
  }

  @override
  String timeAgoHours(int hours) {
    return '${hours}h ago';
  }

  @override
  String timeAgoDays(int days) {
    return '${days}d ago';
  }

  @override
  String get graphLoadError => 'Failed to load graph';

  @override
  String get graphEmptyState => 'No relationship data';
}
