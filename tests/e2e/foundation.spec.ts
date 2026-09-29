import { expect, test } from "@playwright/test";

// Quality binding: REQ-FOUNDATION-001 / AC-FOUNDATION-001.
test("real Foundation Web reaches healthy and ready FastAPI", async ({ page }) => {
  await page.goto("/dashboard");
  await expect(page.getByRole("heading", { name: "NeedRadar" })).toBeVisible();
  await expect(page.getByText("CHANGE-001 / C001-S1")).toBeVisible();
  await expect(page.getByTestId("api-health")).toHaveText("可用");
  await expect(page.getByTestId("api-readiness")).toHaveText("可用");
  await expect(page.getByTestId("readiness-detail")).toContainText("Alembic revision 20260928_0001");
  await expect(page.getByText("Research Project 和后续需求研究能力尚未实现。", { exact: false })).toBeVisible();
});
