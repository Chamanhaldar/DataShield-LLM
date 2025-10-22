import { create } from "zustand";

export interface AuthState {
  token: string | null;
  setToken: (token: string | null) => void;
}

type SetState<T> = (
  partial: T | Partial<T> | ((state: T) => T | Partial<T>),
  replace?: boolean,
  name?: string,
) => void;

export const useAuthStore = create<AuthState>((set: SetState<AuthState>) => ({
  token: null,
  setToken: (token: string | null) => set({ token }),
}));
