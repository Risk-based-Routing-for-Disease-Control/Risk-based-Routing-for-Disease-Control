import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

const ALLOWED_IDS = ['admin', 'field']; // 두 번째 계정명은 여기만 바꾸면 됨
const PASSWORD = '12345678'; // 공통 비밀번호(8자리) — 여기만 바꾸면 됨

interface AuthState {
  isLoggedIn: boolean;
  userId: string | null;
  login: (id: string, password: string) => boolean;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      isLoggedIn: false,
      userId: null,
      login: (id, password) => {
        const trimmed = id.trim();
        if (!ALLOWED_IDS.includes(trimmed) || password !== PASSWORD) return false;
        set({ isLoggedIn: true, userId: trimmed });
        return true;
      },
      logout: () => set({ isLoggedIn: false, userId: null }),
    }),
    { name: 'livestock-auth', storage: createJSONStorage(() => localStorage) },
  ),
);
