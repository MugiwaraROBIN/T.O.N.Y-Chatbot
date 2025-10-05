import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Use environment variables for API URL
const API_URL = process.env.VITE_API_URL || 'https://your-backend.onrender.com'

export default defineConfig({
  plugins: [react()],
  define: {
    __API_URL__: JSON.stringify(API_URL),
  },
  server: {
    // Local dev server config (optional)
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
