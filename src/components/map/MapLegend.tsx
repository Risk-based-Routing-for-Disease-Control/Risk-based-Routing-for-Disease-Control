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
        <Stack direction="row" spacing={1} sx={{ alignItems: 'center', mt: 0.5, pt: 0.5, borderTop: '1px solid', borderColor: 'divider' }}>
          <Box
            component="svg"
            xmlns="http://www.w3.org/2000/svg"
            width={10}
            height={10}
            viewBox="0 0 24 24"
            sx={{ flexShrink: 0 }}
          >
            <rect x="2" y="2" width="20" height="20" rx="4" fill="#1565C0" stroke="#ffffff" strokeWidth="2" />
            <path d="M12 7v10M7 12h10" stroke="#ffffff" strokeWidth="2.2" strokeLinecap="round" />
          </Box>
          <Typography variant="body2">방역시설</Typography>
        </Stack>
      </Stack>
    </Paper>
  );
}
