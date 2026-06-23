import { Box } from '@mui/material';
import { NaverMap } from '../components/map/NaverMap';
import { FarmDetailPanel } from '../components/detail/FarmDetailPanel';

export function MapPage() {
  return (
    <Box sx={{ flex: 1, display: 'flex', minHeight: 0 }}>
      <Box sx={{ flex: 1, position: 'relative', minWidth: 0 }}>
        <NaverMap />
      </Box>
      <FarmDetailPanel />
    </Box>
  );
}
