import { useEffect, useRef } from 'react';
import { Box, CircularProgress, Paper, Typography } from '@mui/material';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import { useNaverMapsScript } from '../../hooks/useNaverMapsScript';
import { MapControls } from '../map/MapControls';
import { RouteLegend } from './RouteLegend';
import { createTooltipContent } from '../../utils/mapTooltip';
import { flattenRoutePath, type MultiStopRouteResult } from '../../api/directions';
import type { DispatchStop, DispatchTeam } from '../../types/dispatch';
import { DEFAULT_MAP_CENTER, DEFAULT_MAP_ZOOM } from '../../constants/map';

const NAVER_CLIENT_ID = import.meta.env.VITE_NAVER_MAP_CLIENT_ID as string | undefined;
const EMPTY_FAILED: Set<string> = new Set();
const ROUTE_DEFAULT_STYLE = { strokeWeight: 3, strokeOpacity: 0.85, zIndex: 10 };
const ROUTE_DIMMED_STYLE = { strokeWeight: 2, strokeOpacity: 0.45, zIndex: 5 };
const ROUTE_HIGHLIGHT_STYLE = { strokeWeight: 7, strokeOpacity: 1, zIndex: 30 };
const ROUTE_HIT_STYLE = { strokeWeight: 20, strokeOpacity: 0.001, zIndex: 40 };

function createStopIcon(stop: DispatchStop, color: string) {
  const size = 26;
  const isCompleted = stop.status === 'completed';
  const fill = isCompleted ? '#9E9E9E' : color;
  const inner = isCompleted
    ? '<path d="M7 13.2l3.4 3.4L19.2 7.4" stroke="#ffffff" stroke-width="2.4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    : `<text x="13" y="17" text-anchor="middle" font-size="12" font-weight="700" fill="#ffffff" font-family="sans-serif">${stop.order}</text>`;
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 26 26"><circle cx="13" cy="13" r="11" fill="${fill}" stroke="#ffffff" stroke-width="2.5"/>${inner}</svg>`;

  return {
    content: svg,
    size: new window.naver.maps.Size(size, size),
    anchor: new window.naver.maps.Point(size / 2, size / 2),
  };
}

function createDisinfectionIcon(color: string) {
  const size = 22;
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 22 22"><rect x="3" y="3" width="16" height="16" rx="3" fill="#ffffff" stroke="${color}" stroke-width="2.4"/><path d="M11 6.4v9.2M6.4 11h9.2" stroke="${color}" stroke-width="2.2" stroke-linecap="round"/></svg>`;

  return {
    content: svg,
    size: new window.naver.maps.Size(size, size),
    anchor: new window.naver.maps.Point(size / 2, size / 2),
  };
}

interface RouteMapProps {
  teams: DispatchTeam[];
  /** Real driving routes fetched by the caller (e.g. via useTeamRoutes), keyed by team id. */
  routesByTeamId?: Record<string, MultiStopRouteResult>;
  isLoadingRoutes?: boolean;
  failedTeamIds?: Set<string>;
}

