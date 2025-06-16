// mushi-frontend/vite.config.js
import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      // Corrected alias to point to the 'src' directory
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
