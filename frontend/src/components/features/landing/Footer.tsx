'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { cn } from '@/lib/cn';

const footerLinks = [
  {
    title: 'Product',
    links: [
      { label: 'Features', href: '#features' },
      { label: 'Pricing', href: '#pricing' },
      { label: 'Security', href: '#' },
    ],
  },
  {
    title: 'Company',
    links: [
      { label: 'About', href: '#' },
      { label: 'Blog', href: '#' },
      { label: 'Careers', href: '#' },
    ],
  },
  {
    title: 'Legal',
    links: [
      { label: 'Privacy', href: '#' },
      { label: 'Terms', href: '#' },
      { label: 'Contact', href: '#' },
    ],
  },
];

export function Footer() {
  return (
    <footer className={cn(
      'w-full py-12 md:py-16',
      'bg-slate-950 border-t border-slate-900/50',
      'px-6'
    )}>
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8"
        >
          {/* Brand */}
          <div className="space-y-4">
            <Link href="/" className="flex items-center gap-2 group">
              <div className={cn(
                'w-10 h-10 rounded-lg',
                'bg-gradient-to-br from-indigo-600 to-cyan-400',
                'flex items-center justify-center font-bold text-white'
              )}>
                MV
              </div>
              <span className="text-lg font-bold text-slate-50">MindVault</span>
            </Link>
            <p className="text-sm text-slate-400">
              Your team's collective intelligence, powered by AI.
            </p>
          </div>

          {/* Links */}
          {footerLinks.map((column) => (
            <div key={column.title} className="space-y-4">
              <h4 className="font-semibold text-slate-50">{column.title}</h4>
              <ul className="space-y-2">
                {column.links.map((link) => (
                  <li key={link.label}>
                    <motion.a
                      href={link.href}
                      whileHover={{ x: 4 }}
                      className="text-sm text-slate-400 hover:text-cyan-400 transition-colors"
                    >
                      {link.label}
                    </motion.a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </motion.div>

        {/* Bottom */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          viewport={{ once: true }}
          className={cn(
            'pt-8 border-t border-slate-900/50',
            'flex flex-col md:flex-row justify-between items-center',
            'text-sm text-slate-400'
          )}
        >
          <p>&copy; {new Date().getFullYear()} MindVault AI. All rights reserved.</p>
          <div className="flex gap-6 mt-4 md:mt-0">
            <a href="#" className="hover:text-cyan-400 transition-colors">Twitter</a>
            <a href="#" className="hover:text-cyan-400 transition-colors">GitHub</a>
            <a href="#" className="hover:text-cyan-400 transition-colors">LinkedIn</a>
          </div>
        </motion.div>
      </div>
    </footer>
  );
}
