import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Farm, RiskLevel } from '../types/farm';
import type { DispatchResult, DispatchTeam } from '../types/dispatch';
import { TEAM_COLORS } from '../constants/teamColors';
import { minutesToTimeLabel, nowTimeLabel } from '../utils/time';

const TEAM_CAPACITY_MINUTES = 240;
const START_OF_DAY_MINUTES = 8 * 60 + 30;

function buildDispatchResult(farms: Farm[], selectedFarmIds: string[], teamCount: number): DispatchResult {
  const selected = farms
    .filter((farm) => selectedFarmIds.includes(farm.id))
    .sort((a, b) => b.riskScore - a.riskScore);

  const teams: DispatchTeam[] = Array.from({ length: teamCount }, (_, index) => ({
    id: `team-${index + 1}`,
    label: `팀 ${index + 1}`,
    color: TEAM_COLORS[index % TEAM_COLORS.length],
    stops: [],
    totalDurationMinutes: 0,
  }));

  const unassignedFarms: Farm[] = [];

  selected.forEach((farm) => {
    const target = teams.reduce((min, team) => (team.totalDurationMinutes < min.totalDurationMinutes ? team : min), teams[0]);
    if (!target || target.totalDurationMinutes + farm.estimatedDurationMinutes > TEAM_CAPACITY_MINUTES) {
      unassignedFarms.push(farm);
      return;
    }
    target.stops.push({ farm, order: target.stops.length + 1, status: 'plain' });
    target.totalDurationMinutes += farm.estimatedDurationMinutes;
  });

  return {
    teams,
    unassignedFarms,
    selectedFarmCount: selected.length,
    teamCount,
    totalDurationMinutes: teams.reduce((sum, team) => sum + team.totalDurationMinutes, 0),
  };
}

function buildLiveTeams(teams: DispatchTeam[]): DispatchTeam[] {
  return teams.map((team) => {
    const completedCount = team.stops.length === 0 ? 0 : Math.max(1, Math.round(team.stops.length * 0.3));
    let clock = START_OF_DAY_MINUTES;
    const stops = team.stops.map((stop, index) => {
      if (index >= completedCount) return { ...stop, status: 'upcoming' as const };
      clock += stop.farm.estimatedDurationMinutes;
      const completedAt = minutesToTimeLabel(clock);
      clock += 15;
      return { ...stop, status: 'completed' as const, completedAt };
    });
    return { ...team, stops };
  });
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
  runDispatch: (farms: Farm[]) => void;
  resetResult: () => void;
  confirmDispatch: () => void;
  advanceLiveProgress: () => void;
}

export const useDispatchStore = create<DispatchState>()(
  persist(
    (set, get) => ({
      teamCount: 3,
      selectedFarmIds: [],
      riskFilter: 'all',
      typeFilter: 'all',
      result: null,
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

      runDispatch: (farms) => {
        const { selectedFarmIds, teamCount } = get();
        set({ result: buildDispatchResult(farms, selectedFarmIds, teamCount) });
      },

      resetResult: () => set({ result: null }),

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
    }),
    {
      name: 'livestock-dispatch',
      partialize: (state) => ({
        teamCount: state.teamCount,
        selectedFarmIds: state.selectedFarmIds,
        result: state.result,
        liveTeams: state.liveTeams,
        confirmed: state.confirmed,
        confirmedSummary: state.confirmedSummary,
        lastUpdatedAt: state.lastUpdatedAt,
      }),
    },
  ),
);
