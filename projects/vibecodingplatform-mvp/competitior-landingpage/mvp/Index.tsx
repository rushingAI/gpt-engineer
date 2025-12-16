import React from 'react';
import { HeroSection } from '@/components/landingpage/heroSection';
import { FeaturesSection } from '@/components/landingpage/featuresSection';
import { TestimonialsSection } from '@/components/landingpage/testimonialsSection';
import { CallToActionSection } from '@/components/landingpage/callToActionSection';
import { Footer } from '@/components/landingpage/footer';

export default function Index() {
  return (
    <div className="bg-gradient-to-br from-green-400 to-green-600">
      <HeroSection />
      <FeaturesSection />
      <TestimonialsSection />
      <CallToActionSection />
      <Footer />
    </div>
  );
}
