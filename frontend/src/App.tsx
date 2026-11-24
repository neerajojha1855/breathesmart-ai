import React, { Suspense } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { LoadingSkeleton } from './components/common/LoadingSkeleton';
import { Layout } from './components/layout/Layout';
import { LocationProvider } from './contexts/LocationContext';

// Route-level code splitting for performance and fast initial load
const DashboardPage = React.lazy(() =>
  import('./pages/DashboardPage').then((m) => ({ default: m.DashboardPage }))
);
const PlannerPage = React.lazy(() =>
  import('./pages/PlannerPage').then((m) => ({ default: m.PlannerPage }))
);
const IndoorAdvisorPage = React.lazy(() =>
  import('./pages/IndoorAdvisorPage').then((m) => ({ default: m.IndoorAdvisorPage }))
);
const SustainabilityPage = React.lazy(() =>
  import('./pages/SustainabilityPage').then((m) => ({ default: m.SustainabilityPage }))
);
const AssistantPage = React.lazy(() =>
  import('./pages/AssistantPage').then((m) => ({ default: m.AssistantPage }))
);
const ProfilePage = React.lazy(() =>
  import('./pages/ProfilePage').then((m) => ({ default: m.ProfilePage }))
);

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
            <Suspense fallback={<LoadingSkeleton />}>
              <Routes>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/planner" element={<PlannerPage />} />
                <Route path="/indoor" element={<IndoorAdvisorPage />} />
                <Route path="/sustainability" element={<SustainabilityPage />} />
                <Route path="/assistant" element={<AssistantPage />} />
                <Route path="/profile" element={<ProfilePage />} />
              </Routes>
            </Suspense>
          </Layout>
        </BrowserRouter>
      </LocationProvider>
    </QueryClientProvider>
  );
};

export default App;
