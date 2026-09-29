import { describe, expect, it } from "vitest";

import { statusLabel } from "./foundation-status";

describe("statusLabel", () => {
  it("uses honest Foundation probe labels", () => {
    expect(statusLabel("checking")).toBe("检查中");
    expect(statusLabel("available")).toBe("可用");
    expect(statusLabel("unavailable")).toBe("不可用");
  });
});
