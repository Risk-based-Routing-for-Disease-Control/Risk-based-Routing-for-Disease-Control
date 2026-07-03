import { Button, Stack, Typography } from '@mui/material';
import { useEmergencyModeStore } from '../../store/useEmergencyModeStore';

export function EmergencyModeBanner() {
  const isActive = useEmergencyModeStore((s) => s.isActive);
  const label = useEmergencyModeStore((s) => s.label);
  const exit = useEmergencyModeStore((s) => s.exit);

  if (!isActive) return null;

  return (
    <Stack
      direction="row"
      sx={{
        alignItems: 'center',
        justifyContent: 'center',
        gap: 2,
        bgcolor: 'error.main',
        color: '#fff',
        px: 2,
        py: 1,
      }}
    >
      <Typography sx={{ fontWeight: 800 }}>{`🚨 비상 대응 모드 활성 — ${label ?? ''}`}</Typography>
      <Button size="small" variant="outlined" onClick={() => exit()} sx={{ color: '#fff', borderColor: '#fff' }}>
        종료
      </Button>
    </Stack>
  );
}
