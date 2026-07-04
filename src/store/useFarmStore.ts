import { create } from 'zustand';
import type { Farm } from '../types/farm';
import { mockFarms } from '../data/mockFarms';
import { normalizeFarmDuration } from '../utils/farmDuration';
import { fetchFarms, updateSuspectedFarm } from '../api/farms';

const initialFarms = mockFarms.map(normalizeFarmDuration);

interface FarmStore {
  farms: Farm[];
  selectedFarmId: string | null;
  isLoading: boolean;
  dataSource: 'db' | 'dummy' | 'unknown';
  loadError: string | null;
  selectFarm: (id: string) => void;
  clearSelection: () => void;
  loadFarms: () => Promise<void>;
  toggleSuspected: (farmId: string, suspected: boolean) => Promise<void>;
}

export const useFarmStore = create<FarmStore>((set, get) => ({
  farms: initialFarms,
  selectedFarmId: initialFarms[0]?.id ?? null,
  isLoading: false,
  dataSource: 'unknown',
  loadError: null,
  selectFarm: (id) => set({ selectedFarmId: id }),
  clearSelection: () => set({ selectedFarmId: null }),
  loadFarms: async () => {
    set({ isLoading: true });
    try {
      const result = await fetchFarms();
      if (result.farms.length > 0) {
        set({ farms: result.farms, selectedFarmId: result.farms[0]?.id ?? null });
      }
      // farms가 비어있으면 mockFarms 유지하되 소스/에러는 그대로 반영
      set({ dataSource: result.source, loadError: result.error });
    } catch (error) {
      // API 자체 호출 실패(백엔드 미기동 등) — mockFarms 유지하되 화면에 알림
      set({
        dataSource: 'dummy',
        loadError: error instanceof Error ? error.message : '농장 데이터 연동에 실패했습니다.',
      });
    } finally {
      set({ isLoading: false });
    }
  },
  toggleSuspected: async (farmId, suspected) => {
    set({
      farms: get().farms.map((farm) => (farm.id === farmId ? { ...farm, suspectedFarm: suspected } : farm)),
    });
    try {
      await updateSuspectedFarm(farmId, suspected);
    } catch (error) {
      // 서버 반영 실패해도 로컬 표시는 유지 — 다음 새로고침 시 서버 값으로 다시 맞춰짐
      console.error('[useFarmStore] failed to update suspected farm', error);
    }
  },
}));
