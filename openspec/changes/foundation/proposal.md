# Proposal

## Why

NeedRadar 的后续 Planner、采集、分析、聚类与评分能力都依赖一个可执行、可迁移、以后端为事实源的产品边界。CHANGE-001 先建立最小且真实的 Web → API → PostgreSQL 闭环，使后续 Change 可以在稳定的 Project aggregate、状态策略和通知契约上增量开发，而不是各自建立不一致的基础设施。

## Business Outcome

用户能够通过 Web UI 创建一个空 Research Project，并在 Dashboard 查看由后端管理、持久化于 PostgreSQL 的真实 Project 状态。

## What Changes

- 建立单体仓库中的 Next.js Web、FastAPI API、PostgreSQL/Alembic、开发配置、真实数据库 readiness 与测试边界。
- 建立最小 `research_project` aggregate、UUID/UTC/版本字段、create/list/get/soft-delete API 及结构化错误。
- 持久化 DEC-006 的 13 状态词汇，并由单一后端 transition service 执行合法转换、失败来源恢复和终态约束。
- 建立只展示真实 Project 数据的 Dashboard；未产生的下游指标显示“尚未分析”/`—`或隐藏，绝不以假 `0` 代替。
- 建立 REST Snapshot + SSE Notification：通过 Connect → `STREAM_READY` → Buffer → GET Snapshot → Reconcile 消除建连竞态，区分 mutation version 与 transport identity，并在断线后重复完整 handshake。
- 建立结构化后端日志和 `crawler_worker`、`analysis_worker`、`clustering_worker` 的逻辑接口/注册边界，不实现任何真实 worker 业务。
- 规划每个 Slice 的静态、单元、真实 PostgreSQL integration 和 Playwright E2E 验证，并在 C001-S6 汇总可复现证据。
- 本 Change 不包含 breaking API 或数据兼容承诺；仓库目前没有已发布实现或 main capability spec。

## In Scope

- Monorepo/project skeleton 与可复现本地启动路径。
- Node.js 24.x LTS、唯一 pnpm package-manager authority、Next.js 15+、React 19+、TypeScript、Tailwind CSS 的 Foundation Web。
- Python 3.11.x、uv、FastAPI、SQLAlchemy、Alembic 与唯一 Psycopg 3 async driver family；本机 Python 3.14.6 不是项目 runtime contract。
- PostgreSQL 18.x（同一 major 的最新支持 minor）、Alembic schema authority、连接生命周期、独立测试数据库与 pytest/pytest-asyncio strict 策略。
- `/health` 仅表示 API process alive；`/ready` 同时验证真实 PostgreSQL connectivity 与数据库 Alembic revision 等于应用 head，且不自动迁移。
- 默认仅绑定 `127.0.0.1`，CORS 仅允许显式本地 Web origin；所有 secret 只进入 backend runtime，不进入前端、SSE、日志或 Git tracked `.env`。
- Foundation `research_project` schema：`id`、`name`、`original_query`、`context`、`status`、`planner_version`、`created_at`、`updated_at`、`completed_at`、`deleted_at`、`project_version`、`failed_from_status`。
- Project create/list/get/delete、soft-delete 默认过滤、backend-owned state、Snapshot、Foundation progress。
- Dashboard 的新建入口、Project 列表/名称/原始问题/真实状态/基础进度/更新时间/进入 Project。
- Project-level SSE notification foundation、heartbeat、stale-version 防护、reconnect Snapshot recovery。
- 结构化 backend logging 与三个逻辑 worker boundary placeholder。
- Foundation tests、clean-run validation、acceptance evidence 与 traceability 更新。

## Out of Scope

- CHANGE-002：Research Planner、Terra Provider、Prompt、Research Plan、Model Run 业务。
- CHANGE-003：MediaCrawler、Crawl Job/attempt、平台登录、采集控制、Source Content/Comment、Evidence。
- CHANGE-004：噪声过滤、Demand Signal、批处理、模型缓存/重试。
- CHANGE-005：Embedding、Micro Cluster、Cluster Curator、Demand Graph。
- CHANGE-006：Demand Score、score breakdown、Demand Snapshot、Trend。
- CHANGE-007：完整 Demand UX、Evidence Browser、下游 Dashboard 指标。
- CHANGE-008：Opportunity Lab。
- CHANGE-009：Report 与 Export。
- CHANGE-010：Gold Set 与 Evaluation 业务。
- V0.2：socai Deep Verify/OCR/转写、Trend Signal、CreatorOS 联动。
- 登录、会员、支付、多用户、团队权限、SaaS、移动端、自动外联/营销/发布、秒级全网监控、Kafka、微服务、Elasticsearch、Neo4j、GraphRAG、自建分析模型、多模型路由或由 LLM 生成产品/市场分数。

