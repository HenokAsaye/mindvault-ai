import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authService } from '@/services/api';
import { TokenStorage } from '@/lib/auth/storage';
import { extractUserFromToken } from '@/lib/auth/jwt-utils';

/**
 * User state structure
 */
export interface AuthUser {
  user_id: string;
  org_id: string;
  role: 'owner' | 'admin' | 'member' | 'viewer';
}

/**
 * Auth store state
 * Manages:
 * - JWT tokens (access + refresh)
 * - Current user info (extracted from token)
 * - Organization context
 * - Loading and error states
 */
interface AuthState {
  // Tokens
  accessToken: string | null;
  refreshToken: string | null;

  // User info
  user: AuthUser | null;

  // UI states
  isLoading: boolean;
  error: string | null;

  // Computed
  isAuthenticated: boolean;

  // Actions
  setTokens: (accessToken: string, refreshToken: string) => void;
  clearTokens: () => void;
  setError: (error: string | null) => void;
  setLoading: (loading: boolean) => void;
  
  // Auth operations
  checkAuth: () => Promise<void>;
  logout: () => Promise<void>;
}

/**
 * Zustand store with persistence
 * Tokens are persisted to localStorage via middleware
 */
export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial state
      accessToken: null,
      refreshToken: null,
      user: null,
      isLoading: true,
      error: null,
      isAuthenticated: false,

      /**
       * Set tokens and extract user info from access token
       */
      setTokens: (accessToken: string, refreshToken: string) => {
        // Save to localStorage
        TokenStorage.setTokens(accessToken, refreshToken);

        // Extract user info from token
        const user = extractUserFromToken(accessToken);

        set({
          accessToken,
          refreshToken,
          user,
          isAuthenticated: true,
          error: null,
        });
      },

      /**
       * Clear all tokens and user data
       */
      clearTokens: () => {
        TokenStorage.clearTokens();
        set({
          accessToken: null,
          refreshToken: null,
          user: null,
          isAuthenticated: false,
          error: null,
        });
      },

      /**
       * Set error message
       */
      setError: (error: string | null) => {
        set({ error });
      },

      /**
       * Set loading state
       */
      setLoading: (isLoading: boolean) => {
        set({ isLoading });
      },

      /**
       * Check if user is authenticated by calling /auth/me
       * This verifies the token is still valid server-side
       */
      checkAuth: async () => {
        const { accessToken } = get();

        // No token = not authenticated
        if (!accessToken) {
          set({ isLoading: false });
          return;
        }

        try {
          const response = await authService.getMe();
          
          // Token is valid, update user info
          const user: AuthUser = {
            user_id: response.data.user_id,
            org_id: response.data.org_id,
            role: response.data.role as AuthUser['role'],
          };

          set({
            user,
            isAuthenticated: true,
            error: null,
            isLoading: false,
          });
        } catch (error) {
          // Token is invalid or expired
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
          });
          
          // Clear tokens if they're invalid
          TokenStorage.clearTokens();
          set({
            accessToken: null,
            refreshToken: null,
          });
        }
      },

      /**
       * Logout user
       */
      logout: async () => {
        try {
          set({ isLoading: true });
          await authService.logout();
        } catch (error) {
          console.error('Logout error:', error);
        } finally {
          // Always clear tokens, even if logout API fails
          get().clearTokens();
          set({ isLoading: false });
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
      }),
    }
  )
);
