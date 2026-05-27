'use client';

import { useEffect } from 'react';
import { useAuthStore } from '@/stores/authStore';

/**
 * AuthInitializer
 * Initializes auth store on app load by checking current session
 * This runs once when the app mounts to populate user state
 */
export function AuthInitializer() {
  const checkAuth = useAuthStore((state) => state.checkAuth);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return null; // This component doesn't render anything
}
