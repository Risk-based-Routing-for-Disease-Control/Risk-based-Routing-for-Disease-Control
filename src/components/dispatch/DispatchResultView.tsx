import { Box, Button, IconButton, Stack, Tooltip, Typography } from '@mui/material';
import HelpOutlineIcon from '@mui/icons-material/HelpOutlineOutlined';
import RefreshIcon from '@mui/icons-material/Refresh';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutlineOutlined';
import { useNavigate } from 'react-router-dom';
import { useDispatchStore } from '../../store/useDispatchStore';
import { RouteMap } from '../route/RouteMap';
import { TeamSummaryCard } from '../route/TeamSummaryCard';
import { UnassignedFarmsCard } from '../route/UnassignedFarmsCard';
import { durationLabel } from '../../utils/time';
import type { DispatchResult } from '../../types/dispatch';

interface DispatchResultViewProps {
  result: DispatchResult;
}

export function DispatchResultView({ result }: DispatchResultViewProps) {
  const navigate = useNavigate();
  const resetResult = useDispatchStore((s) => s.resetResult);
  const confirmDispatch = useDispatchStore((s) => s.confirmDispatch);

  const handleRestart = () => resetResult();
  const handleConfirm = () => {
    confirmDispatch();
    navigate('/confirmed');
  };

  return (
    <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
      <Stack sx={{ px: 3, pt: 3, pb: 2 }}>
        <Stack direction="row" spacing={0.5} sx={{ alignItems: 'center' }}>
          <Typography variant="h5" sx={{ fontWeight: 700 }}>
            경로 배치 결과
          </Typography>
          <Tooltip title="농장 선택 후 가용 팀 수에 맞춰 자동으로 배분된 결과입니다.">
            <IconButton size="small">
              <HelpOutlineIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Stack>
        <Typography variant="body2" color="text.secondary">
          {`선택 농장 ${result.selectedFarmCount}곳  |  가용 팀 ${result.teamCount}팀  |  총 예상 소요시간 ${durationLabel(result.totalDurationMinutes)}`}
        </Typography>
      </Stack>

      <Box sx={{ flex: 1, display: 'flex', minHeight: 0, px: 3, pb: 2, gap: 2 }}>
        <Box sx={{ flex: 1, position: 'relative', minWidth: 0, borderRadius: 1.5, overflow: 'hidden' }}>
          <RouteMap teams={result.teams} />
        </Box>
        <Box sx={{ width: 320, flexShrink: 0, overflowY: 'auto' }}>
          {result.teams.map((team) => (
            <TeamSummaryCard key={team.id} team={team} />
          ))}
          <UnassignedFarmsCard farms={result.unassignedFarms} selectedFarmCount={result.selectedFarmCount} />
        </Box>
      </Box>

      <Stack
        direction="row"
        spacing={2}
        sx={{ alignItems: 'center', justifyContent: 'space-between', px: 3, py: 2, borderTop: '1px solid', borderColor: 'divider' }}
      >
        <Button variant="outlined" startIcon={<RefreshIcon />} onClick={handleRestart}>
          다시하기 (경로 배치 설정으로)
        </Button>
        <Button variant="contained" startIcon={<CheckCircleOutlineIcon />} onClick={handleConfirm}>
          확정하기 (확정 경로로 이동)
        </Button>
      </Stack>
    </Box>
  );
}
