<<<<<<< HEAD
import { betterAuth } from 'better-auth';
import { nextCookies } from 'better-auth/next-js';
import Database from 'better-sqlite3';
import { env } from './env';

export const auth = betterAuth({
  database: new Database('auth.db'),
  secret: env.BETTER_AUTH_SECRET,
  baseURL: env.BETTER_AUTH_URL,
  emailAndPassword: {
    enabled: true,
  },
  plugins: [nextCookies()],
});
=======
export { authClient } from './auth-client';
>>>>>>> 2c83c4e (feat(web,api): integrate better-auth for authentication)
