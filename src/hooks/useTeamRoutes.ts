import { useEffect, useRef, useState } from 'react';
import { fetchMultiStopRoute, type MultiStopRouteResult } from '../api/directions';
import type { DispatchTeam } from '../types/dispatch';

interface UseTeamRoutesResult {
  routesByTeamId: Record<string, MultiStopRouteResult>;
  isLoading: boolean;
  failedTeamIds: Set<string>;
}

const EMPTY_ROUTES: Record<string, MultiStopRouteResult> = {};
const EMPTY_FAILED: Set<string> = new Set();

export function useTeamRoutes(teams: DispatchTeam[], enabled: boolean): UseTeamRoutesResult {
  const fetchedSignatureRef = useRef<string | null>(null);
  const [routesByTeamId, setRoutesByTeamId] = useState<Record<string, MultiStopRouteResult>>(EMPTY_ROUTES);
  const [isLoading, setIsLoading] = useState(false);
  const [failedTeamIds, setFailedTeamIds] = useState<Set<string>>(EMPTY_FAILED);

  const signature = teams
    .map((team) => `${team.id}:${team.stops.map((stop) => `${stop.farm.lat},${stop.farm.lng}`).join('>')}`)
    .join('|');

  useEffect(() => {
    if (!enabled) return;
    if (fetchedSignatureRef.current === signature) return;
    let cancelled = false;
    setIsLoading(true);

    (async () => {
      const results = await Promise.all(
        teams.map(async (team) => {
          if (team.stops.length < 2) return { teamId: team.id, route: null, failed: false };
          try {
            const route = await fetchMultiStopRoute(
              team.stops.map((stop) => ({ lat: stop.farm.lat, lng: stop.farm.lng, name: stop.farm.name })),
            );
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
