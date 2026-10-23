/**
 * NextAuth.js v4 Configuration
 *
 * Authenticates against the existing backend JWT auth system at
 * POST /api/v1/auth/token (OAuth2 form-encoded).
 *
 * NEXTAUTH_SECRET must be set in environment.
 * Generate with: openssl rand -base64 32
 */

import type { NextAuthOptions } from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import { getBackendOrigin } from './backend-proxy';

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null;
        }

        try {
          const body = new URLSearchParams();
          body.append('username', credentials.email);
          body.append('password', credentials.password);
          body.append('grant_type', 'password');

          const origin = getBackendOrigin();
          if (!origin) return null;
          const response = await fetch(`${origin}/api/v1/auth/token`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: body.toString(),
            redirect: 'error',
            cache: 'no-store',
            signal: AbortSignal.timeout(10000),
          });

          if (!response.ok) {
            return null;
          }

          const data = await response.json();

          if (
            typeof data.access_token !== 'string' ||
            !data.access_token.trim() ||
            typeof data.expires_in !== 'number' ||
            !Number.isFinite(data.expires_in) ||
            data.expires_in <= 0 ||
            !Number.isFinite(Date.now() + data.expires_in * 1000)
          ) {
            return null;
          }

          // Return a user object that NextAuth will encode into the JWT
          return {
            id: credentials.email,
            email: credentials.email,
            accessToken: data.access_token,
            accessTokenExpiresAt: Date.now() + data.expires_in * 1000,
          };
        } catch {
          return null;
        }
      },
    }),
  ],

  session: {
    strategy: 'jwt',
    maxAge: 15 * 60, // 15 minutes (matches backend token expiry)
  },

  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.accessToken = user.accessToken;
        token.accessTokenExpiresAt = user.accessTokenExpiresAt;
        token.email = user.email;
        delete token.authError;
      }
      // Never refresh automatically or retain a credential beyond its backend lifetime.
      delete token.refreshToken;
      if (
        typeof token.accessToken !== 'string' ||
        !token.accessToken.trim() ||
        typeof token.accessTokenExpiresAt !== 'number' ||
        !Number.isFinite(token.accessTokenExpiresAt) ||
        token.accessTokenExpiresAt <= Date.now()
      ) {
        delete token.accessToken;
        token.authError = 'BackendTokenExpired';
      }
      return token;
    },

    async session({ session, token }) {
      // Explicitly scrub credentials from legacy sessions as well as new ones.
      const publicSession = session as typeof session & { accessToken?: string; refreshToken?: string };
      delete publicSession.accessToken;
      delete publicSession.refreshToken;
      if (token.authError) session.authError = 'BackendTokenExpired';
      if (session.user) {
        session.user.email = token.email as string;
      }
      return session;
    },
  },

  pages: {
    signIn: '/login',
  },

  // NEXTAUTH_SECRET is read automatically from env by NextAuth
  // No need to explicitly set `secret` here if NEXTAUTH_SECRET is defined
};
