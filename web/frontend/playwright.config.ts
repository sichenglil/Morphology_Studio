import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  workers: 1,
  timeout: 30_000,
  use: { baseURL: 'http://127.0.0.1:8771', channel: 'msedge', screenshot: 'only-on-failure' },
  webServer: {
    command: `powershell -NoProfile -Command "$env:PYTHONPATH=(Resolve-Path '../../src'); python -m morphology_toolkit.cli web --port 8771"`,
    url: 'http://127.0.0.1:8771/api/health',
    timeout: 30_000,
    reuseExistingServer: true,
  },
})
