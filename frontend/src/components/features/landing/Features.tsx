'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/cn';
import { 
  Upload, 
  Search, 
  MessageSquare, 
  Lock, 
  BarChart3, 
  Users 
} from 'lucide-react';

const features = [
  {
    icon: Upload,
    title: 'Smart Document Ingestion',
    description: 'Drop PDFs, docs, and text files. Automatic extraction, cleaning, and chunking—no setup required.',
  },
  {
    icon: Search,
    title: 'Semantic Search',
    description: 'Find the needle in the haystack. Search by meaning, not just keywords.',
  },
  {
    icon: MessageSquare,
    title: 'Cited Answers',
    description: 'Ask anything. Get grounded responses with direct links to source documents.',
  },
  {
    icon: Lock,
    title: 'Enterprise Security',
    description: 'Your data never leaves your tenant. End-to-end encryption, SOC 2 compliant.',
  },
  {
    icon: BarChart3,
    title: 'Usage Insights',
    description: 'Track what your team is using. Monitor costs, queries, and document storage in real-time.',
  },
  {
    icon: Users,
    title: 'Team Collaboration',
    description: 'Invite team members, manage permissions, and share knowledge bases safely.',
  },
];

export function Features() {
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
      id="features"
      className={cn(
        'relative w-full py-20 md:py-32',
        'bg-slate-950 px-6'
      )}
    >
      {/* Background Elements */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <motion.div
          animate={{
            x: [0, 100, 0],
            opacity: [0.2, 0.4, 0.2],
          }}
          transition={{ duration: 10, repeat: Infinity }}
          className={cn(
            'absolute top-1/2 right-0 w-96 h-96',
            'bg-linear-to-l from-indigo-600/20 to-transparent',
            'rounded-full blur-3xl'
          )}
        />
      </div>

      <motion.div
        variants={containerVariants}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: '-100px' }}
        className="relative z-10 max-w-7xl mx-auto"
      >
        {/* Section Header */}
        <motion.div variants={itemVariants} className="text-center mb-20">
          <h2 className={cn(
            'text-4xl md:text-5xl font-bold mb-6',
            'bg-linear-to-r from-slate-50 to-cyan-400',
            'bg-clip-text text-transparent'
          )}>
            Built for Real Work
          </h2>
          <p className="text-lg text-slate-400 max-w-3xl mx-auto leading-relaxed">
            Every feature is designed to eliminate friction. No complicated setup. No learning curve. Just upload and start asking questions.
          </p>
        </motion.div>

        {/* Features Grid */}
        <motion.div
          variants={containerVariants}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              variants={itemVariants}
              whileHover={{ y: -6 }}
              className={cn(
                'group p-8 rounded-xl',
                'bg-linear-to-br from-white/8 to-white/0',
                'border border-slate-700/30 hover:border-cyan-400/40',
                'backdrop-blur-sm',
                'transition-all duration-300',
                'relative overflow-hidden'
              )}
            >
              {/* Subtle glow on hover */}
              <div className={cn(
                'absolute inset-0 bg-linear-to-br from-cyan-400/0 to-indigo-600/0',
                'group-hover:from-cyan-400/5 group-hover:to-indigo-600/5',
                'transition-all duration-300 pointer-events-none'
              )} />

              {/* Content */}
              <div className="relative z-10">
                <motion.div
                  whileHover={{ scale: 1.1, rotate: 5 }}
                  className={cn(
                    'w-14 h-14 rounded-lg mb-5',
                    'bg-linear-to-br from-indigo-600 to-cyan-500',
                    'flex items-center justify-center text-white',
                    'shadow-lg shadow-indigo-500/40 group-hover:shadow-cyan-500/50',
                    'transition-all duration-300'
                  )}
                >
                  <feature.icon size={26} />
                </motion.div>

                <h3 className="text-xl font-bold text-slate-50 mb-3">
                  {feature.title}
                </h3>
                <p className="text-slate-400 leading-relaxed text-[15px]">
                  {feature.description}
                </p>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </motion.div>
    </section>
  );
}
