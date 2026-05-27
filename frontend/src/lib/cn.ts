/**
 * Class Name Utility - Merge Tailwind CSS classes
 * Using clsx and tailwind-merge for optimal CSS performance
 */

import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
