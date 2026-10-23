/**
 * NextAuth.js type augmentations for custom JWT fields
 */

import type { DefaultSession, DefaultUser } from 'next-auth';
import type { DefaultJWT } from 'next-auth/jwt';

declare module 'next-auth' {
  interface User extends DefaultUser {
    accessToken?: string;
    accessTokenExpiresAt?: number;
  }

  interface Session extends DefaultSession {
    authError?: 'BackendTokenExpired';
    user: DefaultSession['user'] & { backendSubject?: string };
  }
}

declare module 'next-auth/jwt' {
  interface JWT extends DefaultJWT {
    backendSubject?: string;
    authError?: 'BackendTokenExpired';
    accessToken?: string;
    accessTokenExpiresAt?: number;
  }
}
