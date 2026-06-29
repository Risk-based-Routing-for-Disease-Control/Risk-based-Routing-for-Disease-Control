import { create } from 'zustand';
import type { Farm } from '../types/farm';
import { mockFarms } from '../data/mockFarms';
import { normalizeFarmDuration } from '../utils/farmDuration';
import { fetchFarms } from '../api/farms';

const initialFarms = mockFarms.map(normalizeFarmDuration);

interface FarmStore {
  farms: Farm[];
  selectedFarmId: string | null;
  isLoading: boolean;
  selectFarm: (id: string) => void;
  clearSelection: () => void;
  loadFarms: () => Promise<void>;
}

export const useFarmStore = create<FarmStore>((set) => ({
  farms: initialFarms,
  selectedFarmId: initialFarms[0]?.id ?? null,
  isLoading: false,
  selectFarm: (id) => set({ selectedFarmId: id }),
  clearSelection: () => set({ selectedFarmId: null }),
  loadFarms: async () => {
    set({ isLoading: true });
    try {
      const farms = await fetchFarms();
      if (farms.length > 0) {
        set({ farms, selectedFarmId: farms[0]?.id ?? null });
      }
      // farms가 비어있으면 mockFarms 유지
    } catch {
      // API 오류 시 mockFarms 유지
    } finally {
      set({ isLoading: false });
    }
  },
}));
