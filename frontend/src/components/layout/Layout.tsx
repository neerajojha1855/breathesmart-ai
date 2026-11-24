import React from 'react';
import { Footer } from './Footer';
import { Navbar } from './Navbar';

export const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
      <a href="#main-content" className="skip-to-content">
        Skip to main content
      </a>

      <Navbar />

      <main id="main-content" role="main" className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {children}
      </main>

      <Footer />
    </div>
  );
};
