import type { components } from "./generated/schema";

export type HealthResponse = components["schemas"]["HealthResponse"];
export type ReadyResponse = components["schemas"]["ReadyResponse"];

export type ProblemDetails = components["schemas"]["ProblemDetails"] & {
  database?: string;
  schema?: string;
};

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { Accept: "application/json" },
    cache: "no-store",
  });
  const payload: unknown = await response.json();
  if (!response.ok) {
    throw payload as ProblemDetails;
  }
  return payload as T;
}

export function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}

export function getReadiness(): Promise<ReadyResponse> {
  return request<ReadyResponse>("/ready");
}
