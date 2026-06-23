import { durationLabel } from './time';

export function formatDistance(meters: number): string {
  if (meters < 1000) return `${Math.round(meters)}m`;
  return `${(meters / 1000).toFixed(1)}km`;
}

/** `get_route` (backend) returns duration in milliseconds. */
export function formatDurationFromMs(ms: number): string {
  return durationLabel(Math.max(1, Math.round(ms / 60000)));
}
