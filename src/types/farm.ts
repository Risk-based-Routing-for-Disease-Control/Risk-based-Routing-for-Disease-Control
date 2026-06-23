export type RiskLevel = 'critical' | 'high' | 'warning';

export interface XaiFactor {
  id: string;
  label: string;
  icon: 'bird' | 'truck';
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
