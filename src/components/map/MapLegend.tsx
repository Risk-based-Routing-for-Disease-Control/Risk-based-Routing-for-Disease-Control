import { Box, Paper, Stack, Typography } from '@mui/material';
import { RISK_LEVELS } from '../../constants/risk';

export function MapLegend() {
  return (
    <Paper
      elevation={2}
      sx={{
        position: 'absolute',
        bottom: 16,
        right: 16,
        px: 1.5,
        py: 1.25,
        borderRadius: 1.5,
        minWidth: 120,
      }}
    >
      <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>
        위험도 범례
      </Typography>
      <Stack spacing={0.75}>
        {RISK_LEVELS.map((level) => (
          <Stack key={level.value} direction="row" spacing={1} sx={{ alignItems: 'center' }}>
            <Box sx={{ width: 10, height: 10, borderRadius: '50%', bgcolor: level.color }} />
            <Typography variant="body2">{level.label}</Typography>
          </Stack>
        ))}
      </Stack>
    </Paper>
  );
}
