import { useState } from 'react';
import { Box, Button, IconButton, Stack, Tooltip, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import HelpOutlineIcon from '@mui/icons-material/HelpOutlineOutlined';
import RefreshIcon from '@mui/icons-material/Refresh';
import PauseIcon from '@mui/icons-material/Pause';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { useDispatchStore } from '../store/useDispatchStore';
import { useTeamRoutes } from '../hooks/useTeamRoutes';
import { useInterval } from '../hooks/useInterval';
import { RouteMap } from '../components/route/RouteMap';
import { LiveTeamCard } from '../components/route/LiveTeamCard';
import { durationLabel } from '../utils/time';
import type { DispatchTeam } from '../types/dispatch';

const NO_TEAMS: DispatchTeam[] = [];
const AUTO_REFRESH_MS = 30_000;

export function ConfirmedRoutePage() {
  const navigate = useNavigate();
  const liveTeams = useDispatchStore((s) => s.liveTeams);
  const confirmedSummary = useDispatchStore((s) => s.confirmedSummary);
  const lastUpdatedAt = useDispatchStore((s) => s.lastUpdatedAt);
  const advanceLiveProgress = useDispatchStore((s) => s.advanceLiveProgress);
  const { routesByTeamId, isLoading: isLoadingRoutes, failedTeamIds } = useTeamRoutes(
    liveTeams ?? NO_TEAMS,
    Boolean(liveTeams),
  );

  const allDone = Boolean(liveTeams && liveTeams.every((team) => team.stops.every((stop) => stop.status === 'completed')));
  const [autoRefresh, setAutoRefresh] = useState(true);
  useInterval(advanceLiveProgress, autoRefresh && !allDone ? AUTO_REFRESH_MS : null);

  if (!liveTeams || !confirmedSummary) {
    return (
      <Stack spacing={2} sx={{ flex: 1, alignItems: 'center', justifyContent: 'center', px: 4 }}>
        <Typography color="text.secondary" align="center" sx={{ mb: 2 }}>
          아직 확정된 경로가 없습니다.
          <br />
          경로 배치를 먼저 진행해주세요.
        </Typography>
        <Button variant="contained" onClick={() => navigate('/dispatch')}>
          경로 배치로 이동
        </Button>
      </Stack>
    );
  }

  return (
    <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
      <Stack
        direction="row"
        sx={{ alignItems: 'flex-start', justifyContent: 'space-between', px: 3, pt: 3, pb: 2 }}
      >
        <Box>
          <Stack direction="row" spacing={0.5} sx={{ alignItems: 'center' }}>
            <Typography variant="h5" sx={{ fontWeight: 700 }}>
              확정 경로 + 실시간 현황
            </Typography>
            <Tooltip title="모바일 앱에서 방역관이 처리를 완료하면 실시간으로 반영됩니다.">
              <IconButton size="small">
                <HelpOutlineIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Stack>
          <Typography variant="body2" color="text.secondary">
            {`선택 농장 ${confirmedSummary.selectedFarmCount}곳  |  가용 팀 ${confirmedSummary.teamCount}팀  |  총 예상 소요시간 ${durationLabel(confirmedSummary.totalDurationMinutes)}`}
          </Typography>
        </Box>
        <Stack direction="row" spacing={1} sx={{ alignItems: 'center', flexShrink: 0 }}>
          <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: allDone ? 'text.disabled' : 'success.main' }} />
          <Typography variant="caption" color="text.secondary">
            {`마지막 업데이트: ${lastUpdatedAt ?? '-'}`}
          </Typography>
          <Button
            size="small"
            variant="outlined"
            startIcon={autoRefresh && !allDone ? <PauseIcon fontSize="small" /> : <PlayArrowIcon fontSize="small" />}
            onClick={() => setAutoRefresh((v) => !v)}
            disabled={allDone}
            sx={{ ml: 1 }}
          >
            {autoRefresh && !allDone ? '자동갱신 중' : allDone ? '완료' : '자동갱신 시작'}
          </Button>
        </Stack>
      </Stack>

      <Box sx={{ flex: 1, display: 'flex', minHeight: 0, px: 3, pb: 2, gap: 2 }}>
        <Box sx={{ flex: 1, position: 'relative', minWidth: 0, borderRadius: 1.5, overflow: 'hidden' }}>
          <RouteMap
            teams={liveTeams}
            routesByTeamId={routesByTeamId}
            isLoadingRoutes={isLoadingRoutes}
            failedTeamIds={failedTeamIds}
          />
        </Box>
        <Box sx={{ width: 320, flexShrink: 0, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
          <Stack
            direction="row"
            sx={{ alignItems: 'center', justifyContent: 'space-between', mb: 1.5 }}
          >
            <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
              <Typography sx={{ fontWeight: 700 }}>실시간 현황 (모바일 연동)</Typography>
              <Box
                sx={{
                  px: 0.75,
                  py: 0.1,
                  borderRadius: 1,
                  bgcolor: 'success.light',
                  color: 'success.dark',
                  fontSize: 11,
                  fontWeight: 700,
                }}
              >
                LIVE
              </Box>
            </Stack>
            <Button size="small" startIcon={<RefreshIcon fontSize="small" />} onClick={advanceLiveProgress}>
              새로고침
            </Button>
          </Stack>
          <Box sx={{ flex: 1, overflowY: 'auto' }}>
            {liveTeams.map((team) => (
              <LiveTeamCard key={team.id} team={team} routeInfo={routesByTeamId[team.id]} />
            ))}
          </Box>
        </Box>
      </Box>
    </Box>
  );
}
