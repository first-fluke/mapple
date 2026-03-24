import { toNextJsHandler } from 'better-auth/next-js';
<<<<<<< HEAD
import { auth } from '@/lib/auth';
=======
import { auth } from '@/lib/auth-server';
>>>>>>> 2c83c4e (feat(web,api): integrate better-auth for authentication)

export const { GET, POST } = toNextJsHandler(auth);
