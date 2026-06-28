import { Navigate } from 'react-router-dom';
import { useDispatchStore } from '../store/useDispatchStore';
import { DispatchResultView } from '../components/dispatch/DispatchResultView';

export function DispatchPage() {
  const result = useDispatchStore((s) => s.result);

  if (result) {
    return <DispatchResultView result={result} />;
  }

  return <Navigate to="/map" replace />;
}
