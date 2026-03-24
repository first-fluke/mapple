import { betterAuth } from 'better-auth';
import { nextCookies } from 'better-auth/next-js';

export const auth = betterAuth({
  database: {
    type: 'postgres',
    url: process.env.DATABASE_URL ?? 'postgresql://globe:globe@localhost:5432/globe_crm',
  },
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID ?? '',
      clientSecret: process.env.GOOGLE_CLIENT_SECRET ?? '',
    },
    github: {
      clientId: process.env.GITHUB_CLIENT_ID ?? '',
      clientSecret: process.env.GITHUB_CLIENT_SECRET ?? '',
    },
  },
  plugins: [nextCookies()],
});

export type Session = typeof auth.$Infer.Session;
