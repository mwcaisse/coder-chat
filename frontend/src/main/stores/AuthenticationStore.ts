import { create } from "zustand/react";
import { createJSONStorage, persist } from "zustand/middleware";

type AuthStore = {
    authToken: string | null;
    refreshToken: string | null;
    update: (authToken: string, refreshToken: string) => void;
};

export const useAuthStore = create<AuthStore>()(
    persist(
        (set) => ({
            authToken: null,
            refreshToken: null,
            update: (authToken: string, refreshToken: string) => {
                set({ authToken, refreshToken });
            },
        }),
        {
            name: "coderchat-auth",
            storage: createJSONStorage(() => localStorage),
        },
    ),
);
