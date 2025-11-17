import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
// https://vite.dev/config/shared-options
export default defineConfig({
  plugins: [react()],
  root: "src/frontend",
})
