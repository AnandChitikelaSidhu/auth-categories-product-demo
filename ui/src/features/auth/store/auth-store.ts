import type { TokenResponse, User, UserRole } from "@/shared/types/api.types";
import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
  setSession: (tokens: TokenResponse, user?: User | null) => void;
  setUser: (user: User) => void;
  clearSession: () => void;
  hasRole: (roles: UserRole[]) => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      setSession: (tokens, user = null) =>
        set({
          accessToken: tokens.access_token,
          refreshToken: tokens.refresh_token,
          user,
        }),
      setUser: (user) => set({ user }),
      clearSession: () => set({ accessToken: null, refreshToken: null, user: null }),
      hasRole: (roles) => {
        const role = get().user?.role;
        return role ? roles.includes(role) : false;
      },
    }),
    {
      name: "kalo-auth",
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
      }),
    },
  ),
);

export const selectIsAuthenticated = (state: AuthState) => Boolean(state.accessToken);
export const selectIsAdmin = (state: AuthState) =>
  state.user?.role === "admin" || state.user?.role === "super_admin";
export const selectIsSuperAdmin = (state: AuthState) => state.user?.role === "super_admin";
