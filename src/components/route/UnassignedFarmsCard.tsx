import { Paper, Stack, Typography } from '@mui/material';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import type { Farm } from '../../types/farm';

interface UnassignedFarmsCardProps {
  farms: Farm[];
  selectedFarmCount: number;
}

export function UnassignedFarmsCard({ farms, selectedFarmCount }: UnassignedFarmsCardProps) {
  if (farms.length === 0) return null;
  const percent = selectedFarmCount === 0 ? 0 : Math.round((farms.length / selectedFarmCount) * 100);

  return (
    <Paper variant="outlined" sx={{ borderColor: '#FFE0A3', bgcolor: '#FFF8E6', borderRadius: 1.5, p: 2 }}>
      <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
        <WarningAmberIcon fontSize="small" sx={{ color: '#B26A00' }} />
        <Typography sx={{ fontWeight: 700, color: '#8A5800' }}>{`미처리 농장 ${farms.length}곳`}</Typography>
      </Stack>
      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
        전체 선택 농장 대비
      </Typography>
      <Typography variant="body2" sx={{ fontWeight: 600 }}>
        {`${selectedFarmCount}곳 중 ${farms.length}곳 / ${percent}%`}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
        {farms.map((farm) => farm.name).join(', ')}
      </Typography>
    </Paper>
  );
}
