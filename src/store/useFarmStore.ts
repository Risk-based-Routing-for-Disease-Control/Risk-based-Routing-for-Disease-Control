import { create } from 'zustand';
import type { Farm } from '../types/farm';
import { mockFarms } from '../data/mockFarms';
import { normalizeFarmDuration } from '../utils/farmDuration';

const farms = mockFarms.map(normalizeFarmDuration);

interface FarmStore {
  farms: Farm[];
  selectedFarmId: string | null;
  selectFarm: (id: string) => void;
  clearSelection: () => void;
}

export const useFarmStore = create<FarmStore>((set) => ({
  farms,
  selectedFarmId: farms[0]?.id ?? null,
  selectFarm: (id) => set({ selectedFarmId: id }),
  clearSelection: () => set({ selectedFarmId: null }),
}));
