import React from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/layout/Layout';
import { LocationProvider } from './contexts/LocationContext';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <LocationProvider>
        <BrowserRouter>
          <Layout>
            <Routes>
              <Route
                path="/"
                element={
                  <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm text-center">
                    <h2 className="text-xl font-bold text-slate-900 mb-2">Air Quality Dashboard</h2>
                    <p className="text-slate-600 text-sm">Dashboard view ready for Phase 3.2 feature integration.</p>
                  </div>
                }
              />
              <Route
                path="/planner"
                element={
                  <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm text-center">
                    <h2 className="text-xl font-bold text-slate-900 mb-2">Personalized Daily Planner</h2>
                    <p className="text-slate-600 text-sm">Daily action planner view ready for Phase 3.2.</p>
                  </div>
                }
              />
              <Route
                path="/indoor"
                element={
                  <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm text-center">
                    <h2 className="text-xl font-bold text-slate-900 mb-2">Indoor Air Quality Advisor</h2>
                    <p className="text-slate-600 text-sm">Ventilation and purifier guidelines view ready for Phase 3.2.</p>
                  </div>
                }
              />
              <Route
                path="/sustainability"
                element={
                  <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm text-center">
                    <h2 className="text-xl font-bold text-slate-900 mb-2">Sustainable Lifestyle Planner</h2>
                    <p className="text-slate-600 text-sm">Commute emission comparison view ready for Phase 3.2.</p>
                  </div>
                }
              />
              <Route
                path="/assistant"
                element={
                  <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm text-center">
                    <h2 className="text-xl font-bold text-slate-900 mb-2">Conversational AI Assistant</h2>
                    <p className="text-slate-600 text-sm">Contextual air quality chat view ready for Phase 3.2.</p>
                  </div>
                }
              />
              <Route
                path="/profile"
                element={
                  <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm text-center">
                    <h2 className="text-xl font-bold text-slate-900 mb-2">Household Preferences</h2>
                    <p className="text-slate-600 text-sm">User preferences view ready for Phase 3.2.</p>
                  </div>
                }
              />
            </Routes>
          </Layout>
        </BrowserRouter>
      </LocationProvider>
    </QueryClientProvider>
  );
};

export default App;
