import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vite.dev/config/
export default defineConfig(() => ({
  root: path.resolve(__dirname, 'src/frontend/compile'),
  publicDir: path.resolve(__dirname, 'src/frontend/static'),
  plugins: [react()],
  build: {
    outDir: path.resolve(__dirname, 'src/frontend/dist'),
    emptyOutDir: true,
  },
}));
