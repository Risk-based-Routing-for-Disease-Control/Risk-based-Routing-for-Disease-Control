import { Alert } from '@mui/material';
import { useFarmStore } from '../../store/useFarmStore';

export function DataSourceBanner() {
  const dataSource = useFarmStore((s) => s.dataSource);
  const loadError = useFarmStore((s) => s.loadError);

  if (dataSource !== 'dummy') return null;

  return (
    <Alert severity="warning" square sx={{ borderRadius: 0, py: 0.25 }}>
      {`실시간 농장 데이터 연동에 실패하여 임시 데이터를 표시하고 있습니다.${loadError ? ` (${loadError})` : ''}`}
    </Alert>
  );
}
