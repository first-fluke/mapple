import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:forui/forui.dart';

import 'package:mobile/features/contacts/providers/add_contact_provider.dart';
import 'package:mobile/l10n/app_localizations.dart';

class BasicInfoStep extends ConsumerStatefulWidget {
  const BasicInfoStep({super.key});

  @override
  ConsumerState<BasicInfoStep> createState() => _BasicInfoStepState();
}

class _BasicInfoStepState extends ConsumerState<BasicInfoStep> {
  late final TextEditingController _nameController;
  late final TextEditingController _emailController;
  late final TextEditingController _phoneController;
  late final TextEditingController _companyController;
  late final TextEditingController _jobTitleController;
  late final TextEditingController _memoController;

  @override
  void initState() {
    super.initState();
    final state = ref.read(addContactProvider);
    _nameController = TextEditingController(text: state.name);
    _emailController = TextEditingController(text: state.email ?? '');
    _phoneController = TextEditingController(text: state.phone ?? '');
    _companyController = TextEditingController(text: state.company ?? '');
    _jobTitleController = TextEditingController(text: state.jobTitle ?? '');
    _memoController = TextEditingController(text: state.memo ?? '');
  }

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _companyController.dispose();
    _jobTitleController.dispose();
    _memoController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = context.theme;
    final l10n = AppLocalizations.of(context)!;
    final notifier = ref.read(addContactProvider.notifier);

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(
          l10n.basicInfoSectionTitle,
          style: theme.typography.lg.copyWith(
            color: theme.colorScheme.foreground,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          l10n.basicInfoSectionSubtitle,
          style: theme.typography.sm.copyWith(
            color: theme.colorScheme.mutedForeground,
          ),
        ),
        const SizedBox(height: 20),
        FTextField(
          label: Text(l10n.basicInfoNameLabel),
          hint: l10n.basicInfoNameHint,
          controller: _nameController,
          onChange: (value) => notifier.setName(value),
        ),
        const SizedBox(height: 16),
        FTextField(
          label: Text(l10n.basicInfoEmailLabel),
          hint: 'email@example.com',
          controller: _emailController,
          onChange: (value) => notifier.setEmail(value),
          keyboardType: TextInputType.emailAddress,
        ),
        const SizedBox(height: 16),
        FTextField(
          label: Text(l10n.basicInfoPhoneLabel),
          hint: '+1 234 567 8900',
          controller: _phoneController,
          onChange: (value) => notifier.setPhone(value),
          keyboardType: TextInputType.phone,
        ),
        const SizedBox(height: 16),
        FTextField(
          label: Text(l10n.basicInfoCompanyLabel),
          hint: l10n.basicInfoCompanyLabel,
          controller: _companyController,
          onChange: (value) => notifier.setCompany(value),
        ),
        const SizedBox(height: 16),
        FTextField(
          label: Text(l10n.basicInfoJobTitleLabel),
          hint: l10n.basicInfoJobTitleHint,
          controller: _jobTitleController,
          onChange: (value) => notifier.setJobTitle(value),
        ),
        const SizedBox(height: 16),
        FTextField(
          label: Text(l10n.basicInfoMemoLabel),
          hint: l10n.basicInfoMemoHint,
          controller: _memoController,
          onChange: (value) => notifier.setMemo(value),
          minLines: 3,
          maxLines: 5,
        ),
      ],
    );
  }
}
