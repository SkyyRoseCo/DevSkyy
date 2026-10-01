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

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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

        const controller = new AbortController();
        let timeoutId: ReturnType<typeof setTimeout> | undefined;
        const deadline = new Promise<never>((_, reject) => {
          timeoutId = setTimeout(() => {
            controller.abort();
            reject(new Error('Authentication deadline exceeded'));
          }, 10000);
        });

        try {
          const body = new URLSearchParams();
          body.append('username', credentials.email);
          body.append('password', credentials.password);
          body.append('grant_type', 'password');

          const response = await Promise.race([
            fetch(`${API_URL}/api/v1/auth/token`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
              },
              body: body.toString(),
              signal: controller.signal,
            }),
            deadline,
          ]);

          if (!response.ok) {
            return null;
          }

          const data = await Promise.race([response.json(), deadline]);

          if (!data.access_token) {
            return null;
          }

          // Return a user object that NextAuth will encode into the JWT
          return {
            id: credentials.email,
            email: credentials.email,
            accessToken: data.access_token,
            refreshToken: data.refresh_token,
          };
        } catch {
          return null;
        } finally {
          clearTimeout(timeoutId);
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
      // On initial sign-in, persist backend tokens into the JWT
      if (user) {
        token.accessToken = (user as { accessToken?: string }).accessToken;
        token.refreshToken = (user as { refreshToken?: string }).refreshToken;
        token.email = user.email;
      }
      return token;
    },

    async session({ session, token }) {
      // Expose the backend access token to the client session
      (session as { accessToken?: string }).accessToken = token.accessToken as string;
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
