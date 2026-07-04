import { create } from 'zustand';

interface EmergencyCenter {
  lat: number;
  lng: number;
}

interface EmergencyModeState {
  isActive: boolean;
  center: EmergencyCenter | null;
  label: string | null;
  outbreakFarmId: string | null;
  awaitingPick: boolean;
  enterWithCenter: (center: EmergencyCenter, label: string, outbreakFarmId?: string | null) => void;
  enterAwaitingPick: (label: string) => void;
  setCenter: (center: EmergencyCenter) => void;
  exit: () => void;
}

export const useEmergencyModeStore = create<EmergencyModeState>((set) => ({
  isActive: false,
  center: null,
  label: null,
  outbreakFarmId: null,
  awaitingPick: false,
  enterWithCenter: (center, label, outbreakFarmId = null) =>
    set({ isActive: true, center, label, outbreakFarmId, awaitingPick: false }),
  enterAwaitingPick: (label) =>
    set({ isActive: true, center: null, label, outbreakFarmId: null, awaitingPick: true }),
  setCenter: (center) => set({ center, awaitingPick: false }),
  exit: () => set({ isActive: false, center: null, label: null, outbreakFarmId: null, awaitingPick: false }),
}));
