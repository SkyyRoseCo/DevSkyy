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
  }
}

declare module 'next-auth/jwt' {
  interface JWT extends DefaultJWT {
    authError?: 'BackendTokenExpired';
    accessToken?: string;
    accessTokenExpiresAt?: number;
  }
}
