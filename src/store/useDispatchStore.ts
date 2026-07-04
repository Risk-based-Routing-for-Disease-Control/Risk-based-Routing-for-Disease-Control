import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { Farm, RiskLevel } from '../types/farm';
import type { DispatchResult, DispatchTeam } from '../types/dispatch';
import { cancelDispatchStop, completeDispatchStop, fetchDispatchRunTeams, routeAssignment } from '../api/dispatch';
import { useFacilitiesStore } from './useFacilitiesStore';
import { useFarmStore } from './useFarmStore';
import { useEmergencyModeStore } from './useEmergencyModeStore';
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
  dispatchRunId: string | null;
  isDispatching: boolean;
  dispatchError: string | null;
  liveTeams: DispatchTeam[] | null;
  confirmed: boolean;
  confirmedSummary: ConfirmedSummary | null;
  lastUpdatedAt: string | null;
  syncError: string | null;
  isLoadingRun: boolean;
  loadRunError: string | null;
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
  completeStop: (teamId: string, farmId: string, actualDurationMinutes: number) => Promise<void>;
  cancelStop: (teamId: string, farmId: string) => Promise<void>;
  syncLiveTeams: () => Promise<void>;
  loadDispatchRun: (dispatchRunId: string) => Promise<void>;
}

export const useDispatchStore = create<DispatchState>()(
  persist(
    (set, get) => ({
      teamCount: 3,
      selectedFarmIds: [],
      riskFilter: 'all',
      typeFilter: 'all',
      result: null,
      dispatchRunId: null,
      isDispatching: false,
      dispatchError: null,
      liveTeams: null,
      confirmed: false,
      confirmedSummary: null,
      lastUpdatedAt: null,
      syncError: null,
      isLoadingRun: false,
      loadRunError: null,

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
          const facilities = useFacilitiesStore.getState().facilities;
          const facilitiesMap = new Map(facilities.map((f) => [f.id, f]));
          const emergencyState = useEmergencyModeStore.getState();
          const { result, dispatchRunId } = await routeAssignment(
            {
              teamCount,
              farmIds: selectedFarmIds,
              farms,
              emergencyMode: emergencyState.isActive,
              emergencyCenterLat: emergencyState.center?.lat,
              emergencyCenterLng: emergencyState.center?.lng,
              outbreakFarmId: emergencyState.outbreakFarmId,
            },
            facilitiesMap,
          );
          set({ result, dispatchRunId, isDispatching: false });
        } catch (error) {
          set({
            isDispatching: false,
            dispatchError: error instanceof Error ? error.message : '배차 요청에 실패했습니다.',
          });
        }
      },

      resetResult: () => set({ result: null, dispatchRunId: null, dispatchError: null }),

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
          const timestamp = new Date().toISOString();
          const liveTeams = state.liveTeams.map((team) => {
            const nextIndex = team.stops.findIndex((stop) => stop.status === 'upcoming');
            if (nextIndex === -1) return team;
            const stops = team.stops.map((stop, index) =>
              index === nextIndex ? { ...stop, status: 'completed' as const, completedAt: timestamp } : stop,
            );
            return { ...team, stops };
          });
          return { liveTeams, lastUpdatedAt: nowTimeLabel(true) };
        }),

      completeStop: async (teamId, farmId, actualDurationMinutes) => {
        set((state) => {
          if (!state.liveTeams) return state;
          const timestamp = new Date().toISOString();
          const liveTeams = state.liveTeams.map((team) => {
            if (team.id !== teamId) return team;
            const stops = team.stops.map((stop) =>
              stop.farm.id === farmId && stop.status === 'upcoming'
                ? {
                    ...stop,
                    status: 'completed' as const,
                    completedAt: timestamp,
                    actualDurationMinutes,
                  }
                : stop,
            );
            return { ...team, stops };
          });
          return { liveTeams, lastUpdatedAt: nowTimeLabel(true) };
        });

        const { dispatchRunId } = get();
        if (!dispatchRunId) return;
        try {
          await completeDispatchStop(dispatchRunId, teamId, farmId, actualDurationMinutes);
          set({ syncError: null });
        } catch (error) {
          set({ syncError: error instanceof Error ? error.message : '완료 처리 서버 반영에 실패했습니다.' });
        }
      },

      cancelStop: async (teamId, farmId) => {
        set((state) => {
          if (!state.liveTeams) return state;
          const timestamp = new Date().toISOString();
          const liveTeams = state.liveTeams.map((team) => {
            if (team.id !== teamId) return team;
            const stops = team.stops.map((stop) =>
              stop.farm.id === farmId && stop.status === 'completed'
                ? {
                    ...stop,
                    status: 'upcoming' as const,
                    completedAt: undefined,
                    actualDurationMinutes: undefined,
                    cancelledAt: timestamp,
                  }
                : stop,
            );
            return { ...team, stops };
          });
          return { liveTeams, lastUpdatedAt: nowTimeLabel(true) };
        });

        const { dispatchRunId } = get();
        if (!dispatchRunId) return;
        try {
          await cancelDispatchStop(dispatchRunId, teamId, farmId);
          set({ syncError: null });
        } catch (error) {
          set({ syncError: error instanceof Error ? error.message : '취소 처리 서버 반영에 실패했습니다.' });
        }
      },

      syncLiveTeams: async () => {
        const { dispatchRunId, liveTeams } = get();
        if (!dispatchRunId || !liveTeams) return;
        try {
          const farmMap = new Map(useFarmStore.getState().farms.map((f) => [f.id, f]));
          const facilitiesMap = new Map(useFacilitiesStore.getState().facilities.map((f) => [f.id, f]));
          const teams = await fetchDispatchRunTeams(dispatchRunId, farmMap, facilitiesMap);
          set({ liveTeams: teams, lastUpdatedAt: nowTimeLabel(true), syncError: null });
        } catch (error) {
          set({ syncError: error instanceof Error ? error.message : '실시간 현황 동기화에 실패했습니다.' });
        }
      },

      loadDispatchRun: async (dispatchRunId) => {
        set({ isLoadingRun: true, loadRunError: null });
        try {
          const farmMap = new Map(useFarmStore.getState().farms.map((f) => [f.id, f]));
          const facilitiesMap = new Map(useFacilitiesStore.getState().facilities.map((f) => [f.id, f]));
          const teams = await fetchDispatchRunTeams(dispatchRunId, farmMap, facilitiesMap);
          const totalDurationMinutes = teams.reduce((sum, t) => sum + t.totalDurationMinutes, 0);
          const selectedFarmCount = teams.reduce((sum, t) => sum + t.stops.length, 0);
          set({
            dispatchRunId,
            liveTeams: teams,
            confirmed: true,
            confirmedSummary: { selectedFarmCount, teamCount: teams.length, totalDurationMinutes },
            lastUpdatedAt: nowTimeLabel(true),
            isLoadingRun: false,
          });
        } catch (error) {
          set({
            isLoadingRun: false,
            loadRunError: error instanceof Error ? error.message : '배차 결과를 불러오지 못했습니다.',
          });
        }
      },
    }),
    {
      name: 'livestock-dispatch',
      storage: createJSONStorage(() => sessionStorage),
      partialize: (state) => ({
        teamCount: state.teamCount,
        selectedFarmIds: state.selectedFarmIds,
        result: state.result,
        dispatchRunId: state.dispatchRunId,
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
