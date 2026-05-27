'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { LoginForm } from '@/components/features/auth';
import { useAuth } from '@/hooks';
import { cn } from '@/lib/utils';
import { Check } from 'lucide-react';

export default function LoginPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  // Redirect if already authenticated
  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, isLoading, router]);

  const features = [
    'Tenant-isolated · AES-256 at rest · TLS 1.3 in transit',
    'Async ingestion — upload 100 PDFs without blocking',
    'GPT-4o answers with streaming, cited responses'
  ];

  return (
    <div className="min-h-screen bg-slate-950">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-0">
        {/* Left Column - Login Form */}
        <div className={cn(
          'flex items-center justify-center px-6 py-20',
          'min-h-screen lg:min-h-auto'
        )}>
          <div className={cn(
            'w-full max-w-md'
          )}>
            <h1 className="text-3xl font-bold text-slate-50 mb-2">Sign In</h1>
            <p className="text-slate-400 mb-8">Welcome back to MindVault</p>
            <LoginForm />
          </div>
        </div>

        {/* Right Column - Marketing Content */}
        <div className={cn(
          'hidden lg:flex flex-col items-center justify-center px-8 py-20',
          'bg-gradient-to-br from-slate-900 to-slate-800',
          'border-l border-slate-700/30'
        )}>
          <div className="max-w-sm space-y-12">
            <div>
              <h2 className="text-4xl font-bold text-slate-50 mb-2">
                Your team's knowledge,
              </h2>
              <p className="text-3xl font-bold bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
                answered with citations.
              </p>
            </div>

            <div className="space-y-4">
              {features.map((feature, idx) => (
                <div key={idx} className="flex gap-3">
                  <div className="flex-shrink-0 mt-1">
                    <div className="flex items-center justify-center h-5 w-5 rounded-full bg-cyan-400/20 text-cyan-400">
                      <Check size={16} />
                    </div>
                  </div>
                  <p className="text-slate-300 text-sm leading-relaxed">{feature}</p>
                </div>
              ))}
            </div>

            <div className="pt-8 border-t border-slate-700/30">
              <p className="text-slate-400 italic mb-4 leading-relaxed">
                "MindVault replaced our internal wiki search the day we plugged it in. Engineering, sales, and support now ask the same vault — and get answers grounded in our own docs."
              </p>
              
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
