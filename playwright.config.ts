import { defineConfig } from "@playwright/test";

const webPort = Number(process.env.WEB_PORT ?? "3000");
const apiPort = Number(process.env.API_PORT ?? "18000");
const webURL = `http://127.0.0.1:${webPort}`;
const apiURL = `http://127.0.0.1:${apiPort}`;

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: false,
  retries: 0,
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: webURL,
    trace: "retain-on-failure",
  },
  webServer: [
    {
      command:
        `PYTHONPATH=apps/api/src uv run python -m needradar.testing.database_safety serve-e2e --port ${apiPort}`,
      url: `${apiURL}/health`,
      env: {
        ...process.env,
        CORS_ORIGINS: JSON.stringify([webURL]),
      },
      reuseExistingServer: false,
      timeout: 120_000,
    },
    {
      command: "pnpm --filter @needradar/web dev",
      url: `${webURL}/dashboard`,
      env: {
        ...process.env,
        WEB_PORT: String(webPort),
        NEXT_PUBLIC_API_URL: apiURL,
      },
      reuseExistingServer: false,
      timeout: 120_000,
    },
  ],
});
