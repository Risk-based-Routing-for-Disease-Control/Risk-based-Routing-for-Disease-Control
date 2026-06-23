import { Avatar, Box, Button, Chip, Divider, IconButton, Stack, Typography } from '@mui/material';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import CloseIcon from '@mui/icons-material/Close';
import ScheduleIcon from '@mui/icons-material/Schedule';
import HomeWorkIcon from '@mui/icons-material/HomeWork';
import FlightIcon from '@mui/icons-material/Flight';
import LocalShippingIcon from '@mui/icons-material/LocalShipping';
import { useFarmStore } from '../../store/useFarmStore';
import { RISK_LEVEL_COLOR, RISK_LEVEL_LABEL } from '../../constants/risk';
import type { XaiFactor } from '../../types/farm';

const XAI_ICONS: Record<XaiFactor['icon'], typeof FlightIcon> = {
  bird: FlightIcon,
  truck: LocalShippingIcon,
};

const PANEL_WIDTH = 360;

export function FarmDetailPanel() {
  const farms = useFarmStore((s) => s.farms);
  const selectedFarmId = useFarmStore((s) => s.selectedFarmId);
  const clearSelection = useFarmStore((s) => s.clearSelection);
  const farm = farms.find((f) => f.id === selectedFarmId);

  return (
    <Box
      sx={{
        width: PANEL_WIDTH,
        flexShrink: 0,
        height: '100%',
        borderLeft: '1px solid',
        borderColor: 'divider',
        bgcolor: 'background.paper',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <Stack
        direction="row"
        sx={{
          alignItems: 'center',
          justifyContent: 'space-between',
          px: 1.5,
          py: 1.5,
          borderBottom: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Stack direction="row" spacing={0.25} sx={{ alignItems: 'center' }}>
          {farm && (
            <IconButton size="small" onClick={clearSelection} aria-label="뒤로가기">
              <ChevronLeftIcon fontSize="small" />
            </IconButton>
          )}
          <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
            농장 상세 정보
          </Typography>
        </Stack>
        {farm && (
          <IconButton size="small" onClick={clearSelection} aria-label="닫기">
            <CloseIcon fontSize="small" />
          </IconButton>
        )}
      </Stack>

      {farm ? (
        <Box sx={{ flex: 1, overflowY: 'auto' }}>
          <Box sx={{ px: 2, py: 2 }}>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
              농장 고유번호
            </Typography>
            <Typography variant="h6" sx={{ fontWeight: 700 }}>
              {farm.code}
            </Typography>
          </Box>
          <Divider />

          <Box sx={{ px: 2, py: 2 }}>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
              위험도 점수
            </Typography>
            <Chip
              label={`${farm.riskScore.toFixed(2)} (${RISK_LEVEL_LABEL[farm.riskLevel]})`}
              sx={{
                bgcolor: RISK_LEVEL_COLOR[farm.riskLevel],
                color: '#fff',
                fontWeight: 700,
                fontSize: 14,
                height: 32,
              }}
            />
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
              ※ 0에 가까울수록 안전, 1에 가까울수록 위험
            </Typography>
          </Box>
          <Divider />

          <Box sx={{ px: 2, py: 2 }}>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
              XAI: 주요 위험 요인
            </Typography>
            <Stack spacing={1} sx={{ alignItems: 'flex-start' }}>
              {farm.xaiFactors.length === 0 && (
                <Typography variant="body2" color="text.secondary">
                  탐지된 주요 위험 요인이 없습니다
                </Typography>
              )}
              {farm.xaiFactors.map((factor) => {
                const Icon = XAI_ICONS[factor.icon];
                return (
                  <Chip
                    key={factor.id}
                    icon={<Icon fontSize="small" sx={{ color: '#C62828 !important' }} />}
                    label={factor.label}
                    sx={{ bgcolor: '#FDECEA', color: '#C62828', fontWeight: 600 }}
                  />
                );
              })}
            </Stack>
          </Box>
          <Divider />

          <Box sx={{ px: 2, py: 2 }}>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
              주소
            </Typography>
            <Typography variant="body2">{farm.address}</Typography>
          </Box>
          <Divider />

          <Stack direction="row" sx={{ px: 2, py: 2 }}>
            <Box sx={{ flex: 1 }}>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                축종
              </Typography>
              <Typography variant="body1" sx={{ fontWeight: 600 }}>
                {farm.livestockType}
              </Typography>
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                사육 두수
              </Typography>
              <Typography variant="body1" sx={{ fontWeight: 600 }}>
                {farm.livestockCount.toLocaleString()}{' '}
                <Typography component="span" variant="body2" color="text.secondary">
                  {farm.livestockUnit}
                </Typography>
              </Typography>
            </Box>
          </Stack>
          <Divider />

          <Stack direction="row" sx={{ alignItems: 'center', justifyContent: 'space-between', px: 2, py: 2 }}>
            <Stack direction="row" spacing={0.75} sx={{ alignItems: 'flex-start', color: 'text.secondary' }}>
              <ScheduleIcon fontSize="small" sx={{ mt: 0.25 }} />
              <Box>
                <Typography variant="caption" sx={{ display: 'block' }}>
                  최종 업데이트
                </Typography>
                <Typography variant="caption">{farm.lastUpdatedAt}</Typography>
              </Box>
            </Stack>
            <Button size="small" endIcon={<ChevronRightIcon />}>
              상세 이력 보기
            </Button>
          </Stack>
        </Box>
      ) : (
        <Stack spacing={2} sx={{ flex: 1, alignItems: 'center', justifyContent: 'center', px: 4 }}>
          <Avatar sx={{ width: 72, height: 72, bgcolor: 'grey.100' }}>
            <HomeWorkIcon sx={{ color: 'grey.400', fontSize: 36 }} />
          </Avatar>
          <Typography color="text.secondary" align="center">
            농장을 클릭하면
            <br />
            상세 정보가 표시됩니다
          </Typography>
        </Stack>
      )}
    </Box>
  );
}