export function RouteMap({
  teams,
  routesByTeamId,
  isLoadingRoutes = false,
  failedTeamIds = EMPTY_FAILED,
}: RouteMapProps) {
  const mapElRef = useRef<HTMLDivElement | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- untyped Naver Maps SDK
  const mapRef = useRef<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- untyped Naver Maps SDK
  const overlaysRef = useRef<any[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- untyped Naver Maps SDK
  const tooltipRef = useRef<any>(null);
  const loaded = useNaverMapsScript(NAVER_CLIENT_ID);

  useEffect(() => {
    if (!loaded || !mapElRef.current || mapRef.current) return;
    const { naver } = window;
    mapRef.current = new naver.maps.Map(mapElRef.current, {
      center: new naver.maps.LatLng(DEFAULT_MAP_CENTER.lat, DEFAULT_MAP_CENTER.lng),
      zoom: DEFAULT_MAP_ZOOM,
      zoomControl: false,
    });
    tooltipRef.current = new naver.maps.InfoWindow({
      content: '',
      borderWidth: 0,
      backgroundColor: 'transparent',
      disableAnchor: true,
      pixelOffset: new naver.maps.Point(0, -16),
    });
  }, [loaded]);

  useEffect(() => {
    if (!loaded || !mapRef.current) return;
    const { naver } = window;
    const map = mapRef.current;

    overlaysRef.current.forEach((overlay) => overlay.setMap(null));
    overlaysRef.current = [];
    const teamRouteOverlays: Array<{
      teamId: string;
      // eslint-disable-next-line @typescript-eslint/no-explicit-any -- untyped Naver Maps SDK
      polyline: any;
      // eslint-disable-next-line @typescript-eslint/no-explicit-any -- untyped Naver Maps SDK
      hitPolyline: any;
      markers: Array<{
        // eslint-disable-next-line @typescript-eslint/no-explicit-any -- untyped Naver Maps SDK
        marker: any;
        zIndex: number;
      }>;
    }> = [];

    const focusTeamRoute = (focusedTeamId: string | null) => {
      teamRouteOverlays.forEach(({ teamId, polyline, hitPolyline, markers }) => {
        const isFocused = focusedTeamId === teamId;
        const style = focusedTeamId === null ? ROUTE_DEFAULT_STYLE : isFocused ? ROUTE_HIGHLIGHT_STYLE : ROUTE_DIMMED_STYLE;
        polyline.setOptions(style);
        hitPolyline.setOptions({ zIndex: isFocused ? 60 : ROUTE_HIT_STYLE.zIndex });
        markers.forEach(({ marker, zIndex }) => {
          marker.setOptions({ zIndex: focusedTeamId === null ? zIndex : isFocused ? 220 : 60 });
        });
      });
    };

    teams.forEach((team) => {
      if (team.stops.length === 0) return;
      const depot = team.depot ?? { name: '공통 방역 출발지', ...DEFAULT_MAP_CENTER };

      const route = routesByTeamId?.[team.id];
      const stopPoints = team.stops.flatMap((stop) => [
        { lat: stop.farm.lat, lng: stop.farm.lng },
        ...(stop.disinfectionHub ? [{ lat: stop.disinfectionHub.lat, lng: stop.disinfectionHub.lng }] : []),
      ]);
      const pathPoints = route
        ? flattenRoutePath(route)
        : [
            { lat: depot.lat, lng: depot.lng },
            ...stopPoints,
            { lat: depot.lat, lng: depot.lng },
          ];
      const path = pathPoints.map((point) => new naver.maps.LatLng(point.lat, point.lng));

      const polyline = new naver.maps.Polyline({
        map,
        path,
        clickable: true,
        strokeColor: team.color,
        ...ROUTE_DEFAULT_STYLE,
      });
      overlaysRef.current.push(polyline);

      const hitPolyline = new naver.maps.Polyline({
        map,
        path,
        clickable: true,
        strokeColor: '#000000',
        ...ROUTE_HIT_STYLE,
      });
      overlaysRef.current.push(hitPolyline);

      const depotMarker = new naver.maps.Marker({
        position: new naver.maps.LatLng(depot.lat, depot.lng),
        map,
        title: depot.name,
        zIndex: 150,
      });
      overlaysRef.current.push(depotMarker);
      const teamMarkers = [{ marker: depotMarker, zIndex: 150 }];

      const bindTeamRouteHover = (overlay: unknown) => {
        naver.maps.Event.addListener(overlay, 'mouseover', () => focusTeamRoute(team.id));
        naver.maps.Event.addListener(overlay, 'mouseout', () => focusTeamRoute(null));
      };
      bindTeamRouteHover(polyline);
      bindTeamRouteHover(hitPolyline);

      team.stops.forEach((stop) => {
        const marker = new naver.maps.Marker({
          position: new naver.maps.LatLng(stop.farm.lat, stop.farm.lng),
          map,
          icon: createStopIcon(stop, team.color),
          title: stop.farm.name,
          zIndex: 100,
        });
        naver.maps.Event.addListener(marker, 'mouseover', () => {
          focusTeamRoute(team.id);
          const tooltip = tooltipRef.current;
          if (!tooltip) return;
          tooltip.setContent(createTooltipContent(stop.farm.name));
          tooltip.open(map, marker);
        });
        naver.maps.Event.addListener(marker, 'mouseout', () => {
          focusTeamRoute(null);
          tooltipRef.current?.close();
        });
        overlaysRef.current.push(marker);
        teamMarkers.push({ marker, zIndex: 100 });

        if (stop.disinfectionHub) {
          const hub = stop.disinfectionHub;
          const hubMarker = new naver.maps.Marker({
            position: new naver.maps.LatLng(hub.lat, hub.lng),
            map,
            icon: createDisinfectionIcon(team.color),
            title: hub.name,
            zIndex: 90,
          });
          naver.maps.Event.addListener(hubMarker, 'mouseover', () => {
            focusTeamRoute(team.id);
            const tooltip = tooltipRef.current;
            if (!tooltip) return;
            tooltip.setContent(createTooltipContent(hub.name));
            tooltip.open(map, hubMarker);
          });
          naver.maps.Event.addListener(hubMarker, 'mouseout', () => {
            focusTeamRoute(null);
            tooltipRef.current?.close();
          });
          overlaysRef.current.push(hubMarker);
          teamMarkers.push({ marker: hubMarker, zIndex: 90 });
        }
      });
      teamRouteOverlays.push({ teamId: team.id, polyline, hitPolyline, markers: teamMarkers });
    });
  }, [loaded, teams, routesByTeamId]);

  const handleZoomIn = () => {
    const map = mapRef.current;
    if (!map) return;
    map.setZoom(map.getZoom() + 1, true);
  };

  const handleZoomOut = () => {
    const map = mapRef.current;
    if (!map) return;
    map.setZoom(map.getZoom() - 1, true);
  };

  const handleLocate = () => {
    const map = mapRef.current;
    if (!map || !window.naver) return;
    map.panTo(new window.naver.maps.LatLng(DEFAULT_MAP_CENTER.lat, DEFAULT_MAP_CENTER.lng));
  };

  if (!NAVER_CLIENT_ID) {
    return (
      <Box sx={fillCenterStyle}>
        <Typography color="text.secondary" align="center" sx={{ px: 3 }}>
          네이버 지도 API 키가 설정되지 않았습니다.
          <br />
          .env 파일에 VITE_NAVER_MAP_CLIENT_ID를 설정해주세요.
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ position: 'relative', width: '100%', height: '100%' }}>
      <Box ref={mapElRef} sx={{ width: '100%', height: '100%' }} />
      {!loaded && (
        <Box sx={fillCenterStyle}>
          <CircularProgress size={28} />
        </Box>
      )}
      {loaded && isLoadingRoutes && (
        <Box sx={{ ...fillCenterStyle, bgcolor: 'rgba(255, 255, 255, 0.75)', flexDirection: 'column', gap: 1.5 }}>
          <CircularProgress size={28} />
          <Typography variant="body2" color="text.secondary">
            실제 도로 경로를 불러오는 중...
          </Typography>
        </Box>
      )}
      {!isLoadingRoutes && failedTeamIds.size > 0 && (
        <Paper
          elevation={2}
          sx={{
            position: 'absolute',
            top: 16,
            left: '50%',
            transform: 'translateX(-50%)',
            display: 'flex',
            alignItems: 'center',
            gap: 0.75,
            px: 1.5,
            py: 0.75,
            borderRadius: 1.5,
            bgcolor: '#FFF8E6',
          }}
        >
          <WarningAmberIcon fontSize="small" sx={{ color: '#B26A00' }} />
          <Typography variant="caption" sx={{ color: '#8A5800' }}>
            일부 경로의 실제 도로 안내를 불러오지 못해 직선 경로로 표시 중입니다.
          </Typography>
        </Paper>
      )}
      <MapControls onZoomIn={handleZoomIn} onZoomOut={handleZoomOut} onLocate={handleLocate} />
      <RouteLegend teams={teams} />
    </Box>
  );
}

const fillCenterStyle = {
  position: 'absolute',
  inset: 0,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  bgcolor: 'grey.100',
} as const;
