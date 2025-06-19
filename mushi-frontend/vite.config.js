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
  server: {
    proxy: {
      // Proxy API requests to the Flask backend
      '/api': {
        target: 'http://127.0.0.1:8001', // Your Flask backend URL
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
