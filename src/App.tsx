import { useEffect } from 'react';
import { CssBaseline, ThemeProvider } from '@mui/material';
import { Navigate, Outlet, Route, BrowserRouter, Routes } from 'react-router-dom';
import { theme } from './theme/theme';
import { AppLayout } from './components/layout/AppLayout';
import { MapPage } from './pages/MapPage';
import { DispatchPage } from './pages/DispatchPage';
import { ConfirmedRoutePage } from './pages/ConfirmedRoutePage';
import { MobileFieldPage } from './pages/MobileFieldPage';
import { LoginPage } from './pages/LoginPage';
import { useDispatchStore } from './store/useDispatchStore';
import { useFarmStore } from './store/useFarmStore';
import { useFacilitiesStore } from './store/useFacilitiesStore';
import { useAuthStore } from './store/useAuthStore';

function RequireAuth() {
  const isLoggedIn = useAuthStore((s) => s.isLoggedIn);
  return isLoggedIn ? <Outlet /> : <Navigate to="/login" replace />;
}

function App() {
  const loadFarms = useFarmStore((s) => s.loadFarms);
  const loadFacilities = useFacilitiesStore((s) => s.loadFacilities);

  useEffect(() => {
    void loadFarms();
  }, [loadFarms]);

  useEffect(() => {
    void loadFacilities();
  }, [loadFacilities]);

  useEffect(() => {
    const handleStorage = (event: StorageEvent) => {
      if (event.key === 'livestock-dispatch') {
        void useDispatchStore.persist.rehydrate();
      }
    };
    window.addEventListener('storage', handleStorage);
    return () => window.removeEventListener('storage', handleStorage);
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/mobile" element={<MobileFieldPage />} />
          <Route path="/mobile/:dispatchRunId" element={<MobileFieldPage />} />
          <Route element={<RequireAuth />}>
            <Route element={<AppLayout />}>
              <Route index element={<Navigate to="/map" replace />} />
              <Route path="/map" element={<MapPage />} />
              <Route path="/dispatch" element={<DispatchPage />} />
              <Route path="/confirmed" element={<ConfirmedRoutePage />} />
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
