export type RiskLevel = 'critical' | 'high' | 'warning';

export interface XaiFactor {
  id: string;
  factorCode?: string;
  label: string;
  icon: string;
  weight?: number | null;
}

export interface Farm {
  id: string;
  code: string;
  name: string;
  lat: number;
  lng: number;
  riskScore: number;
  riskLevel: RiskLevel;
  livestockType: string;
  livestockCount: number;
  livestockUnit: string;
  estimatedDurationMinutes: number;
  address: string;
  xaiFactors: XaiFactor[];
  lastUpdatedAt: string;
}
