import { Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { NaverMap } from '../components/map/NaverMap';
import { FarmDetailOverlay } from '../components/detail/FarmDetailOverlay';
import { DispatchSettingsView } from '../components/dispatch/DispatchSettingsView';

export function MapPage() {
  const navigate = useNavigate();

  return (
    <Box sx={{ flex: 1, display: 'flex', minHeight: 0, bgcolor: 'background.default' }}>
      <Box sx={{ flex: 1, position: 'relative', minWidth: 0, m: 2, mr: 1, borderRadius: 1.5, overflow: 'hidden' }}>
        <NaverMap />
        <FarmDetailOverlay />
      </Box>
      <Box
        sx={{
          width: 460,
          flexShrink: 0,
          display: 'flex',
          minHeight: 0,
          m: 2,
          ml: 1,
          border: '1px solid',
          borderColor: 'divider',
          borderRadius: 1.5,
          bgcolor: 'background.paper',
          overflow: 'hidden',
        }}
      >
        <DispatchSettingsView variant="panel" onDispatchComplete={() => navigate('/dispatch')} />
      </Box>
    </Box>
  );
}
