import { Box, Paper, Stack, Typography } from '@mui/material';
import type { DispatchTeam } from '../../types/dispatch';
import { durationLabel } from '../../utils/time';

interface TeamSummaryCardProps {
  team: DispatchTeam;
}

export function TeamSummaryCard({ team }: TeamSummaryCardProps) {
  return (
    <Paper variant="outlined" sx={{ borderRadius: 1.5, mb: 2, overflow: 'hidden' }}>
      <Stack
        direction="row"
        sx={{
          alignItems: 'center',
          justifyContent: 'space-between',
          px: 2,
          py: 1.5,
          borderBottom: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
          <Box sx={{ width: 10, height: 10, borderRadius: '50%', bgcolor: team.color }} />
          <Typography sx={{ fontWeight: 700 }}>{team.label}</Typography>
        </Stack>
        <Typography variant="body2" color="text.secondary">{`${team.stops.length}곳 방문`}</Typography>
      </Stack>

      <Box sx={{ px: 2, py: 0.5 }}>
        {team.stops.map((stop) => (
          <Stack
            key={stop.farm.id}
            direction="row"
            sx={{ alignItems: 'center', justifyContent: 'space-between', py: 0.85 }}
          >
            <Stack direction="row" spacing={1.25} sx={{ alignItems: 'center' }}>
              <Box
                sx={{
                  width: 20,
                  height: 20,
                  flexShrink: 0,
                  borderRadius: '50%',
                  bgcolor: team.color,
                  color: '#fff',
                  fontSize: 11,
                  fontWeight: 700,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                {stop.order}
              </Box>
              <Typography variant="body2">{stop.farm.name}</Typography>
            </Stack>
            <Typography variant="body2" color="text.secondary">
              {`${stop.farm.estimatedDurationMinutes}분`}
            </Typography>
          </Stack>
        ))}
      </Box>

      <Stack
        direction="row"
        sx={{
          alignItems: 'center',
          justifyContent: 'space-between',
          px: 2,
          py: 1.25,
          borderTop: '1px solid',
          borderColor: 'divider',
          bgcolor: 'grey.50',
        }}
      >
        <Typography variant="body2" color="text.secondary">
          팀 총 예상 소요시간
        </Typography>
        <Typography variant="body2" sx={{ fontWeight: 700 }}>
          {durationLabel(team.totalDurationMinutes)}
        </Typography>
      </Stack>
    </Paper>
  );
}
