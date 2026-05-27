'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/cn';
import {
  Cloud,
  Sparkles,
  Database,
  MessageCircle,
  ChevronRight,
} from 'lucide-react';

const steps = [
  {
    number: '01',
    icon: Cloud,
    title: 'Upload & Process',
    description: 'Drop your PDFs, docs, and files. We automatically extract, clean, and chunk your content with zero manual work.',
    color: 'from-indigo-600 to-indigo-700',
    highlights: ['PDF, Markdown, Text', 'Auto-chunking', 'Batch uploads']
  },
  {
    number: '02',
    icon: Database,
    title: 'Embed & Index',
    description: 'Convert your documents into semantic embeddings. Store securely with row-level encryption and tenant isolation.',
    color: 'from-violet-600 to-violet-700',
    highlights: ['Vector database', 'Encrypted storage', 'Metadata indexing']
  },
  {
    number: '03',
    icon: Sparkles,
    title: 'Semantic Search',
    description: 'Ask questions in plain language. Our AI finds the most relevant chunks across all your documents instantly.',
    color: 'from-cyan-600 to-blue-600',
    highlights: ['Semantic matching', 'Multi-doc retrieval', 'Sub-100ms latency']
  },
  {
    number: '04',
    icon: MessageCircle,
    title: 'Get Cited Answers',
    description: 'Receive streaming, grounded answers with direct citations. Every claim traces back to your source documents.',
    color: 'from-teal-600 to-cyan-600',
    highlights: ['Streaming responses', 'Source citations', 'Fact-grounded']
  },
];

export function HowItWorks() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
        duration: 0.6,
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
      id="how-it-works"
      className={cn(
        'relative w-full py-20 md:py-32',
        'bg-slate-950 px-6 overflow-hidden'
      )}
    >
      {/* Background Elements */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <motion.div
          animate={{
            y: [0, 100, 0],
            opacity: [0.1, 0.3, 0.1],
          }}
          transition={{ duration: 12, repeat: Infinity }}
          className={cn(
            'absolute -top-40 right-0 w-96 h-96',
            'bg-linear-to-br from-cyan-600/20 to-indigo-600/10',
            'rounded-full blur-3xl'
          )}
        />
        <motion.div
          animate={{
            y: [0, -100, 0],
            opacity: [0.1, 0.25, 0.1],
          }}
          transition={{ duration: 15, repeat: Infinity, delay: 1 }}
          className={cn(
            'absolute -bottom-40 left-0 w-96 h-96',
            'bg-linear-to-tr from-indigo-600/15 to-cyan-600/10',
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
        <motion.div variants={itemVariants} className="text-center mb-20">
          <h2 className={cn(
            'text-4xl md:text-5xl font-bold mb-4',
            'bg-linear-to-r from-slate-50 to-cyan-400',
            'bg-clip-text text-transparent'
          )}>
            From Docs to Intelligence in 4 Steps
          </h2>
          <p className="text-lg text-slate-400 max-w-2xl mx-auto">
            Our pipeline handles everything. No setup, no infrastructure headaches—just upload, ask, and get answers.
          </p>
        </motion.div>

        {/* Steps Grid */}
        <motion.div
          variants={containerVariants}
          className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12"
        >
          {steps.map((step, idx) => {
            const Icon = step.icon;
            return (
              <motion.div
                key={step.number}
                variants={itemVariants}
                className="group"
              >
                <div className={cn(
                  'relative h-full rounded-2xl p-8',
                  'bg-linear-to-br from-white/5 to-white/0',
                  'border border-slate-700/30 hover:border-cyan-400/40',
                  'transition-all duration-300',
                  'backdrop-blur-sm hover:bg-white/8'
                )}>
                  {/* Glow border top on hover */}
                  <div className={cn(
                    'absolute top-0 left-1/4 right-1/4 h-px',
                    'bg-linear-to-r from-transparent via-cyan-400/0 to-transparent',
                    'group-hover:via-cyan-400/60 transition-all duration-300'
                  )} />

                  {/* Step Number */}
                  <div className="flex items-start justify-between mb-6">
                    <motion.div
                      whileHover={{ scale: 1.05, rotate: 5 }}
                      className={cn(
                        'w-14 h-14 rounded-xl',
                        `bg-linear-to-br ${step.color}`,
                        'flex items-center justify-center text-white font-bold text-xl',
                        'shadow-lg shadow-indigo-500/30 group-hover:shadow-lg group-hover:shadow-cyan-500/40',
                        'transition-all duration-300'
                      )}
                    >
                      <Icon size={24} />
                    </motion.div>

                    {/* Connector Arrow (except last) */}
                    {idx < steps.length - 1 && (
                      <motion.div
                        animate={{ x: [0, 8, 0] }}
                        transition={{ duration: 2, repeat: Infinity, delay: idx * 0.3 }}
                        className="hidden md:block absolute -right-5 top-1/2 -translate-y-1/2 text-cyan-500/40"
                      >
                        <ChevronRight size={24} />
                      </motion.div>
                    )}
                  </div>

                  {/* Step Number Text */}
                  <p className="text-xs font-mono text-slate-500 mb-3">
                    STEP {step.number}
                  </p>

                  {/* Title */}
                  <h3 className="text-xl font-bold text-slate-50 mb-3">
                    {step.title}
                  </h3>

                  {/* Description */}
                  <p className="text-sm text-slate-400 leading-relaxed mb-6">
                    {step.description}
                  </p>

                  {/* Highlights */}
                  <div className="flex flex-wrap gap-2">
                    {step.highlights.map((highlight) => (
                      <motion.span
                        key={highlight}
                        whileHover={{ y: -2 }}
                        className={cn(
                          'text-xs px-3 py-1.5 rounded-full',
                          'bg-white/5 text-slate-300',
                          'border border-slate-700/40 hover:border-cyan-400/50',
                          'transition-all duration-200 group-hover:bg-white/10',
                          'font-medium'
                        )}
                      >
                        {highlight}
                      </motion.span>
                    ))}
                  </div>
                </div>
              </motion.div>
            );
          })}
        </motion.div>

        {/* Stats Row */}
        <motion.div
          variants={itemVariants}
          className={cn(
            'grid grid-cols-3 gap-4 md:gap-8',
            'mt-16 pt-16 border-t border-slate-700/30'
          )}
        >
          {[
            { value: '100MB+', label: 'Document capacity per org' },
            { value: '<500ms', label: 'Average query response time' },
            { value: '99.9%', label: 'Data security guarantee' },
          ].map((stat, i) => (
            <motion.div
              key={i}
              whileHover={{ y: -4 }}
              className="text-center"
            >
              <motion.p
                className={cn(
                  'text-2xl md:text-3xl font-bold mb-2',
                  'bg-linear-to-r from-indigo-400 to-cyan-400',
                  'bg-clip-text text-transparent'
                )}
              >
                {stat.value}
              </motion.p>
              <p className="text-xs md:text-sm text-slate-400">
                {stat.label}
              </p>
            </motion.div>
          ))}
        </motion.div>
      </motion.div>
    </section>
  );
}
