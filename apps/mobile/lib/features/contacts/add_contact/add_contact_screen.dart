import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:forui/forui.dart';
import 'package:go_router/go_router.dart';

import 'package:mobile/features/contacts/add_contact/steps/basic_info_step.dart';
import 'package:mobile/features/contacts/add_contact/steps/location_step.dart';
import 'package:mobile/features/contacts/add_contact/steps/tags_career_step.dart';
import 'package:mobile/features/contacts/providers/add_contact_provider.dart';
import 'package:mobile/features/contacts/providers/contacts_provider.dart';
import 'package:mobile/l10n/app_localizations.dart';

class AddContactScreen extends ConsumerWidget {
  const AddContactScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(addContactProvider);
    final theme = context.theme;
    final l10n = AppLocalizations.of(context)!;

    final stepLabels = [
      l10n.addContactStepBasic,
      l10n.addContactStepLocation,
      l10n.addContactStepTags,
    ];

    return PopScope(
      onPopInvokedWithResult: (didPop, _) {
        if (didPop) {
          ref.read(addContactProvider.notifier).reset();
        }
      },
      child: Column(
        children: [
          // Top bar
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 8),
            child: Row(
              children: [
                FButton.icon(
                  onPress: state.isSaving
                      ? null
                      : () {
                          ref.read(addContactProvider.notifier).reset();
                          context.go('/contacts');
                        },
                  child: FIcon(FAssets.icons.x),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    l10n.addContactTitle,
                    style: theme.typography.xl.copyWith(
                      color: theme.colorScheme.foreground,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                if (state.isSaving)
                  const Padding(
                    padding: EdgeInsets.only(right: 8),
                    child: SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    ),
                  ),
              ],
            ),
          ),
          // Step indicator
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Row(
              children: List.generate(stepLabels.length, (index) {
                final isActive = index == state.currentStep;
                final isCompleted = index < state.currentStep;
                return Expanded(
                  child: GestureDetector(
                    onTap: (isCompleted && !state.isSaving)
                        ? () => ref
                            .read(addContactProvider.notifier)
                            .goToStep(index)
                        : null,
                    child: Column(
                      children: [
                        Row(
                          children: [
                            if (index > 0)
                              Expanded(
                                child: Container(
                                  height: 2,
                                  color: isCompleted || isActive
                                      ? theme.colorScheme.primary
                                      : theme.colorScheme.border,
                                ),
                              ),
                            Container(
                              width: 28,
                              height: 28,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: isActive || isCompleted
                                    ? theme.colorScheme.primary
                                    : theme.colorScheme.secondary,
                              ),
                              child: Center(
                                child: isCompleted
                                    ? FIcon(
                                        FAssets.icons.check,
                                        size: 14,
                                        color: theme
                                            .colorScheme.primaryForeground,
                                      )
                                    : Text(
                                        '${index + 1}',
                                        style: theme.typography.xs.copyWith(
                                          color: isActive
                                              ? theme.colorScheme
                                                  .primaryForeground
                                              : theme.colorScheme
                                                  .secondaryForeground,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                              ),
                            ),
                            if (index < stepLabels.length - 1)
                              Expanded(
                                child: Container(
                                  height: 2,
                                  color: isCompleted
                                      ? theme.colorScheme.primary
                                      : theme.colorScheme.border,
                                ),
                              ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        Text(
                          stepLabels[index],
                          style: theme.typography.xs.copyWith(
                            color: isActive
                                ? theme.colorScheme.foreground
                                : theme.colorScheme.mutedForeground,
                            fontWeight: isActive
                                ? FontWeight.bold
                                : FontWeight.normal,
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              }),
            ),
          ),
          const FDivider(),
          // Step content
          Expanded(
            child: switch (state.currentStep) {
              0 => const BasicInfoStep(),
              1 => const LocationStep(),
              2 => const TagsCareerStep(),
              _ => const SizedBox.shrink(),
            },
          ),
          // Bottom navigation
          const FDivider(),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                if (state.currentStep > 0)
                  Expanded(
                    child: FButton(
                      style: FButtonStyle.outline,
                      onPress: state.isSaving
                          ? null
                          : () => ref
                              .read(addContactProvider.notifier)
                              .previousStep(),
                      label: Text(l10n.addContactPrevious),
                    ),
                  ),
                if (state.currentStep > 0) const SizedBox(width: 12),
                Expanded(
                  child: state.currentStep < 2
                      ? FButton(
                          onPress: (state.currentStep == 0 &&
                                      !state.isBasicInfoValid) ||
                                  state.isSaving
                              ? null
                              : () => ref
                                  .read(addContactProvider.notifier)
                                  .nextStep(),
                          label: Text(l10n.addContactNext),
                        )
                      : FButton(
                          onPress: (!state.isBasicInfoValid || state.isSaving)
                              ? null
                              : () => _saveContact(context, ref),
                          label: Text(l10n.addContactSave),
                        ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _saveContact(BuildContext context, WidgetRef ref) async {
    final l10n = AppLocalizations.of(context)!;
    final formState = ref.read(addContactProvider);
    final nameError = _validateName(formState.name, l10n);
    if (nameError != null) {
      _showError(context, nameError);
      return;
    }
    if (formState.email != null && formState.email!.trim().isNotEmpty) {
      final emailError = _validateEmail(formState.email!, l10n);
      if (emailError != null) {
        _showError(context, emailError);
        return;
      }
    }

    ref.read(addContactProvider.notifier).setSaving(saving: true);
    try {
      final payload = formState.toPayload();
      final created =
          await ref.read(contactsProvider.notifier).createContact(payload);
      ref.read(addContactProvider.notifier).reset();
      if (context.mounted) {
        context.go('/contacts/${created.id}');
      }
    } catch (e) {
      ref.read(addContactProvider.notifier).setSaveError(e.toString());
      if (context.mounted) {
        final l10nInner = AppLocalizations.of(context)!;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10nInner.addContactSaveFailed),
            backgroundColor: Theme.of(context).colorScheme.error,
            action: SnackBarAction(
              label: l10nInner.addContactDismiss,
              textColor: Theme.of(context).colorScheme.onError,
              onPressed: () =>
                  ScaffoldMessenger.of(context).hideCurrentSnackBar(),
            ),
          ),
        );
      }
    }
  }

  String? _validateName(String name, AppLocalizations l10n) {
    if (name.trim().isEmpty) return l10n.validationNameRequired;
    return null;
  }

  String? _validateEmail(String email, AppLocalizations l10n) {
    final emailRegex = RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$');
    if (!emailRegex.hasMatch(email.trim())) return l10n.validationEmailInvalid;
    return null;
  }

  void _showError(BuildContext context, String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Theme.of(context).colorScheme.error,
      ),
    );
  }
}
