import { create } from "zustand";
import { User, UserRole, AuthTokens } from "../types";

interface AuthState {
  token: string | null;
  refreshToken: string | null;
  user: User | null;
  role: UserRole | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setAuth: (tokens: AuthTokens) => void;
  setUser: (user: User) => void;
  logout: () => void;
}

const TOKEN_KEY = "delayray_access_token";
const REFRESH_KEY = "delayray_refresh_token";
const USER_ROLE_KEY = "delayray_user_role";
const USER_EMAIL_KEY = "delayray_user_email";

const savedToken = localStorage.getItem(TOKEN_KEY);
const savedRole = localStorage.getItem(USER_ROLE_KEY) as UserRole | null;
const savedEmail = localStorage.getItem(USER_EMAIL_KEY);

export const useAuthStore = create<AuthState>((set) => ({
  token: savedToken,
  refreshToken: localStorage.getItem(REFRESH_KEY),
  user: savedEmail && savedRole ? { id: 1, email: savedEmail, role: savedRole, is_active: true } : null,
  role: savedRole || (savedToken ? "analyst" : null),
  isAuthenticated: !!savedToken,
  isLoading: false,

  setAuth: (tokens: AuthTokens) => {
    localStorage.setItem(TOKEN_KEY, tokens.access_token);
    if (tokens.refresh_token) {
      localStorage.setItem(REFRESH_KEY, tokens.refresh_token);
    }
    localStorage.setItem(USER_ROLE_KEY, tokens.role);
    localStorage.setItem(USER_EMAIL_KEY, tokens.email);

    set({
      token: tokens.access_token,
      refreshToken: tokens.refresh_token || null,
      role: tokens.role,
      user: { id: 1, email: tokens.email, role: tokens.role, is_active: true },
      isAuthenticated: true,
      isLoading: false,
    });
  },

  setUser: (user: User) => set({ user, role: user.role }),

  logout: () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(USER_ROLE_KEY);
    localStorage.removeItem(USER_EMAIL_KEY);
    set({
      token: null,
      refreshToken: null,
      user: null,
      role: null,
      isAuthenticated: false,
    });
  },
}));
