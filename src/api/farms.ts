import type { Farm, RiskLevel, XaiFactor } from '../types/farm';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? '';

interface ApiFarm {
  id: string;
  farmCode?: string;
  name: string;
  lat: number;
  lng: number;
  riskScore: number;
  riskScoreId?: number;
  riskLevel: string;
  riskDate?: string;
  livestockType?: string;
  livestockCount?: number;
  livestockUnit?: string;
  estimatedDurationMinutes?: number;
  address?: string;
  xaiFactors?: XaiFactor[];
}

function toRiskLevel(raw: string): RiskLevel {
  const map: Record<string, RiskLevel> = {
    HIGH: 'critical', MEDIUM: 'high', LOW: 'warning',
    critical: 'critical', high: 'high', warning: 'warning',
  };
  return map[raw] ?? 'warning';
}

function toFarm(api: ApiFarm): Farm {
  return {
    id: api.id,
    code: api.farmCode ?? api.id,
    name: api.name,
    lat: api.lat,
    lng: api.lng,
    riskScore: api.riskScore > 1 ? api.riskScore / 100 : api.riskScore,
    riskLevel: toRiskLevel(api.riskLevel),
    livestockType: api.livestockType ?? '미상',
    livestockCount: api.livestockCount ?? 0,
    livestockUnit: api.livestockUnit ?? '두',
    estimatedDurationMinutes: api.estimatedDurationMinutes ?? 30,
    address: api.address ?? '',
    xaiFactors: api.xaiFactors ?? [],
    lastUpdatedAt: api.riskDate ?? '',
  };
}

export interface FetchFarmsResult {
  farms: Farm[];
  source: 'db' | 'dummy';
  error: string | null;
}

interface FarmsListResponse {
  farms: ApiFarm[];
  source: 'db' | 'dummy';
  error: string | null;
}

export async function fetchFarms(): Promise<FetchFarmsResult> {
  const response = await fetch(`${API_BASE_URL}/api/farms`);
  if (!response.ok) throw new Error(`farms fetch failed: ${response.status}`);
  const data = (await response.json()) as FarmsListResponse;
  return { farms: data.farms.map(toFarm), source: data.source, error: data.error };
}
