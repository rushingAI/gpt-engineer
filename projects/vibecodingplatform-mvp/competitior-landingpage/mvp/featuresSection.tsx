import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { motion } from 'framer-motion';
import { Zap, Star, Heart } from 'lucide-react';

const features = [
  { icon: Zap, title: 'Feature 1', description: 'Description of feature 1' },
  { icon: Star, title: 'Feature 2', description: 'Description of feature 2' },
  { icon: Heart, title: 'Feature 3', description: 'Description of feature 3' },
];

export const FeaturesSection: React.FC = () => {
  return (
    <section className="py-20 md:py-32">
      <div className="max-w-7xl mx-auto px-4">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">Features</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <Card className="p-6 hover:shadow-xl transition-all duration-200 hover:scale-105">
                <div className="w-12 h-12 rounded-lg bg-lovable-orange/10 flex items-center justify-center mb-4">
                  <feature.icon className="w-6 h-6 text-lovable-orange" />
                </div>
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
