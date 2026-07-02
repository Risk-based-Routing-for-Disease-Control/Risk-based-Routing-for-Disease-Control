import { useState } from 'react';
import {
  Box,
  Button,
  Collapse,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Stack,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutlineOutlined';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import type { MultiStopRouteResult } from '../../api/directions';
import type { DispatchStop, DispatchTeam } from '../../types/dispatch';
import { formatDistance, formatDurationFromMs } from '../../utils/routeMetrics';
import { formatTimestampLabel } from '../../utils/time';
import { useDispatchStore } from '../../store/useDispatchStore';

interface LiveTeamCardProps {
  team: DispatchTeam;
  routeInfo?: MultiStopRouteResult;
}

export function LiveTeamCard({ team, routeInfo }: LiveTeamCardProps) {
  const [expanded, setExpanded] = useState(true);
  const completeStop = useDispatchStore((s) => s.completeStop);
  const cancelStop = useDispatchStore((s) => s.cancelStop);
  const [completeTarget, setCompleteTarget] = useState<DispatchStop | null>(null);
  const [cancelTarget, setCancelTarget] = useState<DispatchStop | null>(null);
  const [durationValue, setDurationValue] = useState('');
  const completedCount = team.stops.filter((stop) => stop.status === 'completed').length;
  const cancelledCount = team.stops.filter((stop) => stop.status === 'cancelled').length;

  const openComplete = (stop: DispatchStop) => {
    setDurationValue(String(stop.farm.estimatedDurationMinutes));
    setCompleteTarget(stop);
  };

  const closeComplete = () => {
    setCompleteTarget(null);
    setDurationValue('');
  };

  const submitComplete = () => {
    const minutes = Number(durationValue);
    if (!completeTarget || !Number.isInteger(minutes) || minutes < 1 || minutes > 600) return;
    void completeStop(team.id, completeTarget.farm.id, minutes);
    closeComplete();
  };

  const submitCancel = () => {
    if (!cancelTarget) return;
    void cancelStop(team.id, cancelTarget.farm.id);
    setCancelTarget(null);
  };

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
            const leg = routeInfo?.legs[index];
            return (
              <Box key={stop.farm.id}>
                <Stack
                  direction="row"
                  spacing={1}
                  sx={{
                    alignItems: 'center',
                    py: 0.6,
                    color: isCompleted ? 'success.main' : 'text.disabled',
                  }}
                >
                  <Tooltip title={isCompleted ? '완료 취소' : '완료 처리'}>
                    <IconButton
                      size="small"
                      color={isCompleted ? 'success' : 'default'}
                      aria-label={isCompleted ? '완료 취소' : '완료 처리'}
                      onClick={() => (isCompleted ? setCancelTarget(stop) : openComplete(stop))}
                    >
                      {isCompleted ? <CheckCircleIcon fontSize="small" /> : <CheckCircleOutlineIcon fontSize="small" />}
                    </IconButton>
                  </Tooltip>
                  <Typography
                    variant="body2"
                    sx={{ flex: 1, color: isCompleted ? 'text.primary' : 'text.secondary' }}
                  >
                    {stop.farm.name}
                  </Typography>
                  {isCompleted && (
                    <Typography variant="caption" color="text.secondary">
                      {`${formatTimestampLabel(stop.completedAt)} (${stop.actualDurationMinutes ?? stop.farm.estimatedDurationMinutes}분)`}
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

      <Dialog open={Boolean(completeTarget)} onClose={closeComplete} fullWidth maxWidth="xs">
        <DialogTitle sx={{ fontWeight: 800 }}>완료 처리</DialogTitle>
        <DialogContent>
          <Typography sx={{ mb: 2 }}>{`${completeTarget?.farm.name ?? ''} 방문을 완료 처리하시겠습니까?`}</Typography>
          <TextField
            label="실제 소요시간 (분)"
            type="number"
            fullWidth
            value={durationValue}
            onChange={(e) => setDurationValue(e.target.value)}
            slotProps={{ htmlInput: { min: 1, max: 600 } }}
            autoFocus
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={closeComplete}>취소</Button>
          <Button variant="contained" color="success" onClick={submitComplete}>
            확인
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={Boolean(cancelTarget)} onClose={() => setCancelTarget(null)} fullWidth maxWidth="xs">
        <DialogTitle sx={{ fontWeight: 800 }}>완료 취소</DialogTitle>
        <DialogContent>
          <Typography>{`${cancelTarget?.farm.name ?? ''} 완료 처리를 취소하시겠습니까?`}</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCancelTarget(null)}>아니요</Button>
          <Button variant="contained" color="error" onClick={submitCancel}>
            예
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
