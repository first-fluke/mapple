// NOTE: draft translation — pending legal review
import type { LegalDoc } from './types';

export const termsEn: LegalDoc = {
  title: 'Terms of Service',
  lastUpdated: '2026-05-03',
  lastUpdatedLabel: 'Last updated:',
  intro:
    'This terms draft is a temporary placeholder for the Mapple v1 launch. It will be updated following legal review before the official service launch.',
  sections: [
    {
      heading: '1. Service Overview',
      paragraphs: [
        'Mapple (hereinafter "the Service") is software that helps users visualize and manage their personal network.',
      ],
    },
    {
      heading: '2. Account',
      paragraphs: [
        'Using the Service requires OAuth login via a Google or GitHub account. Users are responsible for maintaining the accuracy of the account information they provide.',
      ],
    },
    {
      heading: '3. User Content',
      paragraphs: [
        'Contacts, meetings, organizations, and career information registered by users belong to the user. The operator processes this data solely for the purpose of providing the Service.',
      ],
    },
    {
      heading: '4. Prohibited Activities',
      items: [
        'Registering information that infringes on the rights of others',
        'Reverse engineering or automated bulk collection',
        'Activities that interfere with the normal operation of the Service',
      ],
    },
    {
      heading: '5. Limitation of Liability',
      paragraphs: [
        'The Service is provided "as is." The operator makes no implied warranties regarding service interruptions, data loss, or similar issues. However, this limitation does not apply to damages caused by the operator\'s intentional misconduct or gross negligence.',
      ],
    },
    {
      heading: '6. Changes to Terms',
      paragraphs: [
        'These terms may be amended with prior notice. Users who do not agree to the amended terms may request account deletion.',
      ],
    },
    {
      heading: '7. Contact',
      paragraphs: ['For inquiries regarding these terms, please contact the operator by email.'],
    },
  ],
};
