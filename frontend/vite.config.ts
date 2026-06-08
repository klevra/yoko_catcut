import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";

function parseAllowedHosts(value?: string): true | string[] {
  if (!value || value === "true" || value === "*") {
    return true;
  }
  return value
    .split(",")
    .map((host) => host.trim())
    .filter(Boolean);
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const allowedHosts = parseAllowedHosts(env.VITE_ALLOWED_HOSTS);

  return {
    plugins: [react()],
    server: {
      host: "0.0.0.0",
      port: 3000,
      allowedHosts,
    },
    preview: {
      host: "0.0.0.0",
      port: 3000,
      allowedHosts,
    },
  };
});
