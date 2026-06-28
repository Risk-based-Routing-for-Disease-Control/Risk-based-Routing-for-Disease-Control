import type { Farm } from '../types/farm';

export const DEFAULT_FARM_SERVICE_MINUTES = 15;
export const FARM_SERVICE_MINUTES_PER_LIVESTOCK = 0.0007;

export function calculateFarmServiceMinutes(livestockCount: number | null | undefined): number {
  const count = Math.max(0, livestockCount ?? 0);
  return Math.ceil(DEFAULT_FARM_SERVICE_MINUTES + count * FARM_SERVICE_MINUTES_PER_LIVESTOCK);
}

export function normalizeFarmDuration(farm: Farm): Farm {
  return {
    ...farm,
    estimatedDurationMinutes: calculateFarmServiceMinutes(farm.livestockCount),
  };
}
