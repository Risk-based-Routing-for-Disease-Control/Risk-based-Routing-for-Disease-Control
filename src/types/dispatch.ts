import type { Farm } from './farm';

export type StopStatus = 'plain' | 'completed' | 'upcoming';

export interface DispatchStop {
  farm: Farm;
  order: number;
  status: StopStatus;
  completedAt?: string;
}

export interface DispatchTeam {
  id: string;
  label: string;
  color: string;
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
