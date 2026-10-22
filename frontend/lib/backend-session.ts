import 'server-only';
import { getToken } from 'next-auth/jwt';
import type { NextRequest } from 'next/server';

/** Read only the encrypted NextAuth cookie; never accept caller-supplied Bearer credentials. */
export async function getBackendAccessToken(request: NextRequest): Promise<string | null> {
  const secret = process.env.NEXTAUTH_SECRET;
  if (!secret?.trim()) return null;
  const headers = new Headers(request.headers);
  headers.delete('authorization');
  try {
    const token = await getToken({
      req: { headers, cookies: request.cookies } as NextRequest,
      secret,
    });
    if (
      !token ||
      token.authError ||
      typeof token.accessToken !== 'string' ||
      !token.accessToken.trim() ||
      typeof token.accessTokenExpiresAt !== 'number' ||
      !Number.isFinite(token.accessTokenExpiresAt) ||
      token.accessTokenExpiresAt <= Date.now()
    )
      return null;
    return token.accessToken;
  } catch {
    return null;
  }
}
