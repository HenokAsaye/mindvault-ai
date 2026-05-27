'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { cn } from '@/lib/cn';
import { Check } from 'lucide-react';

const pricingTiers = [
  {
    name: 'Free',
    price: 0,
    period: 'forever',
    description: 'Perfect for individuals exploring AI-powered document search',
    cta: 'Get Started',
    ctaHref: '/register',
    featured: false,
    features: [
      'Up to 5 documents',
      '100 monthly searches',
      'Basic security',
      'Email support',
      'PDF & text files only',
    ],
  },
  {
    name: 'Pro',
    price: 29,
    period: '/month',
    description: 'Everything you need for team collaboration and productivity',
    cta: 'Start Free Trial',
    ctaHref: '/register',
    featured: true,
    features: [
      'Unlimited documents',
      'Unlimited searches',
      'Advanced security & encryption',
      'Priority support',
      'All file formats (PDF, MD, TXT, DOCX)',
      'Team collaboration (up to 5 users)',
      'Custom organization branding',
      'Usage analytics & insights',
      'API access',
    ],
  },
  {
    name: 'Enterprise',
    price: null,
    period: 'custom',
    description: 'For large organizations with specific security & compliance needs',
    cta: 'Contact Sales',
    ctaHref: '/contact',
    featured: false,
    features: [
      'Everything in Pro',
      'Unlimited team members',
      'SSO & SAML integration',
      'Advanced compliance (SOC 2, HIPAA)',
      'Dedicated account manager',
      'Custom SLA & uptime guarantees',
      'Self-hosted option',
      'Advanced audit logs',
      'Custom integrations',
    ],
  },
];

