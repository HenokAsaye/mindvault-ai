/**
 * JWT Utilities - Decode and manage JWT tokens
 * Client-side token management (no signature verification - that's backend's job)
 */

export interface JWTClaims {
  sub: string;        // user_id
  org_id: string;     // organization_id
  role: string;       // owner, admin, member, viewer
  exp: number;        // expiration timestamp
  iat: number;        // issued at timestamp
  jti?: string;       // JWT ID (for refresh token tracking)
  type?: string;      // 'access' or 'refresh'
  [key: string]: any; // allow other claims
}

/**
 * Decode JWT token without verification (client-side only)
 * Backend already verified signature, we just extract claims
 */
export function decodeJWT(token: string): JWTClaims | null {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) {
      return null;
    }

    const decoded = JSON.parse(
      Buffer.from(parts[1], 'base64').toString('utf-8')
    );
    return decoded as JWTClaims;
  } catch (error) {
    console.error('Failed to decode JWT:', error);
    return null;
  }
}

/**
 * Check if token is expired
 */
export function isTokenExpired(token: string): boolean {
  const claims = decodeJWT(token);
  if (!claims) return true;

  const now = Math.floor(Date.now() / 1000);
  return claims.exp <= now;
}

/**
 * Get time until token expires (in seconds)
 */
export function getTokenExpiry(token: string): number {
  const claims = decodeJWT(token);
  if (!claims) return 0;

  const now = Math.floor(Date.now() / 1000);
  return Math.max(0, claims.exp - now);
}

/**
 * Extract user info from access token
 */
export function extractUserFromToken(token: string) {
  const claims = decodeJWT(token);
  if (!claims) return null;

  return {
    user_id: claims.sub,
    org_id: claims.org_id,
    role: claims.role,
  };
}
