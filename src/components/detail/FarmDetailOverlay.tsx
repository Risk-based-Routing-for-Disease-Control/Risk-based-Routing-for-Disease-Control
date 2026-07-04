import { Box, Button, Chip, IconButton, Paper, Stack, Typography } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { useFarmStore } from '../../store/useFarmStore';
import { useEmergencyModeStore } from '../../store/useEmergencyModeStore';
import { RISK_LEVEL_COLOR, RISK_LEVEL_LABEL } from '../../constants/risk';
import { getLivestockDisplayLabel } from '../../utils/livestock';
import { LivestockIcon } from '../common/LivestockIcon';
import { XaiFactorIcons } from './XaiFactorIcons';

const MAX_VISIBLE_XAI_FACTORS = 3;

export function FarmDetailOverlay() {
  const farms = useFarmStore((s) => s.farms);
  const selectedFarmId = useFarmStore((s) => s.selectedFarmId);
  const clearSelection = useFarmStore((s) => s.clearSelection);
  const toggleSuspected = useFarmStore((s) => s.toggleSuspected);
  const emergencyActive = useEmergencyModeStore((s) => s.isActive);
  const farm = farms.find((item) => item.id === selectedFarmId);
  const visibleXaiFactors = farm?.xaiFactors.slice(0, MAX_VISIBLE_XAI_FACTORS) ?? [];
  const hiddenXaiFactorCount = Math.max(0, (farm?.xaiFactors.length ?? 0) - MAX_VISIBLE_XAI_FACTORS);

  if (!farm) return null;

  return (
    <Paper
      elevation={0}
      sx={{
        position: 'absolute',
        left: 16,
        right: 16,
        bottom: 16,
        zIndex: 20,
        borderRadius: 1.5,
        overflow: 'hidden',
        bgcolor: 'rgba(255, 255, 255, 0.96)',
        boxShadow: '0 14px 34px rgba(15, 23, 42, 0.18)',
        backdropFilter: 'blur(4px)',
      }}
    >
      <Stack
        direction="row"
        sx={{ alignItems: 'center', justifyContent: 'space-between', px: 2, py: 1.5 }}
      >
        <Stack direction="row" spacing={1.25} sx={{ alignItems: 'center', minWidth: 0 }}>
          <Typography variant="h6" sx={{ fontWeight: 700 }}>
            {farm.name}
          </Typography>
          <Chip
            size="small"
            label={RISK_LEVEL_LABEL[farm.riskLevel]}
            sx={{ bgcolor: RISK_LEVEL_COLOR[farm.riskLevel], color: '#fff', fontWeight: 700 }}
          />
        </Stack>
        <Stack direction="row" spacing={1} sx={{ alignItems: 'center', flexShrink: 0 }}>
          <Button
            size="small"
            variant="outlined"
            color="error"
            onClick={() =>
              useEmergencyModeStore
                .getState()
                .enterWithCenter({ lat: farm.lat, lng: farm.lng }, `${farm.name} · 수동 지정`)
            }
          >
            비상모드 진입
          </Button>
          {emergencyActive && (
            <Button
              size="small"
              variant={farm.suspectedFarm ? 'contained' : 'outlined'}
              color="warning"
              onClick={() => void toggleSuspected(farm.id, !farm.suspectedFarm)}
            >
              {farm.suspectedFarm ? '의심 농장 해제' : '의심 농장 지정'}
            </Button>
          )}
          <IconButton size="small" onClick={clearSelection} aria-label="농장 상세 닫기">
            <CloseIcon fontSize="small" />
          </IconButton>
        </Stack>
      </Stack>

      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', md: '1.1fr 0.9fr 0.9fr' },
          columnGap: { xs: 0, md: 3 },
          rowGap: 1.5,
          px: 2,
          pb: 1.75,
        }}
      >
        <Stack spacing={0.75} sx={{ py: 1 }}>
          <Typography variant="caption" color="text.secondary">
            농장 고유번호
          </Typography>
          <Typography variant="body2" sx={{ fontWeight: 600 }}>
            {farm.code}
          </Typography>
          <Typography variant="caption" color="text.secondary" sx={{ pt: 0.5 }}>
            주소
          </Typography>
          <Typography variant="body2">{farm.address}</Typography>
        </Stack>

        <Stack direction="row" spacing={1.5} sx={{ alignItems: 'center', py: 1 }}>
          <LivestockIcon livestockType={farm.livestockType} size={32} />
          <Box>
            <Typography variant="caption" color="text.secondary">
              축종
            </Typography>
            <Typography variant="body2" sx={{ fontWeight: 700 }}>
              {getLivestockDisplayLabel(farm.livestockType)}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              사육 두수
            </Typography>
            <Typography variant="body2" sx={{ fontWeight: 700 }}>
              {`${farm.livestockCount.toLocaleString()} ${farm.livestockUnit}`}
            </Typography>
          </Box>
        </Stack>

        <Stack spacing={0.75} sx={{ py: 1 }}>
          <Typography variant="caption" color="text.secondary">
            위험도 점수
          </Typography>
          <Chip
            label={`${farm.riskScore.toFixed(2)} (${RISK_LEVEL_LABEL[farm.riskLevel]})`}
            sx={{
              alignSelf: 'flex-start',
              bgcolor: RISK_LEVEL_COLOR[farm.riskLevel],
              color: '#fff',
              fontWeight: 700,
            }}
          />
          {visibleXaiFactors.length > 0 && (
            <Stack direction="row" spacing={0.75} sx={{ alignItems: 'center' }}>
              <XaiFactorIcons factors={visibleXaiFactors} size={30} imageSize={18} />
              {hiddenXaiFactorCount > 0 && (
                <Chip
                  size="small"
                  label={`+${hiddenXaiFactorCount}`}
                  sx={{ bgcolor: 'grey.100', color: 'text.secondary', fontWeight: 700 }}
                />
              )}
            </Stack>
          )}
        </Stack>
      </Box>
    </Paper>
  );
}
