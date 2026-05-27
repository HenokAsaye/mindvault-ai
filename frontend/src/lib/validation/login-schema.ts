/**
 * Login form validation schema
 * Based on backend /api/v1/auth/login requirements
 */

import { z } from 'zod';

export const loginSchema = z.object({
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Please enter a valid email address'),
  password: z
    .string()
    .min(1, 'Password is required')
    .min(6, 'Password must be at least 6 characters'),
  org_slug: z
    .string()
    .optional(),
});

export type LoginInput = z.infer<typeof loginSchema>;
