import { CssBaseline, ThemeProvider } from '@mui/material';
import { Navigate, Route, BrowserRouter, Routes } from 'react-router-dom';
import { theme } from './theme/theme';
import { AppLayout } from './components/layout/AppLayout';
import { MapPage } from './pages/MapPage';
import { DispatchPage } from './pages/DispatchPage';
import { ConfirmedRoutePage } from './pages/ConfirmedRoutePage';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route element={<AppLayout />}>
            <Route index element={<Navigate to="/map" replace />} />
            <Route path="/map" element={<MapPage />} />
            <Route path="/dispatch" element={<DispatchPage />} />
            <Route path="/confirmed" element={<ConfirmedRoutePage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
