import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { motion } from 'framer-motion';

const testimonials = [
  { name: 'John Doe', feedback: 'This product is amazing!', rating: 5 },
  { name: 'Jane Smith', feedback: 'I love using this every day!', rating: 4 },
  { name: 'Sam Wilson', feedback: 'Highly recommend to everyone!', rating: 5 },
];

export const TestimonialsSection: React.FC = () => {
  return (
    <section className="py-20 md:py-32 bg-gray-100">
      <div className="max-w-7xl mx-auto px-4">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">Testimonials</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <Card className="p-6 hover:shadow-xl transition-all duration-200 hover:scale-105">
                <h3 className="text-xl font-semibold mb-2">{testimonial.name}</h3>
                <p className="text-gray-600 mb-4">{testimonial.feedback}</p>
                <div className="flex">
                  {Array.from({ length: testimonial.rating }).map((_, i) => (
                    <span key={i} className="text-lovable-orange">★</span>
                  ))}
                </div>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