## Requirement Mapping

### Direct CHANGE-001 requirements

| Capability | Requirement IDs | Coverage |
|---|---|---|
| `application-foundation` | REQ-FOUNDATION-001, REQ-ARCH-002, REQ-ARCH-010 | Full for this Change; the two architecture baselines retain `SHOULD` strength. |
| `research-project` | REQ-DATA-001, REQ-PROJECT-013 | Full planned coverage. |
| `project-state` | REQ-PROJECT-009, REQ-PROJECT-010, REQ-PROJECT-011, REQ-PROJECT-016, REQ-PROJECT-017, REQ-GOVERNANCE-014 | Full planned coverage; REQ-PROJECT-009 remains `SHOULD`. |
| `dashboard` | REQ-PROJECT-014 | Full Foundation journey coverage. |
| `project-events` | REQ-SSE-001, REQ-SSE-002, REQ-SSE-003, REQ-SSE-004 | Full Project-level Foundation coverage. |

### Partial cross-Change coverage

| Requirement IDs | Foundation contribution | Completion rule |
|---|---|---|
| REQ-PROJECT-002 | Local Web/API/PostgreSQL runtime only; MediaCrawler comes in CHANGE-003. | `PARTIAL COVERAGE / FUTURE COMPLETION`; remains `UNIMPLEMENTED`. |
| REQ-PROJECT-008 | Creates only the Project aggregate root. | `PARTIAL COVERAGE / FUTURE COMPLETION`; AC-PROJECT-008 cannot pass before downstream associations exist. |
| REQ-PROJECT-018 | Implements only Project row soft-delete, ordinary list/get/Dashboard exclusion, repeat-delete semantics, and absence of physical cascade; CHANGE-001 creates no Source schema. | `PARTIAL COVERAGE / FUTURE COMPLETION`; AC-PROJECT-018 stays `UNIMPLEMENTED` until CHANGE-003 proves shared-Source retention with real PostgreSQL associations. |
| REQ-ARCH-001 | Audits the Foundation frontend dependency/import/bundle graph and keeps crawler process core, LLM judgment, clustering, and scoring out of the browser. | Foundation-scope STATIC evidence only; the multi-Change Requirement remains `UNIMPLEMENTED` until the future business owners exist and are audited. |
| REQ-UI-002 | Creates Foundation project cards without downstream metrics/actions. | `PARTIAL COVERAGE / FUTURE COMPLETION`; AC-UI-002 completes in CHANGE-007. |
| REQ-ARCH-003 | Creates three logical worker interfaces/registrations only. | `PARTIAL COVERAGE / FUTURE COMPLETION`; worker behaviors arrive in CHANGE-003–005. |
| REQ-ARCH-007, REQ-API-007 | Adds Project CRUD/Snapshot/events only. | `PARTIAL COVERAGE / FUTURE COMPLETION`; complete API/event catalogs remain future work. |
| REQ-ARCH-008 | Adds only indexes justified by the Foundation Project schema. | `PARTIAL COVERAGE / FUTURE COMPLETION`; remaining indexed domains arrive with their schemas. |
| REQ-ARCH-011, REQ-ARCH-012 | Enforces frontend/backend ownership for Foundation paths only. | `PARTIAL COVERAGE / FUTURE COMPLETION`; both rollups remain `UNIMPLEMENTED`. |
| REQ-RESILIENCE-007 | Establishes the backend structured-log schema; later jobs and UI events extend it. | `PARTIAL COVERAGE / FUTURE COMPLETION`; remains `UNIMPLEMENTED`. |

### Change gates

