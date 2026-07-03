import { Box } from '@mui/material';
import { Outlet } from 'react-router-dom';
import { AppHeader } from './AppHeader';
import { AppSidebar } from './AppSidebar';
import { DataSourceBanner } from './DataSourceBanner';
import { EmergencyModeBanner } from './EmergencyModeBanner';

export function AppLayout() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <AppHeader />
      <EmergencyModeBanner />
      <DataSourceBanner />
      <Box sx={{ display: 'flex', flex: 1, minHeight: 0 }}>
        <AppSidebar />
        <Box sx={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column' }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
}
