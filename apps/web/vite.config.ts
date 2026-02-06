import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, "../..", "");
  const port = Number(env.VITE_WEB_PORT || 5173);
  return {
    plugins: [react()],
    envDir: "../..",
    server: {
      port,
      host: true,
    },
  };
});
