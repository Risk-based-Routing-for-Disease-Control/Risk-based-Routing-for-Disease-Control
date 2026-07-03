import { useEffect, useRef } from 'react';
import { Box, Button, CircularProgress, Paper, Typography } from '@mui/material';
import { useNaverMapsScript } from '../../hooks/useNaverMapsScript';
import { useFarmStore } from '../../store/useFarmStore';
import { useDispatchStore } from '../../store/useDispatchStore';
import { useFacilitiesStore } from '../../store/useFacilitiesStore';
import { useEmergencyModeStore } from '../../store/useEmergencyModeStore';
import { RISK_LEVEL_COLOR } from '../../constants/risk';
import type { Farm } from '../../types/farm';
import { MapLegend } from './MapLegend';
import { MapControls } from './MapControls';
import { createTooltipContent } from '../../utils/mapTooltip';
import { DEFAULT_MAP_CENTER, DEFAULT_MAP_ZOOM } from '../../constants/map';

const NAVER_CLIENT_ID = import.meta.env.VITE_NAVER_MAP_CLIENT_ID as string | undefined;
const EMERGENCY_RADII_METERS = [3000, 7000, 11000];
const EMERGENCY_RADIUS_STYLES = [
  { strokeColor: '#E53935', fillColor: '#E53935', fillOpacity: 0.08 },
  { strokeColor: '#FB8C00', fillColor: '#FB8C00', fillOpacity: 0.05 },
  { strokeColor: '#FDD835', fillColor: '#FDD835', fillOpacity: 0.03 },
];

function createFacilityMarkerIcon() {
  const size = 24;
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 24 24"><rect x="2" y="2" width="20" height="20" rx="4" fill="#1565C0" stroke="#ffffff" stroke-width="2"/><path d="M12 7v10M7 12h10" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round"/></svg>`;
  return {
    content: svg,
    size: new window.naver.maps.Size(size, size),
    anchor: new window.naver.maps.Point(12, 12),
  };
}

