import type { DispatchResult } from '../types/dispatch';
import type { Farm } from '../types/farm';
import { normalizeFarmDuration } from '../utils/farmDuration';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? '';

export interface DispatchSolveRequest {
  farms: Farm[];
  selectedFarmIds: string[];
  teamCount: number;
}

export async function solveDispatch(request: DispatchSolveRequest): Promise<DispatchResult> {
  const response = await fetch(`${API_BASE_URL}/api/dispatch/solve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...request, farms: request.farms.map(normalizeFarmDuration) }),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Dispatch request failed (${response.status}): ${detail}`);
  }

  return (await response.json()) as DispatchResult;
}