- Scope is gated by REQ-PROJECT-004..007, REQ-SCOPE-001..019, REQ-EVIDENCE-010, REQ-GOVERNANCE-005..006, REQ-UI-012, and REQ-UI-015. These prohibitions are audited but are not the business outcome of a Slice.
- Migration and implementation evidence are gated by REQ-GOVERNANCE-010..011 and REQ-GOVERNANCE-015. No implementation result exists in this planning-only round.
- REQ-API-008 and REQ-RESILIENCE-006 remain `SHOULD`; REQ-ARCH-013 and REQ-RESILIENCE-008 remain `MAY`.
- No OPEN/PROPOSED decision is promoted. DEC-003/006/007/008 are used exactly as `USER_CONFIRMED`; DEC-003 Crawl behavior remains CHANGE-003 scope.

## Acceptance Mapping

| Slice | Acceptance IDs | Planned conclusion |
|---|---|---|
| C001-S1 | AC-FOUNDATION-001, AC-ARCH-001 (Foundation scope) | Pinned/local-safe Web/API + PostgreSQL 18, health/readiness DB+schema-head integration, and frontend boundary audit. |
| C001-S2 | AC-DATA-001, AC-PROJECT-013; AC-PROJECT-018 partial only | Migration/schema, create/list/get/soft-delete, and Project restart persistence against PostgreSQL; no Source schema or shared-Source completion claim. |
| C001-S3 | AC-PROJECT-010, AC-PROJECT-016, AC-PROJECT-017, AC-GOVERNANCE-014 | Exhaustive 13×13 transition policy, failure/retry and terminal-state tests. |
| C001-S4 | AC-PROJECT-011, AC-PROJECT-014 | Playwright Web → API → PostgreSQL empty-project journey and backend-status rendering. |
| C001-S5 | AC-SSE-001..004 | Connect/Buffer/Snapshot/Reconcile, committed mutation versions, non-mutating heartbeat/control events, seven deterministic race cases, and real-SSE reconnect recovery. |
| C001-S6 | All fully executable items above plus AC-ARCH-001 and applicable scope/migration gates | Clean-run evidence, architecture audit, and traceability only; AC-PROJECT-018 retains partial evidence and `UNIMPLEMENTED`; no new feature. |

`AC-PROJECT-002`, `AC-PROJECT-008`, `AC-PROJECT-018`, `AC-UI-002`, `AC-ARCH-003`, `AC-ARCH-007`, `AC-ARCH-008`, `AC-ARCH-011`, `AC-ARCH-012`, `AC-API-007`, and `AC-RESILIENCE-007` receive only `PARTIAL COVERAGE / FUTURE COMPLETION` and MUST NOT be reported PASS by CHANGE-001. `AC-ARCH-001` receives a Foundation-scope STATIC result only; its global multi-Change Requirement remains `UNIMPLEMENTED`.

## Capabilities

### New Capabilities

- `application-foundation`: Executable local Web/API/PostgreSQL boundary, health/readiness, reproducible runtime, migration discipline, logging and logical worker boundaries.
- `research-project`: Minimal PostgreSQL-backed Project aggregate plus create/list/get/soft-delete and Snapshot contracts.
- `project-state`: Confirmed backend-owned Project vocabulary, transition policy, failure recovery and version mutation rules.
- `dashboard`: Empty-project creation and real Project presentation without fabricated downstream metrics.
- `project-events`: Versioned Project-level REST Snapshot + SSE notification and reconnect contract.

### Modified Capabilities

None. No main capability specs exist yet.

## Impact

- Planned areas: root workspace/config/docs, `apps/web`, `apps/api`, Alembic migrations, PostgreSQL runtime/test composition, Playwright and backend test suites.
- Planned API surface: `/health`, `/ready`, Project create/list/get/delete/Snapshot/command endpoints, and Project events SSE.
- Planned data impact: one Foundation `research_project` business table plus Alembic version metadata; no downstream business tables.
- Planned dependencies: Node.js 24.x LTS with pinned pnpm and `pnpm-lock.yaml`; CPython 3.11.x with uv/`uv.lock`; PostgreSQL 18.x with Psycopg 3 async; FastAPI/SQLAlchemy/Alembic; pytest/pytest-asyncio strict; and Playwright.
- This proposal changes planning artifacts only. It creates no runtime, schema, migration, API, UI, or test implementation.
