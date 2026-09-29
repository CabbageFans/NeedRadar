"use client";

import { useEffect, useState } from "react";
import { getHealth, getReadiness, type ProblemDetails } from "@/src/lib/api/foundation";

type ProbeState = "checking" | "available" | "unavailable";

export function statusLabel(state: ProbeState): string {
  if (state === "checking") return "检查中";
  if (state === "available") return "可用";
  return "不可用";
}

export function FoundationStatus() {
  const [health, setHealth] = useState<ProbeState>("checking");
  const [readiness, setReadiness] = useState<ProbeState>("checking");
  const [detail, setDetail] = useState("正在读取真实 FastAPI 状态…");

  useEffect(() => {
    let active = true;
    Promise.allSettled([getHealth(), getReadiness()]).then(([healthResult, readyResult]) => {
      if (!active) return;
      setHealth(healthResult.status === "fulfilled" ? "available" : "unavailable");
      setReadiness(readyResult.status === "fulfilled" ? "available" : "unavailable");
      if (readyResult.status === "fulfilled") {
        setDetail(`PostgreSQL 已连接，Alembic revision ${readyResult.value.revision} 位于 head。`);
      } else {
        const problem = readyResult.reason as ProblemDetails | undefined;
        setDetail(problem?.detail ?? "API readiness 当前不可用。");
      }
    });
    return () => {
      active = false;
    };
  }, []);

  return (
    <section className="grid gap-4 md:grid-cols-2" aria-label="Foundation 状态">
      <StatusCard label="API health" state={health} description="只表示 API 进程存活，不依赖数据库。" />
      <StatusCard label="API readiness" state={readiness} description="要求 PostgreSQL 可连接且 Alembic schema 等于 head。" />
      <p className="md:col-span-2 rounded-2xl border border-emerald-900 bg-black/20 px-5 py-4 text-sm text-emerald-50/70" data-testid="readiness-detail">
        {detail}
      </p>
    </section>
  );
}

function StatusCard({ label, state, description }: { label: string; state: ProbeState; description: string }) {
  return (
    <article className="rounded-2xl border border-emerald-800/70 bg-emerald-950/50 p-6 shadow-2xl shadow-black/20">
      <div className="flex items-center justify-between gap-4">
        <h2 className="text-base font-medium text-emerald-50">{label}</h2>
        <span className="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-semibold text-emerald-300" data-testid={label.toLowerCase().replace(" ", "-")}>
          {statusLabel(state)}
        </span>
      </div>
      <p className="mt-4 text-sm leading-6 text-emerald-100/60">{description}</p>
    </article>
  );
}
