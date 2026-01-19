import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

const backendPort = Number(process.env.BACKEND_PORT || 8000);

// https://vite.dev/config/
export default defineConfig(() => ({
  root: path.resolve(__dirname, 'src/frontend/compile'),
  publicDir: path.resolve(__dirname, 'src/frontend/static'),
  plugins: [react()],
  build: {
    outDir: path.resolve(__dirname, 'dist/frontend'),
    emptyOutDir: true,
  },
}));
