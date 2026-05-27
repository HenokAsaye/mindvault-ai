'use client';

import { cn } from '@/lib/utils';
import { AlertCircle, X } from 'lucide-react';

interface ErrorMessageProps {
  message: string;
  type?: 'error' | 'warning' | 'info';
  dismissible?: boolean;
  onDismiss?: () => void;
}

/**
 * Shared error message component for displaying user-friendly error messages
 * Handles backend errors, validation errors, and other feedback
 */
export function ErrorMessage({
  message,
  type = 'error',
  dismissible = true,
  onDismiss,
}: ErrorMessageProps) {
  // Sanitize and humanize backend error messages
  const humanizedMessage = sanitizeErrorMessage(message);

  const bgColor = {
    error: 'bg-red-500/10 border-red-500/50 text-red-400',
    warning: 'bg-yellow-500/10 border-yellow-500/50 text-yellow-400',
    info: 'bg-blue-500/10 border-blue-500/50 text-blue-400',
  }[type];

  return (
    <div className={cn('p-3 rounded-lg border', bgColor)}>
      <div className="flex items-start gap-3">
        <AlertCircle size={18} className="mt-0.5 flex-shrink-0" />
        <p className="text-sm flex-1">{humanizedMessage}</p>
        {dismissible && onDismiss && (
          <button
            onClick={onDismiss}
            className="text-current hover:opacity-70 transition-opacity flex-shrink-0"
          >
            <X size={16} />
          </button>
        )}
      </div>
    </div>
  );
}

/**
 * Convert raw backend error messages to user-friendly messages
 */
function sanitizeErrorMessage(message: string): string {
  // Handle null/undefined
  if (!message) {
    return 'An error occurred. Please try again.';
  }

  const msg = message.toLowerCase();

  // Password byte length error (multiple variations)
  if (
    msg.includes('password') && 
    (msg.includes('72 bytes') || msg.includes('longer than 72') || msg.includes('byte'))
  ) {
    return 'Your password is too long. Please use a password with 72 bytes or less. (Note: some special characters like emoji count as multiple bytes)';
  }

  // Email already exists
  if (msg.includes('email') && (msg.includes('already') || msg.includes('exists'))) {
    return 'This email is already registered. Please try logging in or use a different email.';
  }

  // Invalid credentials
  if (msg.includes('invalid') || msg.includes('incorrect') || msg.includes('credentials')) {
    return 'Invalid email or password. Please check and try again.';
  }

  // Network/server errors
  if (msg.includes('network') || msg.includes('failed to fetch')) {
    return 'Connection error. Please check your internet and try again.';
  }

  // Generic server error
  if (msg.includes('500') || msg.includes('internal server')) {
    return 'Something went wrong on our end. Please try again later.';
  }

  // Default: return original message
  return message;
}
