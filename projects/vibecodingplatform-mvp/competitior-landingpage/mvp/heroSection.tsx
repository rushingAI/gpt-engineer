import React from 'react';
import { Button } from '@/components/ui/button';
import { ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

export const HeroSection: React.FC = () => {
  return (
    <section className="min-h-screen flex items-center justify-center relative overflow-hidden">
      <motion.div 
        className="absolute top-1/4 left-1/4 w-64 h-64 rounded-full bg-green-400/10 blur-3xl"
        animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.5, 0.3] }}
        transition={{ duration: 8, repeat: Infinity }}
      />
      <div className="relative z-10 max-w-5xl mx-auto text-center px-4">
        <motion.h1 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-5xl md:text-7xl font-bold mb-6"
        >
          Build something <span className="text-gradient bg-gradient-to-r from-green-400 to-green-600 bg-clip-text text-transparent">extraordinary</span>
        </motion.h1>
        <motion.p 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="text-xl text-gray-600 mb-12"
        >
          Your compelling value proposition here
        </motion.p>
        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="flex gap-4 justify-center"
        >
          <Button size="lg" className="bg-gradient-to-r from-green-400 to-green-600">
            Get Started <ArrowRight className="ml-2" />
          </Button>
          <Button size="lg" variant="outline">
            Learn More
          </Button>
        </motion.div>
      </div>
    </section>
  );
}
