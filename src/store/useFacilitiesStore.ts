import { create } from 'zustand';
import type { DispatchDisinfectionHub } from '../types/dispatch';
import { fetchFacilities } from '../api/facilities';

interface FacilitiesStore {
  facilities: DispatchDisinfectionHub[];
  isLoading: boolean;
  loadFacilities: () => Promise<void>;
}

export const useFacilitiesStore = create<FacilitiesStore>((set, get) => ({
  facilities: [],
  isLoading: false,
  loadFacilities: async () => {
    if (get().facilities.length > 0 || get().isLoading) return;
    set({ isLoading: true });
    try {
      const facilities = await fetchFacilities();
      set({ facilities });
    } catch {
      // API 오류 시 빈 배열 유지
    } finally {
      set({ isLoading: false });
    }
  },
}));
