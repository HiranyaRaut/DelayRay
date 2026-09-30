import { create } from "zustand";

export type Theme = "dark" | "light";
export type CurrencyFormat = "in" | "plain";
export type Language = "en" | "hi";

export interface ToastMessage {
  id: string;
  type: "info" | "success" | "warning" | "error" | "critical";
  title: string;
  message?: string;
  duration?: number;
}

interface AppState {
  theme: Theme;
  currencyFormat: CurrencyFormat;
  language: Language;
  presentationMode: boolean;
  commandPaletteOpen: boolean;
  toasts: ToastMessage[];

  toggleTheme: () => void;
  setTheme: (theme: Theme) => void;
  toggleCurrencyFormat: () => void;
  setLanguage: (lang: Language) => void;
  togglePresentationMode: () => void;
  setCommandPaletteOpen: (open: boolean) => void;
  addToast: (toast: Omit<ToastMessage, "id">) => void;
  removeToast: (id: string) => void;
}

const initialTheme: Theme = (localStorage.getItem("delayray_theme") as Theme) || "dark";
if (initialTheme === "dark") {
  document.documentElement.classList.add("dark");
} else {
  document.documentElement.classList.remove("dark");
}

export const useAppStore = create<AppState>((set, get) => ({
  theme: initialTheme,
  currencyFormat: (localStorage.getItem("delayray_currency") as CurrencyFormat) || "in",
  language: (localStorage.getItem("delayray_lang") as Language) || "en",
  presentationMode: false,
  commandPaletteOpen: false,
  toasts: [],

  toggleTheme: () => {
    const nextTheme = get().theme === "dark" ? "light" : "dark";
    if (nextTheme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
    localStorage.setItem("delayray_theme", nextTheme);
    set({ theme: nextTheme });
  },

  setTheme: (theme: Theme) => {
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
    localStorage.setItem("delayray_theme", theme);
    set({ theme });
  },

  toggleCurrencyFormat: () => {
    const next = get().currencyFormat === "in" ? "plain" : "in";
    localStorage.setItem("delayray_currency", next);
    set({ currencyFormat: next });
  },

  setLanguage: (language: Language) => {
    localStorage.setItem("delayray_lang", language);
    set({ language });
  },

  togglePresentationMode: () => {
    set((state) => ({ presentationMode: !state.presentationMode }));
  },

  setCommandPaletteOpen: (commandPaletteOpen: boolean) => {
    set({ commandPaletteOpen });
  },

  addToast: (toast) => {
    const id = Math.random().toString(36).substring(2, 9);
    const newToast: ToastMessage = { ...toast, id, duration: toast.duration || 5000 };
    set((state) => ({ toasts: [...state.toasts, newToast] }));

    setTimeout(() => {
      get().removeToast(id);
    }, newToast.duration);
  },

  removeToast: (id: string) => {
    set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) }));
  },
}));
