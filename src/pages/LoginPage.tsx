import { useState, type FormEvent } from 'react';
import { Box, Button, Paper, Stack, TextField, Typography } from '@mui/material';
import ShieldIcon from '@mui/icons-material/Shield';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/useAuthStore';

export function LoginPage() {
  const navigate = useNavigate();
  const login = useAuthStore((s) => s.login);
  const [userId, setUserId] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(false);

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    const ok = login(userId, password);
    if (ok) {
      navigate('/map', { replace: true });
      return;
    }
    setError(true);
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'grey.100',
        px: 2,
      }}
    >
      <Paper elevation={2} sx={{ p: 4, width: 360, borderRadius: 2 }}>
        <Stack spacing={0.5} sx={{ alignItems: 'center', mb: 3 }}>
          <ShieldIcon color="primary" sx={{ fontSize: 32 }} />
          <Typography variant="h6" sx={{ fontWeight: 700, textAlign: 'center' }}>
            가축전염병 방역 배치 시스템
          </Typography>
        </Stack>
        <Box component="form" onSubmit={handleSubmit}>
          <Stack spacing={2}>
            <TextField
              label="아이디"
              value={userId}
              onChange={(event) => {
                setUserId(event.target.value);
                setError(false);
              }}
              error={error}
              autoFocus
              fullWidth
            />
            <TextField
              label="비밀번호 (8자리)"
              type="password"
              value={password}
              onChange={(event) => {
                setPassword(event.target.value.slice(0, 8));
                setError(false);
              }}
              error={error}
              helperText={error ? '아이디 또는 비밀번호를 확인해주세요.' : ' '}
              slotProps={{ htmlInput: { maxLength: 8 } }}
              fullWidth
            />
            <Button type="submit" variant="contained" fullWidth>
              로그인
            </Button>
          </Stack>
        </Box>
      </Paper>
    </Box>
  );
}
