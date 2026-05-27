import { useAuthStore, AuthUser } from '@/stores/authStore';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { authService, LoginRequest, RegisterRequest } from '@/services/api';
import { loginSchema } from '@/lib/validation/login-schema';
import { registerSchema } from '@/lib/validation/register-schema';
import type { LoginInput } from '@/lib/validation/login-schema';
import type { RegisterInput } from '@/lib/validation/register-schema';

/**
 * Helper function to extract and format error messages
 */
function getErrorMessage(error: any): string {
  // Custom CORS error from interceptor
  if (error.name === 'CORS_ERROR') {
    return error.message;
  }

  // Network error (no response from server)
  if (error.message === 'Network Error' || !error.response) {
    return 'Cannot reach the server. Please make sure the backend is running at http://localhost:8000';
  }

  // Backend validation/business logic errors
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }

  if (error.response?.data?.message) {
    return error.response.data.message;
  }

  // HTTP status errors
  if (error.response?.status === 400) {
    return 'Invalid input. Please check your credentials and try again.';
  }

  if (error.response?.status === 401) {
    return 'Invalid email or password.';
  }

  if (error.response?.status === 403) {
    return 'You do not have permission to access this resource.';
  }

  if (error.response?.status === 404) {
    return 'The requested resource was not found.';
  }

  if (error.response?.status >= 500) {
    return 'Server error. Please try again later.';
  }

  // Default fallback
  return error.message || 'An unexpected error occurred. Please try again.';
}

/**
 * useAuth Hook
 * Access current auth state from Zustand store
 * Uses individual selectors to avoid object reference changes
 */
export function useAuth() {
  const user = useAuthStore((state) => state.user);
  const isLoading = useAuthStore((state) => state.isLoading);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const error = useAuthStore((state) => state.error);
  const logout = useAuthStore((state) => state.logout);
  const checkAuth = useAuthStore((state) => state.checkAuth);

  return { user, isLoading, isAuthenticated, error, logout, checkAuth };
}

/**
 * useLogin Hook
 * Handles user login with email/password
 * Validates input, calls API, and stores tokens
 */
export function useLogin() {
  const router = useRouter();
  const setTokens = useAuthStore((state) => state.setTokens);
  const setError = useAuthStore((state) => state.setError);

  return useMutation({
    mutationFn: async (input: LoginInput) => {
      // Validate input with schema
      const validated = loginSchema.parse(input);

      // Make login request
      const response = await authService.login(
        validated as unknown as LoginRequest
      );

      return response.data;
    },
    onSuccess: (data) => {
      // Store tokens in Zustand (automatically persists to localStorage)
      setTokens(data.access_token, data.refresh_token);

      // Clear any previous errors
      setError(null);

      // Redirect to dashboard
      router.push('/dashboard');
    },
    onError: (error: any) => {
      const message = getErrorMessage(error);
      console.error('Login error:', error);
      setError(message);
    },
  });
}

/**
 * useRegister Hook
 * Handles user registration
 * After successful registration, user must login separately
 */
export function useRegister() {
  const router = useRouter();
  const setError = useAuthStore((state) => state.setError);

  return useMutation({
    mutationFn: async (input: RegisterInput) => {
      // Validate input with schema
      const validated = registerSchema.parse(input);

      // Remove confirmPassword from payload (backend doesn't need it)
      const { confirmPassword, ...payload } = validated as any;

      // Make register request
      const response = await authService.register(
        payload as unknown as RegisterRequest
      );

      return response.data;
    },
    onSuccess: (data) => {
      // Clear any previous errors
      setError(null);

      // Redirect to login page
      // User should login with the credentials they just registered with
      router.push('/login');
    },
    onError: (error: any) => {
      const message = getErrorMessage(error);
      console.error('Registration error:', error);
      setError(message);
    },
  });
}

/**
 * useLogout Hook
 * Handles user logout
 */
export function useLogout() {
  const router = useRouter();
  const logout = useAuthStore((state) => state.logout);

  return useMutation({
    mutationFn: logout,
    onSuccess: () => {
      router.push('/login');
    },
    onError: (error: any) => {
      console.error('Logout failed:', error);
      // Still redirect to login even if logout fails
      router.push('/login');
    },
  });
}

/**
 * useCheckAuth Hook
 * Verify user is still authenticated
 * Runs on app initialization
 */
export function useCheckAuth() {
  const checkAuth = useAuthStore((state) => state.checkAuth);
  const isLoading = useAuthStore((state) => state.isLoading);

  return useQuery({
    queryKey: ['auth', 'check'],
    queryFn: checkAuth,
    staleTime: Infinity, // Don't auto-refetch
    retry: false,
  });
}

/**
 * useSwitchOrg Hook
 * Switch active organization
 */
export function useSwitchOrg() {
  const setTokens = useAuthStore((state) => state.setTokens);
  const setError = useAuthStore((state) => state.setError);

  return useMutation({
    mutationFn: async (orgId: string) => {
      const response = await authService.switchOrg(orgId);
      return response.data;
    },
    onSuccess: (data) => {
      // Update tokens (which updates org context)
      setTokens(data.access_token, data.refresh_token);
      setError(null);
    },
    onError: (error: any) => {
      const message = getErrorMessage(error);
      console.error('Org switch error:', error);
      setError(message);
    },
  });
}