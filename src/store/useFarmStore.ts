import { create } from 'zustand';
import type { Farm } from '../types/farm';
import { mockFarms } from '../data/mockFarms';

interface FarmStore {
  farms: Farm[];
  selectedFarmId: string | null;
  selectFarm: (id: string) => void;
  clearSelection: () => void;
}

export const useFarmStore = create<FarmStore>((set) => ({
  farms: mockFarms,
  selectedFarmId: mockFarms[0]?.id ?? null,
  selectFarm: (id) => set({ selectedFarmId: id }),
  clearSelection: () => set({ selectedFarmId: null }),
}));
