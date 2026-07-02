import { useEffect, useMemo, useState } from 'react';
import {
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Stack,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
} from '@mui/material';
import BackspaceOutlinedIcon from '@mui/icons-material/BackspaceOutlined';
import MenuIcon from '@mui/icons-material/Menu';
import RefreshIcon from '@mui/icons-material/Refresh';
import { useNavigate, useParams } from 'react-router-dom';
import { FarmVisitCard } from '../components/mobile/FarmVisitCard';
import { RISK_LEVEL_COLOR, RISK_LEVEL_LABEL } from '../constants/risk';
import { useDispatchStore } from '../store/useDispatchStore';
import { useFarmStore } from '../store/useFarmStore';
import { useFacilitiesStore } from '../store/useFacilitiesStore';
import { useInterval } from '../hooks/useInterval';
import type { DispatchStop, DispatchTeam } from '../types/dispatch';

const keypad = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'];
const POLL_INTERVAL_MS = 8000;

function fallbackPhone(order: number) {
  return `010-${String(1234 + order * 1111).slice(0, 4)}-${String(5678 + order * 1111).slice(0, 4)}`;
}

function stopCounts(team?: DispatchTeam) {
  const total = team?.stops.length ?? 0;
  const completed = team?.stops.filter((stop) => stop.status === 'completed').length ?? 0;
  return { total, completed, remaining: total - completed };
}

