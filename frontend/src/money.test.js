import { describe, it, expect } from "vitest";
import { formatEUR } from "./money.js";

describe("formatEUR", () => {
  it("formats a number as EUR currency", () => {
    const result = formatEUR(1234.5);
    expect(result).toContain("€");
    // Locale spacing/grouping can vary (1,234.50 vs 1.234,50), just check the digits are there.
    expect(result).toMatch(/1[.,]234[.,]50/);
  });

  it("formats zero correctly", () => {
    const result = formatEUR(0);
    expect(result).toContain("€");
    expect(result).toMatch(/0[.,]00/);
  });
});
