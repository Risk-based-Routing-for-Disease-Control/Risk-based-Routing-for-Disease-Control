const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://localhost:8000';

export interface LatLngPoint {
  lat: number;
  lng: number;
}

export interface RoutePointInput {
  lat: number;
  lng: number;
  name?: string;
}

export interface RouteLegResult {
  from: RoutePointInput;
  to: RoutePointInput;
  distance: number;
  duration: number;
  path: LatLngPoint[];
}

export interface MultiStopRouteResult {
  totalDistance: number;
  totalDuration: number;
  legs: RouteLegResult[];
}

/**
 * Fetches a leg-by-leg driving route for an ordered list of stops via the backend's
 * Naver Directions 5 proxy. The backend chains adjacent legs server-side, so there is
 * no waypoint-count limit to worry about on the frontend.
 */
export async function fetchMultiStopRoute(points: RoutePointInput[]): Promise<MultiStopRouteResult> {
  const response = await fetch(`${API_BASE_URL}/api/directions/multi`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ points }),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Multi-stop directions request failed (${response.status}): ${detail}`);
  }

  return (await response.json()) as MultiStopRouteResult;
}

/** Stitches a route's per-leg paths into one continuous polyline path. */
export function flattenRoutePath(route: MultiStopRouteResult): LatLngPoint[] {
  return route.legs.reduce<LatLngPoint[]>((path, leg, index) => {
    if (index === 0) return [...leg.path];
    return [...path, ...leg.path.slice(1)];
  }, []);
}