function createMarkerIcon(farm: Farm, isFocused: boolean, isSelectedForDispatch: boolean) {
  const color = RISK_LEVEL_COLOR[farm.riskLevel];
  const size = isFocused ? 30 : isSelectedForDispatch ? 24 : 16;
  const center = size / 2;
  const radius = isFocused ? 10 : isSelectedForDispatch ? 8 : 6.5;
  const selectionRing = isSelectedForDispatch
    ? `<circle cx="${center}" cy="${center}" r="${radius + 3}" fill="none" stroke="#0B63E5" stroke-width="3"/>`
    : '';
  const circle = `<circle cx="${center}" cy="${center}" r="${radius}" fill="${color}" stroke="#ffffff" stroke-width="${isFocused ? 3 : 2}"/>`;
  const check = isSelectedForDispatch
    ? `<path d="M${center - 4.5} ${center + 0.2}l3 3 6 -7" stroke="#ffffff" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`
    : '';
  const content = `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">${selectionRing}${circle}${check}</svg>`;

  return {
    content,
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
  const facilityMarkersRef = useRef<any[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- untyped Naver Maps SDK
  const emergencyCirclesRef = useRef<any[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- untyped Naver Maps SDK
  const tooltipRef = useRef<any>(null);
  const loaded = useNaverMapsScript(NAVER_CLIENT_ID);

  const farms = useFarmStore((s) => s.farms);
  const selectedFarmId = useFarmStore((s) => s.selectedFarmId);
  const selectFarm = useFarmStore((s) => s.selectFarm);
  const selectedFarmIds = useDispatchStore((s) => s.selectedFarmIds);
  const toggleFarm = useDispatchStore((s) => s.toggleFarm);
  const facilities = useFacilitiesStore((s) => s.facilities);
  const loadFacilities = useFacilitiesStore((s) => s.loadFacilities);
  const emergencyActive = useEmergencyModeStore((s) => s.isActive);
  const emergencyCenter = useEmergencyModeStore((s) => s.center);
  const emergencyLabel = useEmergencyModeStore((s) => s.label);
  const emergencyAwaitingPick = useEmergencyModeStore((s) => s.awaitingPick);
  const exitEmergencyMode = useEmergencyModeStore((s) => s.exit);

  useEffect(() => {
    loadFacilities();
  }, [loadFacilities]);

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
    naver.maps.Event.addListener(mapRef.current, 'click', (e: { coord: { lat: () => number; lng: () => number } }) => {
      if (!useEmergencyModeStore.getState().awaitingPick) return;
      useEmergencyModeStore.getState().setCenter({ lat: e.coord.lat(), lng: e.coord.lng() });
    });
  }, [loaded]);

  useEffect(() => {
    if (!loaded || !mapRef.current) return;
    const { naver } = window;
    const map = mapRef.current;

    markersRef.current.forEach((marker) => marker.setMap(null));
    markersRef.current.clear();

    farms.forEach((farm) => {
      const isFocused = farm.id === selectedFarmId;
      const isSelectedForDispatch = selectedFarmIds.includes(farm.id);
      const marker = new naver.maps.Marker({
        position: new naver.maps.LatLng(farm.lat, farm.lng),
        map,
        icon: createMarkerIcon(farm, isFocused, isSelectedForDispatch),
        title: farm.name,
        zIndex: isFocused ? 220 : isSelectedForDispatch ? 180 : 100,
      });
      naver.maps.Event.addListener(marker, 'click', () => {
        if (useEmergencyModeStore.getState().awaitingPick) {
          useEmergencyModeStore.getState().setCenter({ lat: farm.lat, lng: farm.lng });
          return;
        }
        selectFarm(farm.id);
        toggleFarm(farm.id);
      });
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
  }, [loaded, farms, selectedFarmId, selectedFarmIds, selectFarm, toggleFarm]);

  useEffect(() => {
    if (!loaded || !mapRef.current) return;
    const { naver } = window;
    const map = mapRef.current;

    facilityMarkersRef.current.forEach((marker) => marker.setMap(null));
    facilityMarkersRef.current = [];

    facilities.forEach((facility) => {
      const marker = new naver.maps.Marker({
        position: new naver.maps.LatLng(facility.lat, facility.lng),
        map,
        icon: createFacilityMarkerIcon(),
        title: facility.name,
        zIndex: 80,
      });
      naver.maps.Event.addListener(marker, 'mouseover', () => {
        const tooltip = tooltipRef.current;
        if (!tooltip) return;
        tooltip.setContent(createTooltipContent(facility.name));
        tooltip.open(map, marker);
      });
      naver.maps.Event.addListener(marker, 'mouseout', () => {
        tooltipRef.current?.close();
      });
      facilityMarkersRef.current.push(marker);
    });
  }, [loaded, facilities]);

  useEffect(() => {
    if (!loaded || !mapRef.current) return;
    const { naver } = window;
    const map = mapRef.current;

    emergencyCirclesRef.current.forEach((circle) => circle.setMap(null));
    emergencyCirclesRef.current = [];

    if (!emergencyActive || !emergencyCenter) return;

    const center = new naver.maps.LatLng(emergencyCenter.lat, emergencyCenter.lng);
    let outerCircle = null;
    // 바깥쪽부터 그려서 안쪽 원이 위에 오도록
    for (let i = EMERGENCY_RADII_METERS.length - 1; i >= 0; i -= 1) {
      const circle = new naver.maps.Circle({
        map,
        center,
        radius: EMERGENCY_RADII_METERS[i],
        strokeWeight: 2,
        strokeOpacity: 0.9,
        ...EMERGENCY_RADIUS_STYLES[i],
      });
      emergencyCirclesRef.current.push(circle);
      if (i === EMERGENCY_RADII_METERS.length - 1) outerCircle = circle;
    }

    if (outerCircle) {
      map.fitBounds(outerCircle.getBounds());
    }
  }, [loaded, emergencyActive, emergencyCenter]);

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
      {emergencyActive && (
        <Paper
          elevation={2}
          sx={{
            position: 'absolute',
            top: 16,
            left: '50%',
            transform: 'translateX(-50%)',
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            px: 1.5,
            py: 0.75,
            borderRadius: 1.5,
            bgcolor: '#FDECEA',
            maxWidth: '80%',
          }}
        >
          <Typography variant="body2" sx={{ color: '#B71C1C', fontWeight: 700 }}>
            {emergencyAwaitingPick
              ? `비상모드: ${emergencyLabel} — 지도를 클릭해 발생 위치를 지정하세요`
              : `비상모드: ${emergencyLabel} · 반경 3/7/11km 표시 중`}
          </Typography>
          {!emergencyAwaitingPick && (
            <Button size="small" color="error" variant="outlined" onClick={() => exitEmergencyMode()}>
              종료
            </Button>
          )}
        </Paper>
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
