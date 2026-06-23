import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    primary: { main: '#1A56C4' },
    background: { default: '#F5F6F8' },
  },
  typography: {
    fontFamily: `'Pretendard', 'Apple SD Gothic Neo', 'Malgun Gothic', system-ui, sans-serif`,
  },
  shape: { borderRadius: 8 },
});
