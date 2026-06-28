import { useEffect, useRef, useState } from 'react';
import { fetchMultiStopRoute, type MultiStopRouteResult } from '../api/directions';
import type { DispatchTeam } from '../types/dispatch';
import { DEFAULT_MAP_CENTER } from '../constants/map';

interface UseTeamRoutesResult {
  routesByTeamId: Record<string, MultiStopRouteResult>;
  isLoading: boolean;
  failedTeamIds: Set<string>;
}

const EMPTY_ROUTES: Record<string, MultiStopRouteResult> = {};
const EMPTY_FAILED: Set<string> = new Set();

function routePointsForTeam(team: DispatchTeam) {
  const depot = team.depot ?? { name: '공통 방역 출발지', ...DEFAULT_MAP_CENTER };
  const stopPoints = team.stops.flatMap((stop) => [
    { lat: stop.farm.lat, lng: stop.farm.lng, name: stop.farm.name },
    ...(stop.disinfectionHub
      ? [{ lat: stop.disinfectionHub.lat, lng: stop.disinfectionHub.lng, name: stop.disinfectionHub.name }]
      : []),
  ]);

  return [
    { lat: depot.lat, lng: depot.lng, name: depot.name },
    ...stopPoints,
    { lat: depot.lat, lng: depot.lng, name: depot.name },
  ];
}

export function useTeamRoutes(teams: DispatchTeam[], enabled: boolean): UseTeamRoutesResult {
  const fetchedSignatureRef = useRef<string | null>(null);
  const [routesByTeamId, setRoutesByTeamId] = useState<Record<string, MultiStopRouteResult>>(EMPTY_ROUTES);
  const [isLoading, setIsLoading] = useState(false);
  const [failedTeamIds, setFailedTeamIds] = useState<Set<string>>(EMPTY_FAILED);

  const signature = teams
    .map((team) => `${team.id}:${routePointsForTeam(team).map((point) => `${point.lat},${point.lng}`).join('>')}`)
    .join('|');

  useEffect(() => {
    if (!enabled) return;
    if (fetchedSignatureRef.current === signature) return;
    let cancelled = false;
    setIsLoading(true);

    (async () => {
      const results = await Promise.all(
        teams.map(async (team) => {
          if (team.stops.length < 1) return { teamId: team.id, route: null, failed: false };
          try {
            const route = await fetchMultiStopRoute(routePointsForTeam(team));
            return { teamId: team.id, route, failed: false };
          } catch (error) {
            console.error(`[useTeamRoutes] failed to fetch route for ${team.id}`, error);
            return { teamId: team.id, route: null, failed: true };
          }
        }),
      );

      // StrictMode mounts effects twice in dev; only commit once a run actually
      // finishes, otherwise the first pass's cleanup would mark the signature as
      // "fetched" while the real (second) pass bails out and nothing ever loads.
      if (cancelled) return;
      fetchedSignatureRef.current = signature;

      setRoutesByTeamId((prev) => {
        const next = { ...prev };
        results.forEach((result) => {
          if (result.route) next[result.teamId] = result.route;
        });
        return next;
      });
      setFailedTeamIds(new Set(results.filter((result) => result.failed).map((result) => result.teamId)));
      setIsLoading(false);
    })();

    return () => {
      cancelled = true;
    };
  }, [signature, enabled, teams]);

  return { routesByTeamId, isLoading, failedTeamIds };
}
