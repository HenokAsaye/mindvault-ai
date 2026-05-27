'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/cn';
import { ArrowUp, FileText, Sparkles, Link as LinkIcon } from 'lucide-react';

export function DemoMockup() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
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
    <section
      id="demo"
      className={cn(
        'relative w-full py-20 md:py-32',
        'bg-slate-950 px-6 overflow-hidden'
      )}
    >
      {/* Background Elements */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <motion.div
          animate={{
            x: [-100, 100, -100],
            opacity: [0.2, 0.4, 0.2],
          }}
          transition={{ duration: 12, repeat: Infinity }}
          className={cn(
            'absolute top-1/2 left-0 w-96 h-96',
            'bg-linear-to-r from-indigo-600/20 to-transparent',
            'rounded-full blur-3xl'
          )}
        />
      </div>

      <motion.div
        variants={containerVariants}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: '-100px' }}
        className="relative z-10 max-w-6xl mx-auto"
      >
        {/* Section Header */}
        <motion.div variants={itemVariants} className="text-center mb-16">
          <h2 className={cn(
            'text-4xl md:text-5xl font-bold mb-4',
            'bg-linear-to-r from-slate-50 to-cyan-400',
            'bg-clip-text text-transparent'
          )}>
            See Intelligence in Action
          </h2>
          <p className="text-lg text-slate-400 max-w-2xl mx-auto">
            Ask questions in natural language. Get answers grounded in your documents with instant citations.
          </p>
        </motion.div>

        {/* Demo Container */}
        <motion.div variants={itemVariants} className="mt-12">
          <div className={cn(
            'rounded-2xl border border-slate-700/40',
            'bg-linear-to-b from-slate-900/60 to-slate-950/80',
            'backdrop-blur-xl overflow-hidden',
            'shadow-2xl shadow-indigo-500/10'
          )}>
            {/* Window Header */}
            <div className={cn(
              'flex items-center justify-between px-6 py-4',
              'border-b border-slate-700/30 bg-white/3'
            )}>
              <div className="flex items-center gap-3">
                <div className="flex gap-1.5">
                  <div className="h-2.5 w-2.5 rounded-full bg-red-500/70" />
                  <div className="h-2.5 w-2.5 rounded-full bg-yellow-500/70" />
                  <div className="h-2.5 w-2.5 rounded-full bg-green-500/70" />
                </div>
                <span className="text-sm font-mono text-slate-400 ml-3">
                  Acme Corp Knowledge Base
                </span>
              </div>
              <div className="flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-3 py-1">
                <span className="text-xs font-semibold text-cyan-400">Active</span>
                <span className="h-1.5 w-1.5 rounded-full bg-cyan-400 animate-pulse" />
              </div>
            </div>

            {/* Chat Content */}
            <div className="p-6 space-y-6 max-h-150 overflow-y-auto">
              {/* User Question */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                viewport={{ once: true }}
                className="flex justify-end"
              >
                <div className={cn(
                  'max-w-xs lg:max-w-md px-4 py-3 rounded-2xl',
                  'bg-linear-to-br from-indigo-600/80 to-indigo-700/60',
                  'text-white text-sm leading-relaxed',
                  'shadow-lg shadow-indigo-500/30'
                )}>
                  What's our policy on remote work?
                </div>
              </motion.div>

              {/* AI Response */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                viewport={{ once: true }}
                className="flex justify-start"
              >
                <div className={cn(
                  'max-w-xs lg:max-w-2xl space-y-4',
                )}>
                  {/* Response with Sparkles */}
                  <div className={cn(
                    'px-4 py-3 rounded-2xl',
                    'bg-linear-to-br from-slate-800/60 to-slate-900/40',
                    'border border-slate-700/40',
                    'text-slate-200 text-sm leading-relaxed'
                  )}>
                    <div className="flex items-start gap-2 mb-3">
                      <Sparkles className="h-4 w-4 text-cyan-400 mt-0.5 shrink-0 animate-pulse" />
                      <p>
                        Acme Corp supports flexible remote work arrangements. Employees are eligible for up to <span className="font-semibold text-slate-100">3 days per week</span> remote work after completing their probation period.
                      </p>
                    </div>
                    <p className="ml-6">
                      The policy requires at least <span className="font-semibold text-slate-100">2 days in-office weekly</span> for team collaboration and culture building.
                    </p>
                  </div>

                  {/* Citations */}
                  <div className="space-y-2 ml-2">
                    <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                      Based on:
                    </p>
                    {[
                      {
                        title: 'Employee Handbook 2024',
                        page: 'page 24',
                        excerpt: '"Remote work eligibility begins after 90-day probation period..."'
                      },
                      {
                        title: 'HR Policy Guidelines',
                        page: 'page 8',
                        excerpt: '"Minimum 2 days per week in-office requirement..."'
                      },
                    ].map((citation, idx) => (
                      <motion.a
                        key={idx}
                        href="#"
                        whileHover={{ x: 4 }}
                        className={cn(
                          'flex items-start gap-3 p-2.5 rounded-lg',
                          'bg-white/4 hover:bg-white/8',
                          'border border-slate-700/30 hover:border-cyan-500/40',
                          'transition-all duration-200 group'
                        )}
                      >
                        <FileText className="h-4 w-4 text-cyan-400 mt-0.5 shrink-0 group-hover:scale-110 transition-transform" />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <p className="text-xs font-semibold text-slate-300 group-hover:text-cyan-400 transition-colors">
                              {citation.title}
                            </p>
                            <span className="text-xs text-slate-500 font-mono">
                              {citation.page}
                            </span>
                          </div>
                          <p className="text-xs text-slate-400 mt-1 line-clamp-1">
                            {citation.excerpt}
                          </p>
                        </div>
                        <LinkIcon className="h-3.5 w-3.5 text-slate-500 shrink-0 group-hover:text-cyan-400 transition-colors" />
                      </motion.a>
                    ))}
                  </div>
                </div>
              </motion.div>
            </div>

            {/* Input Area */}
            <div className={cn(
              'px-6 py-4 border-t border-slate-700/30',
              'bg-linear-to-t from-slate-950 to-slate-900/50'
            )}>
              <div className={cn(
                'flex items-center gap-3',
                'px-4 py-3 rounded-full',
                'bg-white/5 border border-slate-700/50',
                'hover:bg-white/8 hover:border-cyan-500/30',
                'transition-all duration-200'
              )}>
                <input
                  type="text"
                  placeholder="Ask anything about your documents..."
                  disabled
                  className={cn(
                    'flex-1 bg-transparent outline-none',
                    'text-slate-300 placeholder-slate-500',
                    'text-sm'
                  )}
                />
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                  className={cn(
                    'p-2 rounded-full',
                    'bg-linear-to-r from-indigo-600 to-cyan-500',
                    'text-white hover:shadow-lg hover:shadow-indigo-500/50',
                    'transition-all duration-200'
                  )}
                >
                  <ArrowUp size={16} />
                </motion.button>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Trust Info */}
        <motion.div
          variants={itemVariants}
          className={cn(
            'mt-12 flex flex-col sm:flex-row items-center justify-center gap-8',
            'text-sm text-slate-400'
          )}
        >
          <span className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-cyan-400" />
            Citations powered by semantic search
          </span>
          <span className="hidden sm:block w-1 h-1 rounded-full bg-slate-700" />
          <span className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-cyan-400" />
            100% data stays private & encrypted
          </span>
        </motion.div>
      </motion.div>
    </section>
  );
}
