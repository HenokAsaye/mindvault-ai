import { apiClient } from './client';

export interface LoginRequest {
  email: string;
  password: string;
  org_slug?: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  organization_name: string;
}

// Register response - doesn't include tokens
export interface RegisterResponse {
  user_id: string;
  default_org_id: string;
}

// Login response - includes tokens
export interface TokenPairResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// /auth/me response
export interface MeResponse {
  user_id: string;
  org_id: string;
  role: string;
}

/**
 * Authentication service methods
 * Handles all auth-related API calls
 */
export const authService = {
  /**
   * Register a new user and organization
   * Returns user_id and org_id (not tokens)
   * User must login separately
   */
  register: (data: RegisterRequest) =>
    apiClient.post<RegisterResponse>('/auth/register', data),

  /**
   * Login user and get tokens
   * Returns access_token and refresh_token
   */
  login: (data: LoginRequest) =>
    apiClient.post<TokenPairResponse>('/auth/login', data),

  /**
   * Get current user info from access token
   * Returns: user_id, org_id, role
   */
  getMe: () =>
    apiClient.get<MeResponse>('/auth/me'),

  /**
   * Logout user (invalidates refresh token)
   */
  logout: () =>
    apiClient.post('/auth/logout'),

  /**
   * Refresh access token using refresh token
   */
  refresh: (refreshToken: string) =>
    apiClient.post<TokenPairResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    }),

  /**
   * Switch active organization
   */
  switchOrg: (targetOrgId: string) =>
    apiClient.post<TokenPairResponse & { active_org_id: string }>(
      '/auth/switch-org',
      { target_org_id: targetOrgId }
    ),
};

/**
 * Document service methods
 */
export const documentService = {
  list: (orgId: string) =>
    apiClient.get('/documents', { params: { org_id: orgId } }),

  get: (docId: string) =>
    apiClient.get(`/documents/${docId}`),

  create: (title: string, sourceType: string) =>
    apiClient.post('/documents', { title, source_type: sourceType }),

  delete: (docId: string) =>
    apiClient.delete(`/documents/${docId}`),

  upload: (file: File, docId: string) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post(`/documents/${docId}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

/**
 * Chat service methods
 */
export const chatService = {
  createSession: (title: string) =>
    apiClient.post('/chat/sessions', { title }),

  listSessions: () =>
    apiClient.get('/chat/sessions'),

  getSession: (sessionId: string) =>
    apiClient.get(`/chat/sessions/${sessionId}`),

  sendMessage: (sessionId: string, query: string) =>
    apiClient.post(`/chat/sessions/${sessionId}/messages`, { query }),
};

/**
 * Usage/Analytics service methods
 */
export const usageService = {
  getMetrics: (orgId: string) =>
    apiClient.get('/usage/metrics', { params: { org_id: orgId } }),

  getDocumentUsage: (docId: string) =>
    apiClient.get(`/usage/documents/${docId}`),
};
