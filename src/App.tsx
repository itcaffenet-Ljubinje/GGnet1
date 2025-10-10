import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from '@/components/Layout';
import Login from '@/components/Login';
import Dashboard from '@/pages/Dashboard';
import Computers from '@/pages/Computers';
import Sessions from '@/pages/Sessions';
import BootImages from '@/pages/BootImages';
import Games from '@/pages/Games';
import Network from '@/pages/Network';
import Settings from '@/pages/Settings';
import { ggRockAPI } from '@/services/ggrock-api';

// Create a query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5000,
    },
  },
});

// Protected Route component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = ggRockAPI.isAuthenticated();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

// Public Route component (redirects to dashboard if already authenticated)
function PublicRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = ggRockAPI.isAuthenticated();
  
  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route
            path="/login"
            element={
              <PublicRoute>
                <Login />
              </PublicRoute>
            }
          />

          {/* Protected routes */}
          <Route
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route path="/" element={<Dashboard />} />
            <Route path="/computers" element={<Computers />} />
            <Route path="/sessions" element={<Sessions />} />
            <Route path="/boot-images" element={<BootImages />} />
            <Route path="/games" element={<Games />} />
            <Route path="/network" element={<Network />} />
            <Route path="/settings" element={<Settings />} />
          </Route>

          {/* Catch all - redirect to dashboard */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;

