'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { cn } from '@/lib/cn';

export function Navbar() {
  return (
    <motion.nav
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className={cn(
        'fixed top-0 left-0 right-0 z-50',
        'bg-slate-950/80 backdrop-blur-xl border-b border-slate-900/50',
        'px-6 py-4'
      )}
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 group">
          <motion.div
            whileHover={{ scale: 1.05 }}
            className={cn(
              'w-10 h-10 rounded-lg',
              'bg-linear-to-br from-indigo-600 to-cyan-400',
              'flex items-center justify-center font-bold text-white',
              'shadow-lg shadow-indigo-500/50'
            )}
          >
            MV
          </motion.div>
          <span className="text-xl font-bold bg-linear-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
            MindVault
          </span>
        </Link>

        {/* Navigation Links */}
        <div className="hidden md:flex items-center gap-8">
          {[
            { label: 'Features', href: '/#features' },
            { label: 'Pricing', href: '/#pricing' },
          ].map((link, i) => (
            <motion.div
              key={link.label}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * (i + 1), duration: 0.5 }}
            >
              <Link
                href={link.href}
                className={cn(
                  'text-slate-300 hover:text-cyan-400 transition-colors duration-300',
                  'font-medium relative group'
                )}
              >
                {link.label}
                <span
                  className={cn(
                    'absolute bottom-0 left-0 w-0 h-0.5',
                    'bg-linear-to-r from-indigo-600 to-cyan-400',
                    'group-hover:w-full transition-all duration-300'
                  )}
                />
              </Link>
            </motion.div>
          ))}
        </div>

        {/* Sign In Button */}
        <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3, duration: 0.5 }}
          >
            <Link
              href="/login"
              className={cn(
                'px-6 py-2.5 rounded-lg font-semibold',
                'bg-white/10 hover:bg-white/20',
                'border border-slate-700 hover:border-cyan-400/50',
                'text-slate-50 transition-all duration-300',
                'backdrop-blur-sm'
              )}
            >
              Sign In
            </Link>
          </motion.div>
      </div>
    </motion.nav>
  );
}
