import { useEffect, useState } from 'react';
import {
  AppBar,
  Avatar,
  Badge,
  Box,
  Button,
  Chip,
  IconButton,
  Popover,
  Stack,
  Toolbar,
  Tooltip,
  Typography,
} from '@mui/material';
import ShieldIcon from '@mui/icons-material/Shield';
import NotificationsNoneIcon from '@mui/icons-material/NotificationsNone';
import PersonIcon from '@mui/icons-material/Person';
import LogoutIcon from '@mui/icons-material/Logout';
import { useNavigate } from 'react-router-dom';
import { useOutbreakAlertStore } from '../../store/useOutbreakAlertStore';
import { useAuthStore } from '../../store/useAuthStore';
import { useInterval } from '../../hooks/useInterval';

const POLL_INTERVAL_MS = 60000; // 1분 — 배차 상태 폴링(8초)보다 여유 있게

function formatAlertDate(value: string | null) {
  if (!value || value.length !== 8) return value ?? '';
  return `${value.slice(0, 4)}-${value.slice(4, 6)}-${value.slice(6, 8)}`;
}

export function AppHeader() {
  const navigate = useNavigate();
  const logout = useAuthStore((s) => s.logout);
  const badgeCount = useOutbreakAlertStore((s) => s.badgeCount);
  const lastCheckedDate = useOutbreakAlertStore((s) => s.lastCheckedDate);
  const cases = useOutbreakAlertStore((s) => s.cases);
  const checkOutbreaks = useOutbreakAlertStore((s) => s.checkOutbreaks);
  const clearBadge = useOutbreakAlertStore((s) => s.clearBadge);

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };
  const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null);

  useEffect(() => {
    void checkOutbreaks();
  }, [checkOutbreaks]);

  useInterval(() => void checkOutbreaks(), POLL_INTERVAL_MS);

  return (
    <AppBar
      position="static"
      color="inherit"
      elevation={0}
      sx={{ borderBottom: '1px solid', borderColor: 'divider' }}
    >
      <Toolbar sx={{ gap: 1 }}>
        <ShieldIcon color="primary" />
        <Typography variant="h6" sx={{ fontWeight: 700, flexShrink: 0 }}>
          가축전염병 방역 배치 시스템
        </Typography>
        <Box sx={{ flex: 1 }} />
        <Tooltip title={badgeCount > 0 ? `신규 발생 신고 ${badgeCount}건` : '새 알림 없음'}>
          <IconButton aria-label="알림" onClick={(event) => setAnchorEl(event.currentTarget)}>
            <Badge color="error" badgeContent={badgeCount} max={99} invisible={badgeCount === 0}>
              <NotificationsNoneIcon />
            </Badge>
          </IconButton>
        </Tooltip>
        <Popover
          open={Boolean(anchorEl)}
          anchorEl={anchorEl}
          onClose={() => setAnchorEl(null)}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
          transformOrigin={{ vertical: 'top', horizontal: 'right' }}
        >
          <Box sx={{ p: 2, width: 320 }}>
            {badgeCount > 0 ? (
              <>
                <Typography sx={{ fontWeight: 700, mb: 0.5 }}>
                  {`신규 발생 신고 ${badgeCount}건`}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
                  {`${formatAlertDate(lastCheckedDate)} 기준으로 새로 확인된 발생 신고입니다.`}
                </Typography>
                {cases.length > 0 && (
                  <Stack spacing={1} sx={{ mb: 1.5, maxHeight: 280, overflowY: 'auto' }}>
                    {cases.map((c, index) => (
                      <Box
                        key={index}
                        sx={{ p: 1, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}
                      >
                        <Stack direction="row" sx={{ alignItems: 'center', justifyContent: 'space-between' }}>
                          <Typography variant="body2" sx={{ fontWeight: 700 }}>
                            {c.farmName ?? '농장명 미상'}
                          </Typography>
                          {c.isTest && <Chip label="TEST" size="small" color="warning" />}
                        </Stack>
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                          {`${c.disease ?? '질병 미상'} · ${c.region ?? '지역 미상'}`}
                        </Typography>
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                          {`확진일 ${c.confirmedAt ?? '-'}`}
                        </Typography>
                      </Box>
                    ))}
                  </Stack>
                )}
                <Button
                  fullWidth
                  size="small"
                  variant="contained"
                  onClick={() => {
                    clearBadge();
                    setAnchorEl(null);
                  }}
                >
                  확인
                </Button>
              </>
            ) : (
              <Typography variant="body2" color="text.secondary">
                새 알림이 없습니다.
              </Typography>
            )}
          </Box>
        </Popover>
        <Tooltip title="로그아웃">
          <Stack
            direction="row"
            spacing={0.5}
            sx={{ alignItems: 'center', cursor: 'pointer', pl: 1 }}
            onClick={handleLogout}
          >
            <Avatar sx={{ width: 28, height: 28, bgcolor: 'grey.200' }}>
              <PersonIcon sx={{ color: 'grey.600', fontSize: 18 }} />
            </Avatar>
            <Typography variant="body2">관리자</Typography>
            <LogoutIcon fontSize="small" sx={{ color: 'text.secondary' }} />
          </Stack>
        </Tooltip>
      </Toolbar>
    </AppBar>
  );
}
