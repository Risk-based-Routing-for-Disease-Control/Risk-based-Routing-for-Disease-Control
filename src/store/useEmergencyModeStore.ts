import { create } from 'zustand';

interface EmergencyCenter {
  lat: number;
  lng: number;
}

interface EmergencyModeState {
  isActive: boolean;
  center: EmergencyCenter | null;
  label: string | null;
  awaitingPick: boolean;
  enterWithCenter: (center: EmergencyCenter, label: string) => void;
  enterAwaitingPick: (label: string) => void;
  setCenter: (center: EmergencyCenter) => void;
  exit: () => void;
}

export const useEmergencyModeStore = create<EmergencyModeState>((set) => ({
  isActive: false,
  center: null,
  label: null,
  awaitingPick: false,
  enterWithCenter: (center, label) => set({ isActive: true, center, label, awaitingPick: false }),
  enterAwaitingPick: (label) => set({ isActive: true, center: null, label, awaitingPick: true }),
  setCenter: (center) => set({ center, awaitingPick: false }),
  exit: () => set({ isActive: false, center: null, label: null, awaitingPick: false }),
}));
