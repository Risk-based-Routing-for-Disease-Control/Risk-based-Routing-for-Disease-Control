import { Box, Chip, Divider, IconButton, Paper, Stack, Typography } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { useFarmStore } from '../../store/useFarmStore';
import { RISK_LEVEL_COLOR, RISK_LEVEL_LABEL } from '../../constants/risk';
import { LivestockIcon } from '../common/LivestockIcon';

export function FarmDetailOverlay() {
  const farms = useFarmStore((s) => s.farms);
  const selectedFarmId = useFarmStore((s) => s.selectedFarmId);
  const clearSelection = useFarmStore((s) => s.clearSelection);
  const farm = farms.find((item) => item.id === selectedFarmId);

  if (!farm) return null;

  return (
    <Paper
      elevation={3}
      sx={{
        position: 'absolute',
        left: 16,
        right: 16,
        bottom: 16,
        zIndex: 20,
        borderRadius: 1.5,
        overflow: 'hidden',
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
        <IconButton size="small" onClick={clearSelection} aria-label="농장 상세 닫기">
          <CloseIcon fontSize="small" />
        </IconButton>
      </Stack>

      <Divider />

      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', md: '1.1fr 0.9fr 0.9fr' },
          gap: 0,
        }}
      >
        <Stack spacing={0.75} sx={{ px: 2, py: 1.5, borderRight: { md: '1px solid' }, borderColor: 'divider' }}>
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

        <Stack direction="row" spacing={1.5} sx={{ alignItems: 'center', px: 2, py: 1.5, borderRight: { md: '1px solid' }, borderColor: 'divider' }}>
          <LivestockIcon livestockType={farm.livestockType} size={32} />
          <Box>
            <Typography variant="caption" color="text.secondary">
              축종
            </Typography>
            <Typography variant="body2" sx={{ fontWeight: 700 }}>
              {farm.livestockType}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              사육 두수
            </Typography>
            <Typography variant="body2" sx={{ fontWeight: 700 }}>
              {`${farm.livestockCount.toLocaleString()} ${farm.livestockUnit}`}
            </Typography>
          </Box>
        </Stack>

        <Stack spacing={0.75} sx={{ px: 2, py: 1.5 }}>
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
          <Typography variant="caption" color="text.secondary">
            0에 가까울수록 안전, 1에 가까울수록 위험
          </Typography>
        </Stack>
      </Box>
    </Paper>
  );
}
