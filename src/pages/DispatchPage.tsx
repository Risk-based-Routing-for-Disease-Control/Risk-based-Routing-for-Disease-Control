import { useDispatchStore } from '../store/useDispatchStore';
import { DispatchSettingsView } from '../components/dispatch/DispatchSettingsView';
import { DispatchResultView } from '../components/dispatch/DispatchResultView';

export function DispatchPage() {
  const result = useDispatchStore((s) => s.result);

  if (result) {
    return <DispatchResultView result={result} />;
  }

  return <DispatchSettingsView />;
}
