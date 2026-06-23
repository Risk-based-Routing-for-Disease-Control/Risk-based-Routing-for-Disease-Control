import { useEffect, useRef } from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';
import { useNaverMapsScript } from '../../hooks/useNaverMapsScript';
import { useFarmStore } from '../../store/useFarmStore';
import { RISK_LEVEL_COLOR } from '../../constants/risk';
import type { Farm } from '../../types/farm';
import { MapLegend } from './MapLegend';
import { MapControls } from './MapControls';
import { createTooltipContent } from '../../utils/mapTooltip';

const NAVER_CLIENT_ID = import.meta.env.VITE_NAVER_MAP_CLIENT_ID as string | undefined;
const DEFAULT_CENTER = { lat: 37.55, lng: 127.05 };
const DEFAULT_ZOOM = 10;

function createMarkerIcon(farm: Farm, isSelected: boolean) {
  const color = RISK_LEVEL_COLOR[farm.riskLevel];
  const size = isSelected ? 26 : 16;
  const circle = isSelected
    ? `<circle cx="13" cy="13" r="10" fill="${color}" stroke="#ffffff" stroke-width="3"/>`
    : `<circle cx="8" cy="8" r="6.5" fill="${color}" stroke="#ffffff" stroke-width="2"/>`;
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">${circle}</svg>`;

  return {
    content: svg,
    size: new window.naver.maps.Size(size, size),
    anchor: new window.naver.maps.Point(size / 2, size / 2),
  };
}

export function NaverMap() {
  const mapElRef = useRef<HTMLDivElement | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- untyped Naver Maps SDK
  const mapRef = useRef<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- untyped Naver Maps SDK
  const markersRef = useRef<globalThis.Map<string, any>>(new globalThis.Map());
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- untyped Naver Maps SDK
  const tooltipRef = useRef<any>(null);
  const loaded = useNaverMapsScript(NAVER_CLIENT_ID);

  const farms = useFarmStore((s) => s.farms);
  const selectedFarmId = useFarmStore((s) => s.selectedFarmId);
  const selectFarm = useFarmStore((s) => s.selectFarm);

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

    markersRef.current.forEach((marker) => marker.setMap(null));
    markersRef.current.clear();

    farms.forEach((farm) => {
      const isSelected = farm.id === selectedFarmId;
      const marker = new naver.maps.Marker({
        position: new naver.maps.LatLng(farm.lat, farm.lng),
        map,
        icon: createMarkerIcon(farm, isSelected),
        title: farm.name,
        zIndex: isSelected ? 200 : 100,
      });
      naver.maps.Event.addListener(marker, 'click', () => selectFarm(farm.id));
      naver.maps.Event.addListener(marker, 'mouseover', () => {
        const tooltip = tooltipRef.current;
        if (!tooltip) return;
        tooltip.setContent(createTooltipContent(farm.name));
        tooltip.open(map, marker);
      });
      naver.maps.Event.addListener(marker, 'mouseout', () => {
        tooltipRef.current?.close();
      });
      markersRef.current.set(farm.id, marker);
    });
  }, [loaded, farms, selectedFarmId, selectFarm]);

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
      <MapControls onZoomIn={handleZoomIn} onZoomOut={handleZoomOut} onLocate={handleLocate} />
      <MapLegend />
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