export function Pricing() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
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
      id="pricing"
      className={cn(
        'relative w-full py-20 md:py-32',
        'bg-slate-950 overflow-hidden',
        'px-6'
      )}
    >
      {/* Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          animate={{
            y: [0, 50, 0],
            opacity: [0.2, 0.3, 0.2],
          }}
          transition={{ duration: 10, repeat: Infinity }}
          className={cn(
            'absolute -top-40 right-0 w-96 h-96',
            'bg-linear-to-br from-indigo-600/30 to-cyan-400/10',
            'rounded-full blur-3xl'
          )}
        />
      </div>

      {/* Content */}
      <div className="relative z-10 max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16 md:mb-20"
        >
          <h2 className={cn(
            'text-4xl md:text-5xl font-bold mb-6',
            'bg-linear-to-r from-slate-50 to-cyan-400',
            'bg-clip-text text-transparent'
          )}>
            Simple, Transparent Pricing
          </h2>
          <p className={cn(
            'text-lg text-slate-400 max-w-2xl mx-auto',
            'leading-relaxed'
          )}>
            Choose the plan that fits your needs. Upgrade or downgrade anytime.
            All plans include a 14-day free trial.
          </p>
        </motion.div>

        {/* Pricing Cards */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-3 gap-8 lg:gap-6"
        >
          {pricingTiers.map((tier) => (
            <motion.div
              key={tier.name}
              variants={itemVariants}
              whileHover={{ y: -10 }}
              className={cn(
                'relative rounded-2xl p-8 md:p-10',
                'backdrop-blur-xl',
                'border',
                'transition-all duration-300',
                tier.featured
                  ? [
                    'bg-white/10 border-cyan-400/50',
                    'shadow-2xl shadow-cyan-500/20',
                    'ring-2 ring-cyan-400/30',
                    'scale-105 md:scale-110',
                  ]
                  : [
                    'bg-white/5 border-slate-700/50',
                    'hover:bg-white/8 hover:border-slate-600/50',
                  ]
              )}
            >
              {/* Featured Badge */}
              {tier.featured && (
                <motion.div
                  initial={{ opacity: 0, scale: 0 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.3 }}
                  className={cn(
                    'absolute -top-4 left-1/2 -translate-x-1/2',
                    'px-4 py-1 rounded-full',
                    'bg-linear-to-r from-indigo-600 to-cyan-400',
                    'text-white text-sm font-bold',
                    'shadow-lg shadow-cyan-500/50'
                  )}
                >
                  🌟 Most Popular
                </motion.div>
              )}

              {/* Plan Name */}
              <h3 className={cn(
                'text-2xl font-bold mb-2',
                tier.featured ? 'text-cyan-400' : 'text-slate-50'
              )}>
                {tier.name}
              </h3>

              {/* Description */}
              <p className="text-sm text-slate-400 mb-6 h-10">
                {tier.description}
              </p>

              {/* Price */}
              <div className="mb-8">
                {tier.price !== null ? (
                  <div className="flex items-baseline gap-2">
                    <span className={cn(
                      'text-5xl font-bold',
                      tier.featured ? 'text-cyan-400' : 'text-slate-50'
                    )}>
                      ${tier.price}
                    </span>
                    <span className="text-slate-400">
                      {tier.period}
                    </span>
                  </div>
                ) : (
                  <div className="text-2xl font-bold text-slate-50">
                    Custom Pricing
                  </div>
                )}
              </div>

              {/* CTA Button */}
              <Link href={tier.ctaHref} className="block mb-8">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className={cn(
                    'w-full py-3 px-6 rounded-lg font-semibold transition-all duration-300',
                    'flex items-center justify-center',
                    tier.featured
                      ? [
                        'bg-linear-to-r from-indigo-600 to-cyan-400',
                        'text-white shadow-lg shadow-indigo-500/50',
                        'hover:shadow-xl hover:shadow-indigo-500/75',
                      ]
                      : [
                        'bg-white/10 hover:bg-white/20',
                        'border border-slate-700 hover:border-cyan-400/50',
                        'text-slate-50',
                      ]
                  )}
                >
                  {tier.cta}
                </motion.button>
              </Link>

              {/* Divider */}
              <div className="h-px bg-linear-to-r from-slate-700/0 via-slate-700/50 to-slate-700/0 mb-8" />

              {/* Features List */}
              <ul className="space-y-4">
                {tier.features.map((feature) => (
                  <motion.li
                    key={feature}
                    initial={{ opacity: 0, x: -10 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.4 }}
                    viewport={{ once: true }}
                    className="flex items-start gap-3"
                  >
                    <Check
                      size={20}
                      className={cn(
                        'shrink-0 mt-0.5',
                        tier.featured
                          ? 'text-cyan-400'
                          : 'text-indigo-500'
                      )}
                    />
                    <span className="text-sm text-slate-300">
                      {feature}
                    </span>
                  </motion.li>
                ))}
              </ul>
            </motion.div>
          ))}
        </motion.div>

        {/* FAQ Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          viewport={{ once: true }}
          className="mt-20 md:mt-32 pt-16 border-t border-slate-900/50"
        >
          <h3 className={cn(
            'text-2xl md:text-3xl font-bold mb-12 text-center',
            'text-slate-50'
          )}>
            Common Questions
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-3xl mx-auto">
            {[
              {
                q: 'Can I change plans later?',
                a: 'Yes! You can upgrade, downgrade, or cancel your plan at any time with no penalties.',
              },
              {
                q: 'Is there a free trial?',
                a: 'Yes, all Pro and Enterprise plans include a 14-day free trial. No credit card required.',
              },
              {
                q: 'What payment methods do you accept?',
                a: 'We accept all major credit cards, ACH transfers, and wire transfers for Enterprise plans.',
              },
              {
                q: 'Do you offer discounts for annual billing?',
                a: 'Yes! Annual billing saves you 20% on Pro plans. Contact us for Enterprise discounts.',
              },
            ].map((faq, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: i * 0.1 }}
                viewport={{ once: true }}
                className={cn(
                  'p-6 rounded-xl',
                  'bg-white/5 border border-slate-700/50',
                  'hover:bg-white/8 transition-all duration-300'
                )}
              >
                <h4 className="font-semibold text-slate-50 mb-2">
                  {faq.q}
                </h4>
                <p className="text-sm text-slate-400">
                  {faq.a}
                </p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}
