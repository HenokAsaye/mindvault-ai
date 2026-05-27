/**
 * Token Storage - Manage JWT tokens in localStorage
 * Handles both access and refresh tokens
 */

const STORAGE_KEYS = {
  ACCESS_TOKEN: 'mindvault_access_token',
  REFRESH_TOKEN: 'mindvault_refresh_token',
} as const;

export class TokenStorage {
  /**
   * Save tokens to localStorage
   */
  static setTokens(accessToken: string, refreshToken: string): void {
    try {
      localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, accessToken);
      localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, refreshToken);
    } catch (error) {
      console.error('Failed to save tokens to storage:', error);
    }
  }

  /**
   * Get access token from localStorage
   */
  static getAccessToken(): string | null {
    try {
      return localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
    } catch (error) {
      console.error('Failed to get access token from storage:', error);
      return null;
    }
  }

  /**
   * Get refresh token from localStorage
   */
  static getRefreshToken(): string | null {
    try {
      return localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
    } catch (error) {
      console.error('Failed to get refresh token from storage:', error);
      return null;
    }
  }

  /**
   * Clear all tokens from localStorage
   */
  static clearTokens(): void {
    try {
      localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
      localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
    } catch (error) {
      console.error('Failed to clear tokens from storage:', error);
    }
  }

  /**
   * Check if tokens exist
   */
  static hasTokens(): boolean {
    return !!this.getAccessToken() && !!this.getRefreshToken();
  }
}
