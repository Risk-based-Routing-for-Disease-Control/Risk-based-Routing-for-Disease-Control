import { useMemo, useState } from 'react';
import {
  Box,
  Button,
  Checkbox,
  Chip,
  FormControl,
  IconButton,
  MenuItem,
  Paper,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import RefreshIcon from '@mui/icons-material/Refresh';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';
import { useFarmStore } from '../../store/useFarmStore';
import { useDispatchStore } from '../../store/useDispatchStore';
import { RISK_LEVEL_COLOR, RISK_LEVEL_LABEL, RISK_LEVELS } from '../../constants/risk';
import type { RiskLevel } from '../../types/farm';
import { LivestockIcon } from '../common/LivestockIcon';

interface DispatchSettingsViewProps {
  variant?: 'page' | 'panel';
  onDispatchComplete?: () => void;
}

export function DispatchSettingsView({ variant = 'page', onDispatchComplete }: DispatchSettingsViewProps) {
  const farms = useFarmStore((s) => s.farms);
  const selectFarm = useFarmStore((s) => s.selectFarm);

  const teamCount = useDispatchStore((s) => s.teamCount);
  const selectedFarmIds = useDispatchStore((s) => s.selectedFarmIds);
  const isDispatching = useDispatchStore((s) => s.isDispatching);
  const dispatchError = useDispatchStore((s) => s.dispatchError);
  const riskFilter = useDispatchStore((s) => s.riskFilter);
  const typeFilter = useDispatchStore((s) => s.typeFilter);
  const setTeamCount = useDispatchStore((s) => s.setTeamCount);
  const setRiskFilter = useDispatchStore((s) => s.setRiskFilter);
  const setTypeFilter = useDispatchStore((s) => s.setTypeFilter);
  const toggleFarm = useDispatchStore((s) => s.toggleFarm);
  const setSelectedFarmIds = useDispatchStore((s) => s.setSelectedFarmIds);
  const resetSelection = useDispatchStore((s) => s.resetSelection);
  const runDispatch = useDispatchStore((s) => s.runDispatch);

  const [sortDesc, setSortDesc] = useState(true);

  const livestockTypes = useMemo(
    () => Array.from(new Set(farms.map((farm) => farm.livestockType))),
    [farms],
  );

  const filteredFarms = useMemo(() => {
    const list = farms.filter((farm) => {
      if (riskFilter !== 'all' && farm.riskLevel !== riskFilter) return false;
      if (typeFilter !== 'all' && farm.livestockType !== typeFilter) return false;
      return true;
    });
    return list.sort((a, b) => (sortDesc ? b.riskScore - a.riskScore : a.riskScore - b.riskScore));
  }, [farms, riskFilter, typeFilter, sortDesc]);

  const allFilteredSelected =
    filteredFarms.length > 0 && filteredFarms.every((farm) => selectedFarmIds.includes(farm.id));
  const someFilteredSelected = filteredFarms.some((farm) => selectedFarmIds.includes(farm.id));

  const handleToggleSelectAll = () => {
    const filteredIds = filteredFarms.map((farm) => farm.id);
    if (allFilteredSelected) {
      setSelectedFarmIds(selectedFarmIds.filter((id) => !filteredIds.includes(id)));
    } else {
      setSelectedFarmIds(Array.from(new Set([...selectedFarmIds, ...filteredIds])));
    }
  };

  const canDispatch = teamCount >= 1 && selectedFarmIds.length >= 1 && !isDispatching;

  const handleDispatch = async () => {
    if (!canDispatch) return;
    await runDispatch(farms);
    if (useDispatchStore.getState().result) {
      onDispatchComplete?.();
    }
  };

  const isPanel = variant === 'panel';

  return (
    <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
      <Box sx={{ flex: 1, overflowY: 'auto', p: isPanel ? 2 : 3 }}>
        {!isPanel && (
          <Typography variant="h5" sx={{ fontWeight: 700, mb: 3 }}>
            경로 배치 설정
          </Typography>
        )}

        <Paper variant="outlined" sx={{ borderRadius: 1.5, p: isPanel ? 2 : 2.5, mb: isPanel ? 2 : 3 }}>
          <Typography sx={{ fontWeight: 700, mb: 1.5 }}>오늘 가용 팀 수</Typography>
          <Stack direction="row" spacing={1.5} sx={{ alignItems: 'center' }}>
            <IconButton
              size="small"
              onClick={() => setTeamCount(teamCount - 1)}
              disabled={teamCount <= 1}
              sx={{ border: '1px solid', borderColor: 'divider' }}
            >
              <RemoveIcon fontSize="small" />
            </IconButton>
            <Typography variant="h6" sx={{ minWidth: 32, textAlign: 'center' }}>
              {teamCount}
            </Typography>
            <IconButton
              size="small"
              onClick={() => setTeamCount(teamCount + 1)}
              sx={{ border: '1px solid', borderColor: 'divider' }}
            >
              <AddIcon fontSize="small" />
            </IconButton>
            <Typography color="text.secondary">팀</Typography>
          </Stack>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
            1팀 = 방역관 2인 + 소독차 1대
          </Typography>
        </Paper>

        <Paper variant="outlined" sx={{ borderRadius: 1.5, p: isPanel ? 2 : 2.5 }}>
          <Stack direction="row" sx={{ alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Typography sx={{ fontWeight: 700 }}>농장 선택</Typography>
            <Button size="small" startIcon={<RefreshIcon fontSize="small" />} onClick={resetSelection}>
              초기화
            </Button>
          </Stack>

          <Stack direction={isPanel ? 'column' : 'row'} spacing={isPanel ? 1 : 2} sx={{ mb: 2 }}>
            <FormControl size="small" sx={{ minWidth: 140 }}>
              <Select
                value={riskFilter}
                onChange={(event) => setRiskFilter(event.target.value as RiskLevel | 'all')}
                displayEmpty
              >
                <MenuItem value="all">위험도 등급: 전체</MenuItem>
                {RISK_LEVELS.map((level) => (
                  <MenuItem key={level.value} value={level.value}>
                    {level.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl size="small" sx={{ minWidth: 140 }}>
              <Select value={typeFilter} onChange={(event) => setTypeFilter(event.target.value)} displayEmpty>
                <MenuItem value="all">축종: 전체</MenuItem>
                {livestockTypes.map((type) => (
                  <MenuItem key={type} value={type}>
                    {type}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Stack>

          <Stack direction="row" spacing={1} sx={{ alignItems: 'center', mb: 1 }}>
            <Checkbox
              size="small"
              checked={allFilteredSelected}
              indeterminate={!allFilteredSelected && someFilteredSelected}
              onChange={handleToggleSelectAll}
            />
            <Typography variant="body2">전체 선택</Typography>
          </Stack>

          <Box sx={{ overflowX: 'auto' }}>
            <Table size="small" sx={{ minWidth: isPanel ? 520 : undefined }}>
              <TableHead>
                <TableRow>
                  <TableCell padding="checkbox" />
                  <TableCell>농장명</TableCell>
                  <TableCell onClick={() => setSortDesc((value) => !value)} sx={{ cursor: 'pointer' }}>
                    <Stack direction="row" sx={{ alignItems: 'center' }}>
                      위험도 등급
                      <ArrowDropDownIcon
                        fontSize="small"
                        sx={{ transform: sortDesc ? 'none' : 'rotate(180deg)' }}
                      />
                    </Stack>
                  </TableCell>
                  <TableCell>축종</TableCell>
                  <TableCell align="right">사육 두수</TableCell>
                  <TableCell align="right">예상 소요시간</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredFarms.map((farm) => (
                  <TableRow
                    key={farm.id}
                    hover
                    selected={selectedFarmIds.includes(farm.id)}
                    onClick={() => selectFarm(farm.id)}
                    sx={{ cursor: 'pointer' }}
                  >
                    <TableCell padding="checkbox">
                      <Checkbox
                        size="small"
                        checked={selectedFarmIds.includes(farm.id)}
                        onClick={(event) => event.stopPropagation()}
                        onChange={() => toggleFarm(farm.id)}
                      />
                    </TableCell>
                    <TableCell>{farm.name}</TableCell>
                    <TableCell>
                      <Chip
                        size="small"
                        label={RISK_LEVEL_LABEL[farm.riskLevel]}
                        sx={{ bgcolor: RISK_LEVEL_COLOR[farm.riskLevel], color: '#fff', fontWeight: 700 }}
                      />
                    </TableCell>
                    <TableCell>
                      <Stack direction="row" spacing={0.75} sx={{ alignItems: 'center' }}>
                        <LivestockIcon livestockType={farm.livestockType} size={22} />
                        <Typography variant="body2">{farm.livestockType}</Typography>
                      </Stack>
                    </TableCell>
                    <TableCell align="right">{`${farm.livestockCount.toLocaleString()} ${farm.livestockUnit}`}</TableCell>
                    <TableCell align="right">{`${farm.estimatedDurationMinutes}분`}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Box>
        </Paper>
      </Box>

      <Stack
        spacing={1}
        sx={{ alignItems: 'center', px: 3, py: 2, borderTop: '1px solid', borderColor: 'divider' }}
      >
        <Button
          variant="contained"
          fullWidth
          size="large"
          disabled={!canDispatch}
          onClick={handleDispatch}
          sx={{ maxWidth: 480 }}
        >
          {isDispatching ? '배치 중...' : '배치하기'}
        </Button>
        {dispatchError && (
          <Typography variant="caption" color="error">
            {dispatchError}
          </Typography>
        )}
        {!canDispatch && (
          <Typography variant="caption" color="text.secondary">
            팀 수를 입력하고 최소 1개 이상의 농장을 선택해주세요.
          </Typography>
        )}
      </Stack>
    </Box>
  );
}
