import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// https://vite.dev/config/
export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            "@app": path.resolve(__dirname, "src/main/"),
            "@test": path.resolve(__dirname, "src/test/"),
        },
    },
    server: {
        proxy: {
            "/api": {
                target: "http://localhost:5005",
            },
        },
    },
});
