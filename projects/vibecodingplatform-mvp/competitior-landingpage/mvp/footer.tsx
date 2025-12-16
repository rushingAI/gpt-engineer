import React from 'react';
import { Facebook, Twitter, Instagram } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-white py-8 border-t border-gray-200">
      <div className="max-w-7xl mx-auto px-4 flex flex-col md:flex-row justify-between items-center">
        <div className="text-center md:text-left mb-4 md:mb-0">
          <p className="text-gray-600">&copy; 2023 Your Company. All rights reserved.</p>
        </div>
        <div className="flex gap-4">
          <a href="#" aria-label="Facebook">
            <Facebook className="w-6 h-6 text-gray-600 hover:text-lovable-orange" />
          </a>
          <a href="#" aria-label="Twitter">
            <Twitter className="w-6 h-6 text-gray-600 hover:text-lovable-orange" />
          </a>
          <a href="#" aria-label="Instagram">
            <Instagram className="w-6 h-6 text-gray-600 hover:text-lovable-orange" />
          </a>
        </div>
      </div>
    </footer>
  );
}
