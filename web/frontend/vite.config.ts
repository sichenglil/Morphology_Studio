import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: { alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) } },
  build: {
    outDir: '../../src/morphology_toolkit/static/frontend',
    emptyOutDir: true,
  },
  server: { proxy: { '/api': 'http://127.0.0.1:8000' } },
  test: { environment: 'jsdom', globals: true, include: ['tests/*.spec.ts', 'tests/performance/*.spec.ts'] },
})
