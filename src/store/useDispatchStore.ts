import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Farm, RiskLevel } from '../types/farm';
import type { DispatchResult, DispatchTeam } from '../types/dispatch';
import { solveDispatch } from '../api/dispatch';
import { nowTimeLabel } from '../utils/time';

function buildLiveTeams(teams: DispatchTeam[]): DispatchTeam[] {
  return teams.map((team) => ({
    ...team,
    stops: team.stops.map((stop) => ({
      ...stop,
      status: 'upcoming' as const,
      completedAt: undefined,
      cancelledAt: undefined,
      actualDurationMinutes: undefined,
    })),
  }));
}

interface ConfirmedSummary {
  selectedFarmCount: number;
  teamCount: number;
  totalDurationMinutes: number;
}

interface DispatchState {
  teamCount: number;
  selectedFarmIds: string[];
  riskFilter: RiskLevel | 'all';
  typeFilter: string;
  result: DispatchResult | null;
  isDispatching: boolean;
  dispatchError: string | null;
  liveTeams: DispatchTeam[] | null;
  confirmed: boolean;
  confirmedSummary: ConfirmedSummary | null;
  lastUpdatedAt: string | null;
  setTeamCount: (count: number) => void;
  setRiskFilter: (value: RiskLevel | 'all') => void;
  setTypeFilter: (value: string) => void;
  toggleFarm: (id: string) => void;
  setSelectedFarmIds: (ids: string[]) => void;
  resetSelection: () => void;
  runDispatch: (farms: Farm[]) => Promise<void>;
  resetResult: () => void;
  confirmDispatch: () => void;
  advanceLiveProgress: () => void;
  completeStop: (teamId: string, farmId: string, actualDurationMinutes: number) => void;
  cancelStop: (teamId: string, farmId: string) => void;
}

export const useDispatchStore = create<DispatchState>()(
  persist(
    (set, get) => ({
      teamCount: 3,
      selectedFarmIds: [],
      riskFilter: 'all',
      typeFilter: 'all',
      result: null,
      isDispatching: false,
      dispatchError: null,
      liveTeams: null,
      confirmed: false,
      confirmedSummary: null,
      lastUpdatedAt: null,

      setTeamCount: (count) => set({ teamCount: Math.max(1, count) }),
      setRiskFilter: (value) => set({ riskFilter: value }),
      setTypeFilter: (value) => set({ typeFilter: value }),

      toggleFarm: (id) =>
        set((state) => ({
          selectedFarmIds: state.selectedFarmIds.includes(id)
            ? state.selectedFarmIds.filter((farmId) => farmId !== id)
            : [...state.selectedFarmIds, id],
        })),

      setSelectedFarmIds: (ids) => set({ selectedFarmIds: ids }),

      resetSelection: () => set({ selectedFarmIds: [], riskFilter: 'all', typeFilter: 'all' }),

      runDispatch: async (farms) => {
        const { selectedFarmIds, teamCount } = get();
        set({ isDispatching: true, dispatchError: null });
        try {
          const result = await solveDispatch({ farms, selectedFarmIds, teamCount });
          set({ result, isDispatching: false });
        } catch (error) {
          set({
            isDispatching: false,
            dispatchError: error instanceof Error ? error.message : '배차 요청에 실패했습니다.',
          });
        }
      },

      resetResult: () => set({ result: null, dispatchError: null }),

      confirmDispatch: () => {
        const { result } = get();
        if (!result) return;
        set({
          liveTeams: buildLiveTeams(result.teams),
          confirmed: true,
          confirmedSummary: {
            selectedFarmCount: result.selectedFarmCount,
            teamCount: result.teamCount,
            totalDurationMinutes: result.totalDurationMinutes,
          },
          lastUpdatedAt: nowTimeLabel(true),
        });
      },

      advanceLiveProgress: () =>
        set((state) => {
          if (!state.liveTeams) return state;
          const label = nowTimeLabel();
          const liveTeams = state.liveTeams.map((team) => {
            const nextIndex = team.stops.findIndex((stop) => stop.status === 'upcoming');
            if (nextIndex === -1) return team;
            const stops = team.stops.map((stop, index) =>
              index === nextIndex ? { ...stop, status: 'completed' as const, completedAt: label } : stop,
            );
            return { ...team, stops };
          });
          return { liveTeams, lastUpdatedAt: nowTimeLabel(true) };
        }),

      completeStop: (teamId, farmId, actualDurationMinutes) =>
        set((state) => {
          if (!state.liveTeams) return state;
          const label = nowTimeLabel();
          const liveTeams = state.liveTeams.map((team) => {
            if (team.id !== teamId) return team;
            const stops = team.stops.map((stop) =>
              stop.farm.id === farmId && stop.status === 'upcoming'
                ? {
                    ...stop,
                    status: 'completed' as const,
                    completedAt: label,
                    actualDurationMinutes,
                  }
                : stop,
            );
            return { ...team, stops };
          });
          return { liveTeams, lastUpdatedAt: nowTimeLabel(true) };
        }),

      cancelStop: (teamId, farmId) =>
        set((state) => {
          if (!state.liveTeams) return state;
          const label = nowTimeLabel();
          const liveTeams = state.liveTeams.map((team) => {
            if (team.id !== teamId) return team;
            const stops = team.stops.map((stop) =>
              stop.farm.id === farmId && stop.status === 'completed'
                ? {
                    ...stop,
                    status: 'upcoming' as const,
                    completedAt: undefined,
                    actualDurationMinutes: undefined,
                    cancelledAt: label,
                  }
                : stop,
            );
            return { ...team, stops };
          });
          return { liveTeams, lastUpdatedAt: nowTimeLabel(true) };
        }),
    }),
    {
      name: 'livestock-dispatch',
      partialize: (state) => ({
        teamCount: state.teamCount,
        selectedFarmIds: state.selectedFarmIds,
        result: state.result,
        isDispatching: state.isDispatching,
        dispatchError: state.dispatchError,
        liveTeams: state.liveTeams,
        confirmed: state.confirmed,
        confirmedSummary: state.confirmedSummary,
        lastUpdatedAt: state.lastUpdatedAt,
      }),
    },
  ),
);
