import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
// The `test` block below is AI-generated (Claude, Anthropic) — it's read by Vitest,
// not by Vite itself, to configure the frontend test suite in src/**/*.test.jsx.
export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: './src/setupTests.js',
    globals: true,
  },
})
