import { Box, Paper, Stack, Typography } from '@mui/material';
import type { DispatchTeam } from '../../types/dispatch';

interface RouteLegendProps {
  teams: DispatchTeam[];
}

export function RouteLegend({ teams }: RouteLegendProps) {
  const visibleTeams = teams.filter((team) => team.stops.length > 0);
  if (visibleTeams.length === 0) return null;

  return (
    <Paper
      elevation={2}
      sx={{ position: 'absolute', bottom: 16, right: 16, px: 1.5, py: 1.25, borderRadius: 1.5, minWidth: 140 }}
    >
      <Stack spacing={0.75}>
        {visibleTeams.map((team) => {
          const completedCount = team.stops.filter((stop) => stop.status === 'completed').length;
          const cancelledCount = team.stops.filter((stop) => stop.status === 'cancelled').length;
          const hasProgress = completedCount > 0 || cancelledCount > 0;
          return (
            <Stack key={team.id} direction="row" spacing={1} sx={{ alignItems: 'center' }}>
              <Box sx={{ width: 18, height: 3, borderRadius: 1, bgcolor: team.color }} />
              <Typography variant="body2">
                {hasProgress
                  ? `${team.label} (${completedCount}/${team.stops.length}완료${cancelledCount ? ` · 취소 ${cancelledCount}` : ''})`
                  : `${team.label} (${team.stops.length}곳)`}
              </Typography>
            </Stack>
          );
        })}
      </Stack>
    </Paper>
  );
}
