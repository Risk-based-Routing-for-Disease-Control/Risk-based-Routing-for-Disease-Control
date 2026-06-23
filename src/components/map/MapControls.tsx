import { Divider, IconButton, Paper, Stack } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import MyLocationIcon from '@mui/icons-material/MyLocation';

interface MapControlsProps {
  onZoomIn: () => void;
  onZoomOut: () => void;
  onLocate: () => void;
}

export function MapControls({ onZoomIn, onZoomOut, onLocate }: MapControlsProps) {
  return (
    <Stack spacing={1} sx={{ position: 'absolute', top: 16, left: 16, zIndex: 10 }}>
      <Paper elevation={2} sx={{ borderRadius: 1.5, overflow: 'hidden' }}>
        <IconButton
          size="small"
          onClick={onZoomIn}
          aria-label="확대"
          sx={{ borderRadius: 0, display: 'flex', width: 36, height: 36 }}
        >
          <AddIcon fontSize="small" />
        </IconButton>
        <Divider />
        <IconButton
          size="small"
          onClick={onZoomOut}
          aria-label="축소"
          sx={{ borderRadius: 0, display: 'flex', width: 36, height: 36 }}
        >
          <RemoveIcon fontSize="small" />
        </IconButton>
      </Paper>
      <Paper elevation={2} sx={{ borderRadius: 1.5 }}>
        <IconButton size="small" onClick={onLocate} aria-label="현재 위치" sx={{ width: 36, height: 36 }}>
          <MyLocationIcon fontSize="small" />
        </IconButton>
      </Paper>
    </Stack>
  );
}
