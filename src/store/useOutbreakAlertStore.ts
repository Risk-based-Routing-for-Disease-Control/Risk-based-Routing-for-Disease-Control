import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { fetchOutbreakAlerts, type OutbreakCase } from '../api/alerts';

interface OutbreakAlertState {
  badgeCount: number;
  lastKnownCount: number;
  lastCheckedDate: string | null;
  cases: OutbreakCase[];
  isLoading: boolean;
  checkOutbreaks: () => Promise<void>;
  clearBadge: () => void;
}

export const useOutbreakAlertStore = create<OutbreakAlertState>()(
  persist(
    (set, get) => ({
      badgeCount: 0,
      lastKnownCount: 0,
      lastCheckedDate: null,
      cases: [],
      isLoading: false,
      checkOutbreaks: async () => {
        if (get().isLoading) return;
        set({ isLoading: true });
        try {
          const { ok, date, count, cases } = await fetchOutbreakAlerts();
          if (!ok) return;
          const { lastCheckedDate, lastKnownCount, badgeCount } = get();
          const isNewDay = lastCheckedDate !== null && lastCheckedDate !== date;
          const baseline = isNewDay ? 0 : lastKnownCount;
          const delta = Math.max(0, count - baseline);
          set({
            lastCheckedDate: date,
            lastKnownCount: count,
            badgeCount: badgeCount + delta,
            cases,
          });
        } catch {
          // 보조 기능이므로 실패 시 조용히 다음 폴링을 기다림
        } finally {
          set({ isLoading: false });
        }
      },
      clearBadge: () => set({ badgeCount: 0 }),
    }),
    {
      name: 'livestock-outbreak-alert',
      storage: createJSONStorage(() => sessionStorage),
      partialize: (state) => ({
        badgeCount: state.badgeCount,
        lastKnownCount: state.lastKnownCount,
        lastCheckedDate: state.lastCheckedDate,
        cases: state.cases,
      }),
    },
  ),
);
