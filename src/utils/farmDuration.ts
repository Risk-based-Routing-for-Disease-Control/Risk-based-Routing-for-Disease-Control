import type { Farm } from '../types/farm';

export const DEFAULT_FARM_SERVICE_MINUTES = 90;
export const MIN_FARM_SERVICE_MINUTES = 60;
export const BASE_LIVESTOCK_COUNT = 10_000;
export const BASE_FARM_SERVICE_MINUTES = 90;
export const ADDITIONAL_MINUTES_PER_10K_LIVESTOCK = 35;
export const SERVICE_ROUNDING_MINUTES = 10;

function roundUpMinutes(value: number, unit = SERVICE_ROUNDING_MINUTES): number {
  return Math.ceil((value - Number.EPSILON) / unit) * unit;
}

export function calculateFarmServiceMinutes(livestockCount: number | null | undefined): number {
  const count = Math.max(0, livestockCount ?? 0);
  if (count <= 0) return DEFAULT_FARM_SERVICE_MINUTES;

  if (count <= BASE_LIVESTOCK_COUNT) {
    const scaled =
      MIN_FARM_SERVICE_MINUTES +
      (count / BASE_LIVESTOCK_COUNT) * (BASE_FARM_SERVICE_MINUTES - MIN_FARM_SERVICE_MINUTES);
    return roundUpMinutes(scaled);
  }

  const extraUnits = Math.ceil((count - BASE_LIVESTOCK_COUNT) / BASE_LIVESTOCK_COUNT);
  return BASE_FARM_SERVICE_MINUTES + extraUnits * ADDITIONAL_MINUTES_PER_10K_LIVESTOCK;
}

export function normalizeFarmDuration(farm: Farm): Farm {
  return {
    ...farm,
    estimatedDurationMinutes: calculateFarmServiceMinutes(farm.livestockCount),
  };
}
