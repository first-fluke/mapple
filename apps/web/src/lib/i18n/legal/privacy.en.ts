// NOTE: draft translation — pending legal review
import type { LegalDoc } from './types';

export const privacyEn: LegalDoc = {
  title: 'Privacy Policy',
  lastUpdated: '2026-05-03',
  lastUpdatedLabel: 'Last updated:',
  intro:
    'This policy draft is a temporary placeholder for the Mapple v1 launch. It will be updated following legal review before the official service launch.',
  sections: [
    {
      heading: '1. Personal Information We Collect',
      items: [
        'Email address, name, and profile picture received from OAuth providers (Google, GitHub)',
        'Contacts, meetings, organizations, and career data entered directly by the user',
        'Session cookies and access logs generated automatically during service use',
      ],
    },
    {
      heading: '2. Purpose of Use',
      items: [
        'User authentication and identity verification',
        'Storage, display, and search of user-registered data',
        'Error analysis and service quality improvement',
      ],
    },
    {
      heading: '3. Retention Period',
      paragraphs: [
        'Data is retained while the account is active. Upon a user request to delete their account, all personal information and user content will be permanently deleted within 30 days. Items whose retention is mandated by law are subject to the applicable retention periods.',
      ],
    },
    {
      heading: '4. Third-Party Disclosure',
      paragraphs: [
        'The operator does not disclose user information to third parties except with user consent or as required by law.',
      ],
    },
    {
      heading: '5. Data Processing Partners',
      paragraphs: [
        'The following sub-processors are used to operate the service: Google Cloud Platform (infrastructure), Fly.io (API hosting), Vercel (web hosting), Cloudflare (DNS/CDN), Sentry (error tracking).',
      ],
    },
    {
      heading: '6. User Rights',
      items: [
        'Requests to access, correct, delete, or restrict processing of personal information',
        'Direct data modification or account deletion via the account settings page',
      ],
    },
    {
      heading: '7. Security Measures',
      paragraphs: [
        'We apply TLS encryption in transit, database access controls, regular backups, and integrity checks.',
      ],
    },
    {
      heading: '8. Contact',
      paragraphs: ['For privacy-related inquiries, please contact the operator by email.'],
    },
  ],
};
