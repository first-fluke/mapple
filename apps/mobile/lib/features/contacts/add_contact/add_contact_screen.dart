import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:forui/forui.dart';
import 'package:go_router/go_router.dart';

import 'package:mobile/features/contacts/add_contact/steps/basic_info_step.dart';
import 'package:mobile/features/contacts/add_contact/steps/location_step.dart';
import 'package:mobile/features/contacts/add_contact/steps/tags_career_step.dart';
import 'package:mobile/features/contacts/providers/add_contact_provider.dart';
import 'package:mobile/features/contacts/providers/contacts_provider.dart';

class AddContactScreen extends ConsumerWidget {
  const AddContactScreen({super.key});

  static const _stepLabels = ['Basic', 'Location', 'Tags'];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(addContactProvider);
    final theme = context.theme;

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
                  onPress: () {
                    ref.read(addContactProvider.notifier).reset();
                    context.go('/contacts');
                  },
                  child: FIcon(FAssets.icons.x),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'New Contact',
                    style: theme.typography.xl.copyWith(
                      color: theme.colorScheme.foreground,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
          ),
          // Step indicator
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Row(
              children: List.generate(_stepLabels.length, (index) {
                final isActive = index == state.currentStep;
                final isCompleted = index < state.currentStep;
                return Expanded(
                  child: GestureDetector(
                    onTap: isCompleted
                        ? () =>
                            ref.read(addContactProvider.notifier).goToStep(index)
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
                                        color:
                                            theme.colorScheme.primaryForeground,
                                      )
                                    : Text(
                                        '${index + 1}',
                                        style: theme.typography.xs.copyWith(
                                          color: isActive
                                              ? theme
                                                  .colorScheme.primaryForeground
                                              : theme.colorScheme
                                                  .secondaryForeground,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                              ),
                            ),
                            if (index < _stepLabels.length - 1)
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
                          _stepLabels[index],
                          style: theme.typography.xs.copyWith(
                            color: isActive
                                ? theme.colorScheme.foreground
                                : theme.colorScheme.mutedForeground,
                            fontWeight:
                                isActive ? FontWeight.bold : FontWeight.normal,
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
          FDivider(),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                if (state.currentStep > 0)
                  Expanded(
                    child: FButton(
                      style: FButtonStyle.outline,
                      onPress: () =>
                          ref.read(addContactProvider.notifier).previousStep(),
                      label: const Text('Back'),
                    ),
                  ),
                if (state.currentStep > 0) const SizedBox(width: 12),
                Expanded(
                  child: state.currentStep < 2
                      ? FButton(
                          onPress: state.currentStep == 0 &&
                                  !state.isBasicInfoValid
                              ? null
                              : () => ref
                                  .read(addContactProvider.notifier)
                                  .nextStep(),
                          label: const Text('Next'),
                        )
                      : FButton(
                          onPress: !state.isBasicInfoValid
                              ? null
                              : () => _saveContact(context, ref),
                          label: const Text('Save Contact'),
                        ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _saveContact(BuildContext context, WidgetRef ref) {
    final state = ref.read(addContactProvider);
    final contact = state.toContact();
    ref.read(contactsProvider.notifier).addContact(contact);
    ref.read(addContactProvider.notifier).reset();
    context.go('/contacts/${contact.id}');
  }
}