export function MobileFieldPage() {
  const navigate = useNavigate();
  const { dispatchRunId: routeDispatchRunId } = useParams<{ dispatchRunId: string }>();
  const liveTeams = useDispatchStore((state) => state.liveTeams);
  const lastUpdatedAt = useDispatchStore((state) => state.lastUpdatedAt);
  const dispatchRunId = useDispatchStore((state) => state.dispatchRunId);
  const syncError = useDispatchStore((state) => state.syncError);
  const isLoadingRun = useDispatchStore((state) => state.isLoadingRun);
  const loadRunError = useDispatchStore((state) => state.loadRunError);
  const completeStop = useDispatchStore((state) => state.completeStop);
  const cancelStop = useDispatchStore((state) => state.cancelStop);
  const syncLiveTeams = useDispatchStore((state) => state.syncLiveTeams);
  const loadDispatchRun = useDispatchStore((state) => state.loadDispatchRun);
  const loadFarms = useFarmStore((state) => state.loadFarms);
  const loadFacilities = useFacilitiesStore((state) => state.loadFacilities);
  const [selectedTeamId, setSelectedTeamId] = useState<string | null>(liveTeams?.[0]?.id ?? null);

  useEffect(() => {
    if (!routeDispatchRunId) return; // 파라미터 없는 /mobile: 기존 로컬 상태 그대로 사용
    if (dispatchRunId === routeDispatchRunId && liveTeams) return; // 이미 로드됨(같은 기기 등)
    void (async () => {
      await Promise.all([loadFarms(), loadFacilities()]);
      await loadDispatchRun(routeDispatchRunId);
    })();
  }, [routeDispatchRunId, dispatchRunId, liveTeams, loadFarms, loadFacilities, loadDispatchRun]);

  useInterval(() => void syncLiveTeams(), liveTeams && dispatchRunId ? POLL_INTERVAL_MS : null);
  const [completeTarget, setCompleteTarget] = useState<DispatchStop | null>(null);
  const [cancelTarget, setCancelTarget] = useState<DispatchStop | null>(null);
  const [durationValue, setDurationValue] = useState('');

  const selectedTeam = useMemo(() => {
    if (!liveTeams?.length) return undefined;
    return liveTeams.find((team) => team.id === selectedTeamId) ?? liveTeams[0];
  }, [liveTeams, selectedTeamId]);
  const counts = stopCounts(selectedTeam);

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
    if (!selectedTeam || !completeTarget || !Number.isInteger(minutes) || minutes < 1 || minutes > 600) return;
    completeStop(selectedTeam.id, completeTarget.farm.id, minutes);
    closeComplete();
  };

  const submitCancel = () => {
    if (!selectedTeam || !cancelTarget) return;
    cancelStop(selectedTeam.id, cancelTarget.farm.id);
    setCancelTarget(null);
  };

  const appendDigit = (digit: string) => {
    setDurationValue((value) => {
      const next = `${value}${digit}`.replace(/^0+(?=\d)/, '');
      return next.length > 3 ? value : next;
    });
  };

  if (routeDispatchRunId && isLoadingRun) {
    return (
      <Box sx={{ minHeight: '100dvh', bgcolor: '#F6F7F9', px: 2.5, py: 3 }}>
        <Stack spacing={2} sx={{ minHeight: 'calc(100dvh - 48px)', alignItems: 'center', justifyContent: 'center' }}>
          <CircularProgress size={28} />
          <Typography color="text.secondary" align="center">
            배차 정보를 불러오는 중입니다...
          </Typography>
        </Stack>
      </Box>
    );
  }

  if (routeDispatchRunId && loadRunError) {
    return (
      <Box sx={{ minHeight: '100dvh', bgcolor: '#F6F7F9', px: 2.5, py: 3 }}>
        <Stack spacing={2} sx={{ minHeight: 'calc(100dvh - 48px)', alignItems: 'center', justifyContent: 'center' }}>
          <Typography sx={{ fontWeight: 800, fontSize: 20 }}>배차 결과를 불러오지 못했습니다</Typography>
          <Typography color="text.secondary" align="center">
            {loadRunError}
          </Typography>
          <Button variant="contained" onClick={() => navigate('/dispatch')}>
            배치 화면으로 이동
          </Button>
        </Stack>
      </Box>
    );
  }

  if (!liveTeams?.length) {
    return (
      <Box sx={{ minHeight: '100dvh', bgcolor: '#F6F7F9', px: 2.5, py: 3 }}>
        <Stack spacing={2} sx={{ minHeight: 'calc(100dvh - 48px)', alignItems: 'center', justifyContent: 'center' }}>
          <Typography sx={{ fontWeight: 800, fontSize: 20 }}>확정된 경로가 없습니다</Typography>
          <Typography color="text.secondary" align="center">
            웹 화면에서 경로 배치를 확정한 뒤 다시 열어주세요.
          </Typography>
          <Button variant="contained" onClick={() => navigate('/dispatch')}>
            배치 화면으로 이동
          </Button>
        </Stack>
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: '100dvh', bgcolor: '#F6F7F9', color: '#111827' }}>
      <Box sx={{ maxWidth: 430, mx: 'auto', minHeight: '100dvh', bgcolor: '#FAFAFB', px: 2, py: 1.5 }}>
        <Stack direction="row" sx={{ alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <IconButton size="small" aria-label="menu">
            <MenuIcon />
          </IconButton>
          <Typography sx={{ fontWeight: 800 }}>농장 리스트</Typography>
          <IconButton size="small" aria-label="refresh" onClick={() => void syncLiveTeams()}>
            <RefreshIcon />
          </IconButton>
        </Stack>
        {syncError && (
          <Typography variant="caption" color="error" sx={{ display: 'block', mb: 1 }}>
            {`동기화 실패: ${syncError}`}
          </Typography>
        )}

        <ToggleButtonGroup
          exclusive
          fullWidth
          value={selectedTeam?.id ?? ''}
          onChange={(_, value: string | null) => value && setSelectedTeamId(value)}
          sx={{
            mb: 1.75,
            bgcolor: '#fff',
            borderRadius: 999,
            '& .MuiToggleButton-root': {
              borderColor: '#E2E5EA',
              py: 1,
              fontWeight: 800,
              color: '#1F2937',
              '&.Mui-selected': {
                bgcolor: 'primary.main',
                color: '#fff',
                '&:hover': { bgcolor: 'primary.dark' },
              },
            },
          }}
        >
          {liveTeams.map((team) => (
            <ToggleButton key={team.id} value={team.id}>
              {team.label}
            </ToggleButton>
          ))}
        </ToggleButtonGroup>

        <Stack direction="row" spacing={1.25} sx={{ alignItems: 'center', mb: 1.5 }}>
          <Typography variant="body2">{`전체 ${counts.total}곳`}</Typography>
          <Typography variant="body2" color="text.secondary">
            |
          </Typography>
          <Typography variant="body2">{`완료 ${counts.completed}곳`}</Typography>
          <Typography variant="body2" color="text.secondary">
            |
          </Typography>
          <Typography variant="body2">{`남은 ${counts.remaining}곳`}</Typography>
        </Stack>

        <Stack spacing={1.1}>
          {selectedTeam?.stops.map((stop) => (
            <FarmVisitCard
              key={stop.farm.id}
              stop={stop}
              phone={fallbackPhone(stop.order)}
              riskLabel={RISK_LEVEL_LABEL[stop.farm.riskLevel]}
              riskColor={RISK_LEVEL_COLOR[stop.farm.riskLevel]}
              onComplete={() => openComplete(stop)}
              onCancel={() => setCancelTarget(stop)}
            />
          ))}
        </Stack>

        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', textAlign: 'center', py: 2 }}>
          {`→ 완료 · 완료 항목은 ← 취소 · ${lastUpdatedAt ?? '동기화 전'}`}
        </Typography>
      </Box>

      <Dialog
        open={Boolean(completeTarget)}
        onClose={closeComplete}
        fullWidth
        maxWidth="xs"
        slotProps={{ paper: { sx: { borderRadius: 2 } } }}
      >
        <DialogTitle sx={{ textAlign: 'center', fontWeight: 800, pb: 0 }}>완료 처리</DialogTitle>
        <DialogContent>
          <Typography align="center" sx={{ mt: 1, mb: 3 }}>
            정말 완료하시겠습니까?
          </Typography>
          <Typography align="center" variant="body2" sx={{ mb: 1.25 }}>
            실제 소요시간 입력 (분)
          </Typography>
          <Stack direction="row" sx={{ alignItems: 'center', mb: 1 }}>
            <Box
              sx={{
                flex: 1,
                height: 52,
                border: '1px solid #D7DBE2',
                borderRadius: 1,
                display: 'grid',
                placeItems: 'center',
                fontSize: 24,
                fontWeight: 900,
                bgcolor: '#fff',
              }}
            >
              {durationValue || '0'}
            </Box>
            <Typography sx={{ ml: 1.25, fontWeight: 700 }}>분</Typography>
          </Stack>
          <Typography align="center" variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>
            숫자만 입력해주세요.
          </Typography>
          <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 0.75 }}>
            {keypad.slice(0, 9).map((digit) => (
              <Button key={digit} variant="outlined" sx={{ height: 48, fontSize: 20, fontWeight: 800 }} onClick={() => appendDigit(digit)}>
                {digit}
              </Button>
            ))}
            <Box />
            <Button variant="outlined" sx={{ height: 48, fontSize: 20, fontWeight: 800 }} onClick={() => appendDigit('0')}>
              0
            </Button>
            <Button variant="outlined" sx={{ height: 48 }} onClick={() => setDurationValue((value) => value.slice(0, -1))}>
              <BackspaceOutlinedIcon />
            </Button>
          </Box>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3, gap: 1 }}>
          <Button fullWidth variant="contained" color="inherit" onClick={closeComplete}>
            취소
          </Button>
          <Button fullWidth variant="contained" color="success" onClick={submitComplete}>
            확인
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={Boolean(cancelTarget)}
        onClose={() => setCancelTarget(null)}
        fullWidth
        maxWidth="xs"
        slotProps={{ paper: { sx: { borderRadius: 2 } } }}
      >
        <DialogTitle sx={{ textAlign: 'center', fontWeight: 800, pb: 0 }}>완료 취소</DialogTitle>
        <DialogContent>
          <Typography align="center" sx={{ mt: 1 }}>
            완료 처리를 취소하시겠습니까?
          </Typography>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3, gap: 1 }}>
          <Button fullWidth variant="contained" color="inherit" onClick={() => setCancelTarget(null)}>
            아니요
          </Button>
          <Button fullWidth variant="contained" color="error" onClick={submitCancel}>
            예
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
