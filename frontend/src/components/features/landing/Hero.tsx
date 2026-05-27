'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { cn } from '@/lib/cn';
import { ArrowRight, Lock, Zap, FileText } from 'lucide-react';

export function Hero() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.12,
        delayChildren: 0.2,
        duration: 0.5,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: 'spring' as const,
        stiffness: 100,
        damping: 15,
      },
    },
  };

  return (
    <section className={cn(
      'relative min-h-screen w-full',
      'bg-slate-950 overflow-hidden',
      'flex items-center justify-center px-6 py-20 md:py-0'
    )}>
      {/* Gradient Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          animate={{
            y: [0, 50, 0],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{ duration: 8, repeat: Infinity }}
          className={cn(
            'absolute -top-40 -right-40 w-96 h-96',
            'bg-linear-to-br from-indigo-600/40 to-cyan-400/20',
            'rounded-full blur-3xl'
          )}
        />
        <motion.div
          animate={{
            y: [0, -50, 0],
            opacity: [0.2, 0.4, 0.2],
          }}
          transition={{ duration: 10, repeat: Infinity, delay: 1 }}
          className={cn(
            'absolute -bottom-40 -left-40 w-96 h-96',
            'bg-linear-to-tr from-cyan-400/20 to-indigo-600/30',
            'rounded-full blur-3xl'
          )}
        />
      </div>

      {/* Content */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className={cn(
          'relative z-10 max-w-4xl mx-auto text-center',
          'space-y-8'
        )}
      >
        {/* Badge */}
        <motion.div
          variants={itemVariants}
          className="flex justify-center"
        >
          <a href="#demo" className={cn(
            'group inline-flex items-center gap-2 px-4 py-2 rounded-full',
            'bg-white/5 border border-slate-700/50',
            'backdrop-blur-sm text-sm text-slate-300',
            'hover:bg-white/10 hover:border-cyan-400/50',
            'transition-all duration-300'
          )}>
            <motion.span
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 2.5, repeat: Infinity }}
              className="inline-block w-2 h-2 bg-cyan-400 rounded-full"
            />
            <span>See it in action</span>
            <ArrowRight size={14} className="group-hover:translate-x-0.5 transition-transform" />
          </a>
        </motion.div>

        {/* Main Headline */}
        <motion.div variants={itemVariants} className="space-y-4">
          <h1 className={cn(
            'text-5xl md:text-6xl lg:text-7xl font-bold leading-tight',
            'bg-linear-to-r from-slate-50 via-indigo-300 to-cyan-400',
            'bg-clip-text text-transparent',
            'tracking-tight'
          )}>
            Your Knowledge Base Answers Questions
          </h1>
        </motion.div>

        {/* Sub-headline - More Human */}
        <motion.p
          variants={itemVariants}
          className={cn(
            'text-lg md:text-xl max-w-2xl mx-auto',
            'text-slate-300 leading-relaxed'
          )}
        >
          Stop digging through documents. Upload your files and ask questions in natural language. Get answers grounded in your actual content, with instant citations.
        </motion.p>

        {/* CTA Buttons */}
        <motion.div
          variants={itemVariants}
          className="flex flex-col sm:flex-row gap-4 justify-center pt-4"
        >
          <Link href="/register">
            <motion.button
              whileHover={{ scale: 1.05, boxShadow: '0 0 30px rgba(79, 70, 229, 0.6)' }}
              whileTap={{ scale: 0.95 }}
              className={cn(
                'px-8 py-4 rounded-lg font-semibold',
                'bg-linear-to-r from-indigo-600 to-cyan-400',
                'text-white shadow-lg shadow-indigo-500/50',
                'hover:shadow-xl hover:shadow-indigo-500/75',
                'transition-all duration-300',
                'flex items-center gap-2 justify-center'
              )}
            >
              Start Free Trial
              <ArrowRight size={20} />
            </motion.button>
          </Link>
          <Link href="#demo">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className={cn(
                'px-8 py-4 rounded-lg font-semibold',
                'bg-white/10 border border-slate-700/50 hover:border-cyan-400/50',
                'text-slate-50 backdrop-blur-sm',
                'hover:bg-white/15 transition-all duration-300',
                'flex items-center gap-2 justify-center'
              )}
            >
              Watch Demo
              <ArrowRight size={20} />
            </motion.button>
          </Link>
        </motion.div>

        {/* Trust Indicators - More Concrete */}
        <motion.div
          variants={itemVariants}
          className={cn(
            'grid grid-cols-1 md:grid-cols-3 gap-6 pt-8',
            'max-w-2xl mx-auto'
          )}
        >
          {[
            { icon: Zap, label: 'Lightning Fast', desc: 'Answers in seconds, not hours' },
            { icon: Lock, label: 'Your Data Stays Yours', desc: 'End-to-end encrypted' },
            { icon: FileText, label: 'Always Cited', desc: 'Every answer links to sources' },
          ].map((item, i) => (
            <motion.div
              key={item.label}
              variants={itemVariants}
              className={cn(
                'p-4 rounded-lg',
                'bg-white/5 border border-slate-700/30',
                'backdrop-blur-sm hover:bg-white/10 hover:border-cyan-400/30',
                'transition-all duration-300'
              )}
            >
              <motion.div
                whileHover={{ scale: 1.1, rotate: 10 }}
                className="flex justify-center mb-3"
              >
                <item.icon className="w-6 h-6 text-cyan-400" />
              </motion.div>
              <p className="font-semibold text-slate-200 mb-1">{item.label}</p>
              <p className="text-sm text-slate-400">{item.desc}</p>
            </motion.div>
          ))}
        </motion.div>
      </motion.div>

      {/* Scroll Indicator */}
      <motion.div
        animate={{ y: [0, 10, 0] }}
        transition={{ duration: 2.5, repeat: Infinity }}
        className={cn(
          'absolute bottom-8 left-1/2 -translate-x-1/2',
          'text-slate-400 text-sm'
        )}
      >
        <p>Explore features</p>
        <div className="flex justify-center mt-2">
          <motion.div className="w-1 h-6 rounded-full bg-linear-to-b from-cyan-400 to-transparent" />
        </div>
      </motion.div>
    </section>
  );
}
