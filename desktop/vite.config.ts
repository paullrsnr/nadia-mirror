import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig(({ command }) => ({
  plugins: [react()],

  // 👉 le frontend est ici
  root: path.resolve(__dirname, "src/renderer"),

  // 👉 base différente dev / prod
  base: command === "build" ? "./" : "/",

  build: {
    // 👉 sortie EXACTEMENT là où Electron s’attend à la trouver
    outDir: path.resolve(__dirname, "dist/renderer"),
    emptyOutDir: true,
  },
}));
