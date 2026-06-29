import type { DispatchResult, DispatchStop, DispatchTeam } from '../types/dispatch';
import type { Farm } from '../types/farm';
import { normalizeFarmDuration } from '../utils/farmDuration';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? '';

// ── 구버전 (하위 호환) ──────────────────────────────────────────────────────
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

// ── 신규 엔드포인트 (POST /api/route-assignment) ──────────────────────────
interface ApiStop {
  stopOrder: number;
  farmId: string | null;
  facilityId: string | null;
  name: string;
  estimatedDuration: number;
}

interface ApiTeam {
  teamId: string;
  teamNo: number;
  teamLabel: string;
  color: string;
  totalDuration: number;
  stops: ApiStop[];
}

interface RouteAssignmentResponse {
  dispatchRunId: string;
  status: string;
  totalEstimatedDuration: number;
  teams: ApiTeam[];
  unassignedFarms: { farmId: string; reason: string }[];
}

export interface RouteAssignmentRequest {
  teamCount: number;
  farmIds: string[];
  farms: Farm[];
  depotName?: string;
  depotLat?: number;
  depotLng?: number;
  maxRouteMinutes?: number;
  disinfectServiceMinutes?: number;
  allowUnassigned?: boolean;
}

function mapToDispatchResult(
  data: RouteAssignmentResponse,
  farmMap: Map<string, Farm>,
  teamCount: number,
  selectedFarmIds: string[],
): DispatchResult {
  const teams: DispatchTeam[] = data.teams.map((t) => {
    const stops: DispatchStop[] = t.stops
      .filter((s) => s.farmId !== null)
      .map((s) => ({
        farm: farmMap.get(s.farmId!) ?? {
          id: s.farmId!,
          code: s.farmId!,
          name: s.name,
          lat: 0,
          lng: 0,
          riskScore: 0,
          riskLevel: 'warning' as const,
          livestockType: '미상',
          livestockCount: 0,
          livestockUnit: '두',
          estimatedDurationMinutes: s.estimatedDuration,
          address: '',
          xaiFactors: [],
          lastUpdatedAt: '',
        },
        order: s.stopOrder,
        status: 'upcoming' as const,
      }));

    return {
      id: t.teamId,
      label: t.teamLabel,
      color: t.color,
      stops,
      totalDurationMinutes: t.totalDuration,
    };
  });

  const unassignedFarms = data.unassignedFarms
    .map((u) => farmMap.get(u.farmId))
    .filter((f): f is Farm => f !== undefined);

  return {
    teams,
    unassignedFarms,
    selectedFarmCount: selectedFarmIds.length,
    teamCount,
    totalDurationMinutes: data.totalEstimatedDuration,
  };
}

export async function routeAssignment(
  request: RouteAssignmentRequest,
): Promise<{ result: DispatchResult; dispatchRunId: string }> {
  const farmMap = new Map(request.farms.map((f) => [f.id, f]));

  const response = await fetch(`${API_BASE_URL}/api/route-assignment`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      teamCount: request.teamCount,
      farmIds: request.farmIds,
      farms: request.farms.map(normalizeFarmDuration),
      depotName: request.depotName,
      depotLat: request.depotLat,
      depotLng: request.depotLng,
      maxRouteMinutes: request.maxRouteMinutes,
      disinfectServiceMinutes: request.disinfectServiceMinutes,
      allowUnassigned: request.allowUnassigned,
    }),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Route assignment failed (${response.status}): ${detail}`);
  }

  const data = (await response.json()) as RouteAssignmentResponse;
  const result = mapToDispatchResult(data, farmMap, request.teamCount, request.farmIds);
  return { result, dispatchRunId: data.dispatchRunId };
}
