import { useState } from 'react';
import { Box, Collapse, IconButton, Stack, Typography } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import type { MultiStopRouteResult } from '../../api/directions';
import type { DispatchTeam } from '../../types/dispatch';
import { formatDistance, formatDurationFromMs } from '../../utils/routeMetrics';

interface LiveTeamCardProps {
  team: DispatchTeam;
  routeInfo?: MultiStopRouteResult;
}

export function LiveTeamCard({ team, routeInfo }: LiveTeamCardProps) {
  const [expanded, setExpanded] = useState(true);
  const completedCount = team.stops.filter((stop) => stop.status === 'completed').length;
  const cancelledCount = team.stops.filter((stop) => stop.status === 'cancelled').length;

  return (
    <Box sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 1.5, mb: 2, overflow: 'hidden' }}>
      <Box onClick={() => setExpanded((value) => !value)} sx={{ px: 2, py: 1.5, cursor: 'pointer' }}>
        <Stack direction="row" sx={{ alignItems: 'center', justifyContent: 'space-between' }}>
          <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
            <Box sx={{ width: 10, height: 10, borderRadius: '50%', bgcolor: team.color }} />
            <Typography sx={{ fontWeight: 700 }}>{team.label}</Typography>
          </Stack>
          <Stack direction="row" spacing={0.5} sx={{ alignItems: 'center' }}>
            <Typography variant="body2" color="text.secondary">{`${completedCount}완료 · ${cancelledCount}취소`}</Typography>
            <IconButton
              size="small"
              sx={{ transform: expanded ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }}
            >
              <ExpandMoreIcon fontSize="small" />
            </IconButton>
          </Stack>
        </Stack>
        {routeInfo && (
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
            {`실제 이동: ${formatDistance(routeInfo.totalDistance)} · ${formatDurationFromMs(routeInfo.totalDuration)}`}
          </Typography>
        )}
      </Box>
      <Collapse in={expanded}>
        <Box sx={{ px: 2, pb: 1.5 }}>
          {team.stops.map((stop, index) => {
            const isCompleted = stop.status === 'completed';
            const isCancelled = stop.status === 'cancelled';
            const leg = routeInfo?.legs[index];
            return (
              <Box key={stop.farm.id}>
                <Stack
                  direction="row"
                  spacing={1}
                  sx={{
                    alignItems: 'center',
                    py: 0.6,
                    color: isCompleted ? 'text.disabled' : isCancelled ? 'error.main' : 'primary.main',
                  }}
                >
                  {isCompleted ? (
                    <CheckCircleIcon fontSize="small" />
                  ) : isCancelled ? (
                    <CancelIcon fontSize="small" />
                  ) : (
                    <ArrowForwardIcon fontSize="small" />
                  )}
                  <Typography
                    variant="body2"
                    sx={{ flex: 1, color: isCompleted ? 'text.disabled' : isCancelled ? 'error.main' : 'text.primary' }}
                  >
                    {stop.farm.name}
                  </Typography>
                  {isCompleted && (
                    <Typography variant="caption" color="text.secondary">
                      {`${stop.completedAt} (${stop.actualDurationMinutes ?? stop.farm.estimatedDurationMinutes}분)`}
                    </Typography>
                  )}
                  {isCancelled && (
                    <Typography variant="caption" color="error.main">
                      취소됨
                    </Typography>
                  )}
                </Stack>
                {leg && (
                  <Stack direction="row" spacing={0.5} sx={{ alignItems: 'center', pl: 3.5, color: 'text.disabled' }}>
                    <ArrowDownwardIcon sx={{ fontSize: 14 }} />
                    <Typography variant="caption">
                      {`이동 ${formatDurationFromMs(leg.duration)} · ${formatDistance(leg.distance)}`}
                    </Typography>
                  </Stack>
                )}
              </Box>
            );
          })}
        </Box>
      </Collapse>
    </Box>
  );
}
