import type { Farm } from './farm';

export type StopStatus = 'upcoming' | 'completed' | 'cancelled';

export interface DispatchDisinfectionHub {
  id: string;
  name: string;
  lat: number;
  lng: number;
}

export interface DispatchStop {
  farm: Farm;
  disinfectionHub?: DispatchDisinfectionHub;
  order: number;
  status: StopStatus;
  completedAt?: string;
  cancelledAt?: string;
  actualDurationMinutes?: number;
}

export interface DispatchDepot {
  name: string;
  lat: number;
  lng: number;
}

export interface DispatchTeam {
  id: string;
  label: string;
  color: string;
  depot?: DispatchDepot;
  stops: DispatchStop[];
  totalDurationMinutes: number;
}

export interface DispatchResult {
  teams: DispatchTeam[];
  unassignedFarms: Farm[];
  selectedFarmCount: number;
  teamCount: number;
  totalDurationMinutes: number;
}
