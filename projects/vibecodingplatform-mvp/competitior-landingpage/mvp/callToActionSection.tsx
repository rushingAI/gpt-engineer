import React from 'react';
import { Button } from '@/components/ui/button';
import { ArrowRight } from 'lucide-react';

export const CallToActionSection: React.FC = () => {
  return (
    <section className="py-20 md:py-32 bg-gradient-to-br from-green-400 to-green-600 text-white text-center">
      <div className="max-w-7xl mx-auto px-4">
        <h2 className="text-3xl md:text-4xl font-bold mb-6">Ready to get started?</h2>
        <p className="text-xl mb-12">Join us today and make a difference!</p>
        <Button className="bg-gradient-to-r from-green-400 to-green-600 text-white shadow-lg hover:shadow-xl">
          Sign Up Now <ArrowRight className="ml-2" />
        </Button>
      </div>
    </section>
  );
}
