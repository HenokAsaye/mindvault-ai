import { Navbar } from '@/components/features/landing/Navbar';
import { Hero } from '@/components/features/landing/Hero';
import { Features } from '@/components/features/landing/Features';
import { DemoMockup } from '@/components/features/landing/DemoMockup';
import { HowItWorks } from '@/components/features/landing/HowItWorks';
import { Pricing } from '@/components/features/landing/Pricing';
import { Footer } from '@/components/features/landing/Footer';

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-slate-950">
      <Navbar />
      <main className="flex-1">
        <Hero />
        <Features />
        <DemoMockup />
        <HowItWorks />
        <Pricing />
      </main>
      <Footer />
    </div>
  );
}
