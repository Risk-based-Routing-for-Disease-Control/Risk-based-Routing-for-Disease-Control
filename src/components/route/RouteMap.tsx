import { useEffect, useRef } from 'react';
import { Box, CircularProgress, Paper, Typography } from '@mui/material';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import { useNaverMapsScript } from '../../hooks/useNaverMapsScript';
import { MapControls } from '../map/MapControls';
import { RouteLegend } from './RouteLegend';
import { createTooltipContent } from '../../utils/mapTooltip';
import { flattenRoutePath, type MultiStopRouteResult } from '../../api/directions';
import type { DispatchStop, DispatchTeam } from '../../types/dispatch';

const NAVER_CLIENT_ID = import.meta.env.VITE_NAVER_MAP_CLIENT_ID as string | undefined;
const DEFAULT_CENTER = { lat: 37.55, lng: 127.05 };
const DEFAULT_ZOOM = 10;
const EMPTY_FAILED: Set<string> = new Set();

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
      center: new naver.maps.LatLng(DEFAULT_CENTER.lat, DEFAULT_CENTER.lng),
      zoom: DEFAULT_ZOOM,
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

    teams.forEach((team) => {
      if (team.stops.length === 0) return;

      const route = routesByTeamId?.[team.id];
      const pathPoints = route
        ? flattenRoutePath(route)
        : team.stops.map((stop) => ({ lat: stop.farm.lat, lng: stop.farm.lng }));
      const path = pathPoints.map((point) => new naver.maps.LatLng(point.lat, point.lng));

      const polyline = new naver.maps.Polyline({
        map,
        path,
        strokeColor: team.color,
        strokeWeight: 3,
        strokeOpacity: 0.85,
      });
      overlaysRef.current.push(polyline);

      team.stops.forEach((stop) => {
        const marker = new naver.maps.Marker({
          position: new naver.maps.LatLng(stop.farm.lat, stop.farm.lng),
          map,
          icon: createStopIcon(stop, team.color),
          title: stop.farm.name,
          zIndex: 100,
        });
        naver.maps.Event.addListener(marker, 'mouseover', () => {
          const tooltip = tooltipRef.current;
          if (!tooltip) return;
          tooltip.setContent(createTooltipContent(stop.farm.name));
          tooltip.open(map, marker);
        });
        naver.maps.Event.addListener(marker, 'mouseout', () => {
          tooltipRef.current?.close();
        });
        overlaysRef.current.push(marker);
      });
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
    map.panTo(new window.naver.maps.LatLng(DEFAULT_CENTER.lat, DEFAULT_CENTER.lng));
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
