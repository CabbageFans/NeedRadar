import { FoundationStatus } from "@/src/components/foundation-status";

export default function DashboardPage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-5xl flex-col justify-center px-6 py-16">
      <div className="mb-10 max-w-3xl">
        <p className="mb-3 text-sm font-semibold uppercase tracking-[0.28em] text-emerald-300">
          CHANGE-001 / C001-S1
        </p>
        <h1 className="text-5xl font-semibold tracking-tight text-white">NeedRadar</h1>
        <p className="mt-5 text-lg leading-8 text-emerald-50/70">
          当前是 Foundation 阶段：只验证本地 Web、API、PostgreSQL 与 schema readiness。
          Research Project 和后续需求研究能力尚未实现。
        </p>
      </div>
      <FoundationStatus />
    </main>
  );
}
