import { AppBar, Avatar, Badge, Box, IconButton, Stack, Toolbar, Typography } from '@mui/material';
import ShieldIcon from '@mui/icons-material/Shield';
import NotificationsNoneIcon from '@mui/icons-material/NotificationsNone';
import PersonIcon from '@mui/icons-material/Person';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

export function AppHeader() {
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
        <IconButton aria-label="알림">
          <Badge color="error" variant="dot">
            <NotificationsNoneIcon />
          </Badge>
        </IconButton>
        <Stack direction="row" spacing={0.5} sx={{ alignItems: 'center', cursor: 'pointer', pl: 1 }}>
          <Avatar sx={{ width: 28, height: 28, bgcolor: 'grey.200' }}>
            <PersonIcon sx={{ color: 'grey.600', fontSize: 18 }} />
          </Avatar>
          <Typography variant="body2">관리자</Typography>
          <ExpandMoreIcon fontSize="small" sx={{ color: 'text.secondary' }} />
        </Stack>
      </Toolbar>
    </AppBar>
  );
}
