# Requirement Index

## Baseline record

| Field | Value |
|---|---|
| Canonical file | `docs/spec/NeedRadar_需求说明书_OpenSpec_v1.0.md` |
| Document version | v1.0 |
| Target stage | V0.1 local self-use |
| SHA-256 | `4a826baf65246dba140ab08872d1af1fd295ed95ecd6bb27d53f21509ecc7c1c` |
| Repository HEAD at baseline | `7f2272c1897aa694f1bf28af76d6214264070788` |
| Baseline established | `2026-09-27T19:51:06+08:00` |
| Baseline rule | Read-only. Codex must not automatically modify this file during implementation. |

The catalog below is an index, not a replacement or reinterpretation of the baseline. If a summary conflicts with the canonical file, the canonical file wins and the conflict must be reported. Requirement level preserves the source force: `MUST`, `MUST_NOT`, `SHOULD`, `MAY`. All items begin `UNIMPLEMENTED`; this is expected before development.

Requirement Kind distinguishes completion semantics: `ATOMIC` is independently implementable/verifiable, `SCOPE_GUARD` is a global prohibition, `ROLLUP` aggregates multiple stages and cannot PASS early, and `E2E` is a complete user-journey gate. Completion reporting must show all Requirements, mandatory ATOMIC Requirements, and ROLLUP/E2E gates separately so duplicated rollups do not inflate progress.

## Requirement catalog

| Requirement ID | Requirement Kind | Source Section | Level | Requirement Summary | Acceptance Required | Target Change | Status |
|---|---|---|---|---|---|---|---|
| REQ-PROJECT-001 | E2E | §2.1 | MUST | Complete the stated research-direction → plan → confirmed crawl → normalized Evidence → Signals → clusters → curated demands → programmatic score → map/evidence → opportunities → report loop. | AC-PROJECT-001 | CHANGE-001..010 | UNIMPLEMENTED |
| REQ-PROJECT-002 | ROLLUP | §3.1–3.2 | MUST | Operate as a local, single-user Web application on localhost with PostgreSQL and local MediaCrawler. | AC-PROJECT-002 | CHANGE-001/003 | UNIMPLEMENTED |
| REQ-PROJECT-003 | E2E | §3.2–3.3 | MUST | Cover every normal product operation in Web UI without requiring config edits, CLI, SQL, scripts, prompt edits, model selection, or manual API construction. | AC-PROJECT-003 | CHANGE-001..010 | UNIMPLEMENTED |
| REQ-PROJECT-004 | SCOPE_GUARD | §2.3, §3.1 | MUST_NOT | Do not add registration, login/membership/payment, multi-user, or team permission capabilities in V0.1. | AC-PROJECT-004 | ALL | UNIMPLEMENTED |
| REQ-PROJECT-005 | SCOPE_GUARD | §2.3 | MUST_NOT | Do not make V0.1 a SaaS cloud service, mobile app, or automated outreach/marketing/publishing/contact system. | AC-PROJECT-005 | ALL | UNIMPLEMENTED |
| REQ-PROJECT-006 | SCOPE_GUARD | §2.3 | MUST_NOT | Do not implement second-level whole-web monitoring, Kafka, microservices, Elasticsearch, Neo4j, or complex GraphRAG in V0.1. | AC-PROJECT-006 | ALL | UNIMPLEMENTED |
| REQ-PROJECT-007 | SCOPE_GUARD | §2.3, §36 | MUST_NOT | Do not build a self-hosted LLM/multi-model router or automatically estimate TAM/SAM/SOM, market score, blue-ocean score, or success probability. | AC-PROJECT-007 | ALL | UNIMPLEMENTED |
| REQ-PROJECT-008 | ROLLUP | §6.1 | MUST | A Research Project aggregates its question, target user, dimensions, queries, platforms, jobs, Evidence, Signals, Clusters, Opportunities, and report. Foundation establishes only the aggregate root; this Requirement remains UNIMPLEMENTED until all listed downstream associations exist. | AC-PROJECT-008 | CHANGE-001..009 | UNIMPLEMENTED |
| REQ-PROJECT-009 | ATOMIC | §22 | SHOULD | Use the suggested project states as the starting state vocabulary. | No | CHANGE-001 | UNIMPLEMENTED |
| REQ-PROJECT-010 | ATOMIC | §22 | MUST | Manage project state transitions centrally in the backend. | AC-PROJECT-010 | CHANGE-001 | UNIMPLEMENTED |
| REQ-PROJECT-011 | ATOMIC | §22 | MUST_NOT | Frontend must not infer project state. | AC-PROJECT-011 | CHANGE-001 | UNIMPLEMENTED |
| REQ-PROJECT-012 | ATOMIC | §22 | MAY | Allow `CRAWL_PARTIAL → ANALYZING_SIGNALS` when the user continues with partial data. | No | CHANGE-003/004 | UNIMPLEMENTED |
| REQ-PROJECT-013 | ATOMIC | §23.1 | MUST | Provide create/list/get/delete Project API capabilities; the concrete REST paths are suggested rather than mandatory. | AC-PROJECT-013 | CHANGE-001 | UNIMPLEMENTED |
| REQ-PROJECT-014 | E2E | §32 CHANGE-001 | MUST | Foundation completion lets a user create an empty Research Project and see its status in UI. | AC-PROJECT-014 | CHANGE-001 | UNIMPLEMENTED |
| REQ-PROJECT-015 | ATOMIC | §35 | MUST | Preserve the P0 → P1 → P2 priority order when resources are constrained. | AC-PROJECT-015 | PLAN | UNIMPLEMENTED |
| REQ-SCOPE-001 | SCOPE_GUARD | §2.3 | MUST_NOT | Do not implement multi-user registration in V0.1. | AC-SCOPE-001 | ALL | UNIMPLEMENTED |
| REQ-SCOPE-002 | SCOPE_GUARD | §2.3 | MUST_NOT | Do not implement login in V0.1. | AC-SCOPE-002 | ALL | UNIMPLEMENTED |
| REQ-SCOPE-003 | SCOPE_GUARD | §2.3 | MUST_NOT | Do not implement membership in V0.1. | AC-SCOPE-003 | ALL | UNIMPLEMENTED |
| REQ-SCOPE-004 | SCOPE_GUARD | §2.3 | MUST_NOT | Do not implement payment/billing in V0.1. | AC-SCOPE-004 | ALL | UNIMPLEMENTED |
| REQ-SCOPE-005 | SCOPE_GUARD | §2.3 | MUST_NOT | Do not implement team permissions in V0.1. | AC-SCOPE-005 | ALL | UNIMPLEMENTED |
| REQ-SCOPE-006 | SCOPE_GUARD | §2.3 | MUST_NOT | Do not implement a SaaS cloud service in V0.1. | AC-SCOPE-006 | ALL | UNIMPLEMENTED |
| REQ-SCOPE-007 | SCOPE_GUARD | §2.3 | MUST_NOT | Do not implement a mobile App in V0.1. | AC-SCOPE-007 | ALL | UNIMPLEMENTED |
| REQ-SCOPE-008 | SCOPE_GUARD | §2.3 | MUST_NOT | Do not automatically send private messages to users. | AC-SCOPE-008 | ALL | UNIMPLEMENTED |
| REQ-SCOPE-009 | SCOPE_GUARD | §2.3 | MUST_NOT | Do not implement automatic marketing. | AC-SCOPE-009 | ALL | UNIMPLEMENTED |
| REQ-SCOPE-010 | SCOPE_GUARD | §2.3 | MUST_NOT | Do not automatically publish social content. | AC-SCOPE-010 | ALL | UNIMPLEMENTED |
| REQ-SCOPE-011 | SCOPE_GUARD | §2.3 | MUST_NOT | Do not automatically contact potential customers. | AC-SCOPE-011 | ALL | UNIMPLEMENTED |
| REQ-SCOPE-012 | SCOPE_GUARD | §2.3 | MUST_NOT | Do not implement real-time second-level whole-web monitoring. | AC-SCOPE-012 | ALL | UNIMPLEMENTED |
| REQ-SCOPE-013 | SCOPE_GUARD | §2.3 | MUST_NOT | Do not introduce Kafka in V0.1. | AC-SCOPE-013 | ALL | UNIMPLEMENTED |
| REQ-SCOPE-014 | SCOPE_GUARD | §2.3 | MUST_NOT | Do not split V0.1 into microservices. | AC-SCOPE-014 | ALL | UNIMPLEMENTED |
| REQ-SCOPE-015 | SCOPE_GUARD | §2.3 | MUST_NOT | Do not introduce Elasticsearch in V0.1. | AC-SCOPE-015 | ALL | UNIMPLEMENTED |
| REQ-SCOPE-016 | SCOPE_GUARD | §2.3 | MUST_NOT | Do not introduce Neo4j in V0.1. | AC-SCOPE-016 | ALL | UNIMPLEMENTED |
| REQ-SCOPE-017 | SCOPE_GUARD | §2.3 | MUST_NOT | Do not implement complex GraphRAG in V0.1. | AC-SCOPE-017 | ALL | UNIMPLEMENTED |
| REQ-SCOPE-018 | SCOPE_GUARD | §2.3 | MUST_NOT | Do not self-host/build an analysis LLM or implement multi-model routing in V0.1. | AC-SCOPE-018 | ALL | UNIMPLEMENTED |
| REQ-SCOPE-019 | SCOPE_GUARD | §2.3 | MUST_NOT | Do not automatically estimate TAM/SAM/SOM or let an LLM directly output market/blue-ocean/success scores. | AC-SCOPE-019 | ALL | UNIMPLEMENTED |
| REQ-PLANNER-001 | ATOMIC | §8.1 | MUST | Planner input requires `query` and permits optional `context`. | AC-PLANNER-001 | CHANGE-002 | UNIMPLEMENTED |
| REQ-PLANNER-002 | ATOMIC | §8.2 | MUST | Terra High outputs a structured JSON research plan. | AC-PLANNER-002 | CHANGE-002 | UNIMPLEMENTED |
| REQ-PLANNER-003 | ATOMIC | §8.3 | MUST | Support at least DOMAIN, WORKFLOW, PAIN, REQUEST, PAYMENT, and COMPETITOR keyword groups. | AC-PLANNER-003 | CHANGE-002 | UNIMPLEMENTED |
| REQ-PLANNER-004 | ATOMIC | §8.3 | MAY | Later add ALTERNATIVE, ABANDON, PRICE, BEGINNER, and ADVANCED keyword types. | No | Future | UNIMPLEMENTED |
| REQ-PLANNER-005 | ATOMIC | §7.3, §8.4 | MUST | Present the plan as an editable structure including target, goal, dimensions, keyword tree, platforms, depth, time range, and estimated jobs. | AC-PLANNER-005 | CHANGE-002 | UNIMPLEMENTED |
| REQ-PLANNER-006 | ATOMIC | §7.3, §8.4 | MUST | Do not start crawl or create Crawl Jobs until the user confirms and starts the plan. | AC-PLANNER-006 | CHANGE-002 | UNIMPLEMENTED |
| REQ-PLANNER-007 | ATOMIC | §8.4 | MUST_NOT | Do not treat keywords as validated demands or return only 3–5 generic terms. | AC-PLANNER-007 | CHANGE-002 | UNIMPLEMENTED |
| REQ-PLANNER-008 | ATOMIC | §8.4 | MUST | Include keyword strategy for pain, help-seeking, price, and alternatives. | AC-PLANNER-008 | CHANGE-002 | UNIMPLEMENTED |
| REQ-CRAWL-001 | ATOMIC | §9.1 | SHOULD | V0.1 UI supports xhs, dy, ks, bili, wb, tieba, and zhihu MediaCrawler platforms. | No | CHANGE-003 | UNIMPLEMENTED |
| REQ-CRAWL-002 | ATOMIC | §9.1 | SHOULD | Default selected platforms are xhs, dy, bili, and zhihu. | No | CHANGE-002/003 | UNIMPLEMENTED |
| REQ-CRAWL-003 | ATOMIC | §9.2 | MUST | Create an independent Crawl Job per selected platform under a Research Project. | AC-CRAWL-003 | CHANGE-003 | UNIMPLEMENTED |
| REQ-CRAWL-004 | ATOMIC | §9.2 | SHOULD | Begin from the suggested Crawl Job state vocabulary. | No | CHANGE-003 | UNIMPLEMENTED |
| REQ-CRAWL-005 | ATOMIC | §9.3 | MUST | Persist each platform job's keywords, crawler type, limits, comment flags, start page, and lifecycle timestamps. | AC-CRAWL-005 | CHANGE-003 | UNIMPLEMENTED |
| REQ-CRAWL-006 | ATOMIC | §9.4 | MUST | Default global MediaCrawler concurrency to 1 and queue multiple platforms. | AC-CRAWL-006 | CHANGE-003 | UNIMPLEMENTED |
| REQ-CRAWL-007 | ATOMIC | §9.4 | MUST | Show users platform queue order. | AC-CRAWL-007 | CHANGE-003 | UNIMPLEMENTED |
| REQ-CRAWL-008 | ATOMIC | §9.4, §25.1 | MUST | Isolate a platform failure so it does not automatically fail the Project or discard other platform data. | AC-CRAWL-008 | CHANGE-003 | UNIMPLEMENTED |
| REQ-CRAWL-009 | ATOMIC | §9.4, §25.1 | MUST | Retain already collected Evidence and permit partial-success data to continue into analysis. | AC-CRAWL-009 | CHANGE-003/004 | UNIMPLEMENTED |
| REQ-CRAWL-010 | ATOMIC | §9.5 | MUST | Enter LOGIN_REQUIRED, visibly prompt the user, and allow continue/re-detect when interactive login is required. | AC-CRAWL-010 | CHANGE-003 | UNIMPLEMENTED |
| REQ-CRAWL-011 | ATOMIC | §9.5 | MUST_NOT | Do not fail silently when login is required. | AC-CRAWL-011 | CHANGE-003 | UNIMPLEMENTED |
| REQ-CRAWL-012 | ATOMIC | §7.4 | MUST | Per platform show state, keyword, completed keywords, content/comment/error counts, phase, recent log, and login requirement. | AC-CRAWL-012 | CHANGE-003 | UNIMPLEMENTED |
| REQ-CRAWL-013 | ATOMIC | §7.4 | MUST | Let users retry a failed platform, skip a platform, stop unfinished work, and continue downstream analysis with existing data. | AC-CRAWL-013 | CHANGE-003 | UNIMPLEMENTED |
| REQ-CRAWL-014 | ATOMIC | §33 Then 2 | MUST | Starting research from UI creates jobs, invokes MediaCrawler in background, streams progress, and persists Source Content/Comment. | AC-CRAWL-014 | CHANGE-003 | UNIMPLEMENTED |
| REQ-EVIDENCE-001 | ATOMIC | §9.6 | MUST | Enforce uniqueness for platform+content ID and platform+comment ID, including content ID when platform comment IDs are not global. | AC-EVIDENCE-001 | CHANGE-003 | UNIMPLEMENTED |
| REQ-EVIDENCE-002 | ATOMIC | §10.1 | MUST | Normalize Source Content with all listed fields and retain raw payload. | AC-EVIDENCE-002 | CHANGE-003 | UNIMPLEMENTED |
| REQ-EVIDENCE-003 | ATOMIC | §10.2 | MUST | Normalize Source Comment with all listed fields, parent relationship, source keyword, and raw payload. | AC-EVIDENCE-003 | CHANGE-003 | UNIMPLEMENTED |
| REQ-EVIDENCE-004 | ATOMIC | §10.1 | MUST_NOT | Do not encode an unavailable platform metric as zero; store it as NULL. | AC-EVIDENCE-004 | CHANGE-003 | UNIMPLEMENTED |
| REQ-EVIDENCE-005 | ATOMIC | §9.6, §21.12 | MUST | Reuse a source item collected by multiple projects while preserving explicit project associations; do not duplicate source data. | AC-EVIDENCE-005 | CHANGE-003 | UNIMPLEMENTED |
| REQ-EVIDENCE-006 | ATOMIC | §10.3, §34.12 | MUST | Assign every analyzed Evidence a stable internal ID and never use raw text as its unique key. | AC-EVIDENCE-006 | CHANGE-003 | UNIMPLEMENTED |
| REQ-EVIDENCE-007 | ATOMIC | §6.2, §34.3 | MUST | Every demand conclusion is traceable through Evidence to its original post/comment. | AC-EVIDENCE-007 | CHANGE-004..009 | UNIMPLEMENTED |
| REQ-EVIDENCE-008 | ATOMIC | §7.7 | MUST | Evidence Browser supports platform, source kind, Signal Type, Cluster, time, likes, keyword, and raw-text filters/search. | AC-EVIDENCE-008 | CHANGE-007 | UNIMPLEMENTED |
| REQ-EVIDENCE-009 | ATOMIC | §7.7 | MUST | Evidence rows expose the listed IDs, provenance, creator/time/likes/text/URL/query, Signals, and Cluster. | AC-EVIDENCE-009 | CHANGE-007 | UNIMPLEMENTED |
| REQ-EVIDENCE-010 | ATOMIC | §31.1 | MUST_NOT | Do not implement V0.2 socai deep verify/OCR/transcription in V0.1. | AC-EVIDENCE-010 | ALL | UNIMPLEMENTED |
| REQ-SIGNAL-001 | ATOMIC | §11 | MUST | Run deterministic no-model noise filtering before Terra extraction. | AC-SIGNAL-001 | CHANGE-004 | UNIMPLEMENTED |
| REQ-SIGNAL-002 | ATOMIC | §11.1 | MUST | Filter the enumerated empty/emoji/@/numeric/low-information/duplicate/spam/short-without-demand-keyword inputs. | AC-SIGNAL-002 | CHANGE-004 | UNIMPLEMENTED |
| REQ-SIGNAL-003 | ATOMIC | §11.2 | MUST | Preserve short strong-demand phrases through a configurable demand-term allowlist. | AC-SIGNAL-003 | CHANGE-004 | UNIMPLEMENTED |
| REQ-SIGNAL-004 | ATOMIC | §11.3 | MUST | Store `filtered`, `filter_reason`, and `filter_version`. | AC-SIGNAL-004 | CHANGE-004 | UNIMPLEMENTED |
| REQ-SIGNAL-005 | ATOMIC | §12.2 | MUST | Support all 16 listed V0.1 Signal Types, allowing multiple types per Evidence. | AC-SIGNAL-005 | CHANGE-004 | UNIMPLEMENTED |
| REQ-SIGNAL-006 | ATOMIC | §12.3–12.7 | MUST | Produce the listed Demand Signal schema and fixed pain, recurrence, payment, and existing-solution-sentiment enums. | AC-SIGNAL-006 | CHANGE-004 | UNIMPLEMENTED |
| REQ-SIGNAL-007 | ATOMIC | §12.8 | MUST | Extract only from current Evidence, quote original text, and explicitly emit `is_demand=false` when appropriate. | AC-SIGNAL-007 | CHANGE-004 | UNIMPLEMENTED |
| REQ-SIGNAL-008 | ATOMIC | §12.8 | MUST_NOT | Do not invent payment intent, infer willingness to pay from negativity, or force ordinary interest/praise into a demand. | AC-SIGNAL-008 | CHANGE-004 | UNIMPLEMENTED |
| REQ-SIGNAL-009 | ATOMIC | §12.8, §25.3 | MUST | Require strict JSON; repair parse failures, retry the model, then mark Model Run FAILED without fake Signals if still invalid. | AC-SIGNAL-009 | CHANGE-004 | UNIMPLEMENTED |
| REQ-SIGNAL-010 | ATOMIC | §12.9 | MUST_NOT | Do not issue one model API call per comment. | AC-SIGNAL-010 | CHANGE-004 | UNIMPLEMENTED |
| REQ-SIGNAL-011 | ATOMIC | §12.9 | SHOULD | Batch 40–100 Evidence by default, shrink to token/character budget, maintain one-to-one IDs, and retry missing outputs. | No | CHANGE-004 | UNIMPLEMENTED |
| REQ-SIGNAL-012 | ATOMIC | §12.10, §27.3 | MUST | Hash prompt/model/reasoning/Evidence IDs/text hashes and avoid duplicate model calls for identical input. | AC-SIGNAL-012 | CHANGE-004 | UNIMPLEMENTED |
| REQ-SIGNAL-013 | ATOMIC | §12.10, §27.3 | MUST | Permit an explicit user-forced reanalysis to bypass cache without overwriting history. | AC-SIGNAL-013 | CHANGE-004 | UNIMPLEMENTED |
| REQ-CLUSTER-001 | ATOMIC | §13.1 | MUST_NOT | Do not embed only the raw full comment text. | AC-CLUSTER-001 | CHANGE-005 | UNIMPLEMENTED |
| REQ-CLUSTER-002 | ATOMIC | §13.1 | SHOULD | Embed the normalized Demand Atom fields listed in the baseline. | No | CHANGE-005 | UNIMPLEMENTED |
| REQ-CLUSTER-003 | ATOMIC | §13.2 | MAY | Reuse/reference DeepPoint Embedding, cosine, and DBSCAN algorithms. | No | CHANGE-005 | UNIMPLEMENTED |
| REQ-CLUSTER-004 | ATOMIC | §13.2 | MUST | Encapsulate clustering behind a `ClusteringProvider`. | AC-CLUSTER-004 | CHANGE-005 | UNIMPLEMENTED |
| REQ-CLUSTER-005 | ATOMIC | §13.3 | MUST_NOT | Above the configured large-data threshold, do not allocate a huge NxN distance matrix. | AC-CLUSTER-005 | CHANGE-005 | UNIMPLEMENTED |
| REQ-CLUSTER-006 | ATOMIC | §13.3 | MUST | Use a memory-efficient/hierarchical path or enforce and visibly disclose a V0.1 per-run cluster limit. | AC-CLUSTER-006 | CHANGE-005 | UNIMPLEMENTED |
| REQ-CLUSTER-007 | ATOMIC | §14 | MUST | After micro-clustering, Terra High curates merge/split/name/parent-child and semantic distinctions. | AC-CLUSTER-007 | CHANGE-005 | UNIMPLEMENTED |
| REQ-CLUSTER-008 | ATOMIC | §14 | MUST_NOT | Cluster Curator must not delete/modify Evidence, invent Signals, or generate final Demand Score. | AC-CLUSTER-008 | CHANGE-005 | UNIMPLEMENTED |
| REQ-CLUSTER-009 | ATOMIC | §14 | MUST | Persist a Model Run for every curator merge/split operation. | AC-CLUSTER-009 | CHANGE-005 | UNIMPLEMENTED |
| REQ-CLUSTER-010 | ATOMIC | §15, §34.8 | MUST | Store listed Cluster fields and a many-to-many Cluster–Signal relation without copying or dropping Signal/Evidence. | AC-CLUSTER-010 | CHANGE-005 | UNIMPLEMENTED |
| REQ-SCORE-001 | ATOMIC | §16.1 | MUST | Compute Demand Score programmatically on 0–100, make it explainable/versioned, and expose missing data rather than silently using zero. | AC-SCORE-001 | CHANGE-006 | UNIMPLEMENTED |
| REQ-SCORE-002 | ATOMIC | §16.2 | MUST | Use the eight stated dimensions and weights totaling 100. | AC-SCORE-002 | CHANGE-006 | UNIMPLEMENTED |
| REQ-SCORE-003 | ATOMIC | §16.3 | SHOULD | Breadth uses signal and unique-creator counts with project P95/log1p normalization; P95≤0 is insufficient data. | No | CHANGE-006 | UNIMPLEMENTED |
| REQ-SCORE-004 | ATOMIC | §16.4 | MUST | Apply the stated recurrence mappings, exclude UNKNOWN, and scale valid weighted mean to 15. | AC-SCORE-004 | CHANGE-006 | UNIMPLEMENTED |
| REQ-SCORE-005 | ATOMIC | §16.5 | MUST | Apply stated pain mappings and scale valid weighted mean to 15. | AC-SCORE-005 | CHANGE-006 | UNIMPLEMENTED |
| REQ-SCORE-006 | ATOMIC | §16.6 | MUST | Workaround dimension uses only listed qualifying Signal Types plus signal/unique-creator counts, normalized to max 10. | AC-SCORE-006 | CHANGE-006 | UNIMPLEMENTED |
| REQ-SCORE-007 | ATOMIC | §16.7 | MUST | Payment uses only explicit listed payment mappings plus signal/creator counts, normalized to max 15. | AC-SCORE-007 | CHANGE-006 | UNIMPLEMENTED |
| REQ-SCORE-008 | ATOMIC | §16.7, §34.5 | MUST_NOT | Do not score payment intent from Terra's subjective inference without an original payment Signal. | AC-SCORE-008 | CHANGE-006 | UNIMPLEMENTED |
| REQ-SCORE-009 | ATOMIC | §16.8 | MUST | Unsatisfied-solution dimension uses only listed complaint/switch Signals and negative/switching sentiment, max 10. | AC-SCORE-009 | CHANGE-006 | UNIMPLEMENTED |
| REQ-SCORE-010 | ATOMIC | §16.9 | MUST | Trend uses Snapshots for 7/30/90 days; insufficient history is disclosed and the dimension removed, not scored zero. | AC-SCORE-010 | CHANGE-006 | UNIMPLEMENTED |
| REQ-SCORE-011 | ATOMIC | §16.10 | SHOULD | Cross-platform uses the suggested 1/2/3/4+ mapping scaled to 5. | No | CHANGE-006 | UNIMPLEMENTED |
| REQ-SCORE-012 | ATOMIC | §16.11 | MUST | Remove missing dimensions, proportionally rescale remaining weights to 100, and show which dimensions contributed. | AC-SCORE-012 | CHANGE-006 | UNIMPLEMENTED |
| REQ-SCORE-013 | ATOMIC | §16.12 | MUST_NOT | Do not overwrite historical scores after a formula change; save `score_version="v1"`. | AC-SCORE-013 | CHANGE-006 | UNIMPLEMENTED |
| REQ-DEMAND-001 | ATOMIC | §7.5 | MUST | Demand overview shows Evidence, valid Signal, unique creator, Cluster, and platform counts. | AC-DEMAND-001 | CHANGE-007 | UNIMPLEMENTED |
| REQ-DEMAND-002 | ATOMIC | §7.5 | MUST | Demand list exposes all listed score/count/coverage/trend/payment/workaround/status fields. | AC-DEMAND-002 | CHANGE-007 | UNIMPLEMENTED |
| REQ-DEMAND-003 | ATOMIC | §7.5 | MUST | Demand list supports sorting plus platform, score, Signal Type, search, and time filters. | AC-DEMAND-003 | CHANGE-007 | UNIMPLEMENTED |
| REQ-DEMAND-004 | ATOMIC | §7.5 | MUST | Demand map/grouped view shows primary topic, child demand, score, scale, and trend. | AC-DEMAND-004 | CHANGE-007 | UNIMPLEMENTED |
| REQ-DEMAND-005 | ATOMIC | §7.6 | MUST | Demand detail exposes all 20 listed facts/actions including breakdown, context, workaround/payment, quotes, URLs, children, and opportunity action. | AC-DEMAND-005 | CHANGE-007 | UNIMPLEMENTED |
| REQ-DEMAND-006 | ATOMIC | §18 | MUST | Demand Analyst receives all listed evidence/statistical inputs and produces all listed explanations, uncertainty, and Evidence IDs. | AC-DEMAND-006 | CHANGE-007 | UNIMPLEMENTED |
| REQ-DEMAND-007 | ATOMIC | §17 | MUST | Save listed Demand Snapshot fields on completion/manual refresh and expose 7/30/90-day changes, first seen, and growth direction. | AC-DEMAND-007 | CHANGE-006 | UNIMPLEMENTED |
| REQ-DEMAND-008 | ATOMIC | §17 | MAY | V0.1 may keep semantically similar demands separate across Research Projects; global identity is deferred. | No | Future | UNIMPLEMENTED |
| REQ-OPPORTUNITY-001 | ATOMIC | §6.5 | MUST | Support Product and Content Opportunity types, each referencing one or more Demand Clusters. | AC-OPPORTUNITY-001 | CHANGE-008 | UNIMPLEMENTED |
| REQ-OPPORTUNITY-002 | ATOMIC | §19.1 | MUST | Run product opportunity analysis only after an explicit user click. | AC-OPPORTUNITY-002 | CHANGE-008 | UNIMPLEMENTED |
| REQ-OPPORTUNITY-003 | ATOMIC | §19.1 | MUST_NOT | Do not automatically run Terra for opportunities across every demand. | AC-OPPORTUNITY-003 | CHANGE-008 | UNIMPLEMENTED |
| REQ-OPPORTUNITY-004 | ATOMIC | §19.2 | MUST | Product Opportunity input includes the listed cluster/score/evidence/payment/workaround/solution/trend/personal-constraint context. | AC-OPPORTUNITY-004 | CHANGE-008 | UNIMPLEMENTED |
| REQ-OPPORTUNITY-005 | ATOMIC | §19.3 | MUST_NOT | Personal developer constraints affect Opportunity analysis only, never Demand Score. | AC-OPPORTUNITY-005 | CHANGE-008 | UNIMPLEMENTED |
| REQ-OPPORTUNITY-006 | ATOMIC | §19.4–19.5 | MUST | Product and Content Opportunity outputs contain every listed field/topic and Evidence references. | AC-OPPORTUNITY-006 | CHANGE-008 | UNIMPLEMENTED |
| REQ-OPPORTUNITY-007 | ATOMIC | §19.5 | MUST_NOT | Do not equate topic heat with product-worthiness. | AC-OPPORTUNITY-007 | CHANGE-008 | UNIMPLEMENTED |
| REQ-REPORT-001 | ATOMIC | §7.9 | MUST | Compose the report from scope, quality/coverage, demand categories, opportunities, limitations, and Evidence citations. | AC-REPORT-001 | CHANGE-009 | UNIMPLEMENTED |
| REQ-REPORT-002 | ATOMIC | §2.2, §7.9, §29 | MUST | Export the research report as Markdown and export tabular research data as CSV and/or Excel per the unresolved baseline wording. | AC-REPORT-002 | CHANGE-009 | UNIMPLEMENTED |
| REQ-REPORT-003 | ATOMIC | §29.2 | MUST | Table export provides Demands, Signals, and Evidence datasets with all listed columns. | AC-REPORT-003 | CHANGE-009 | UNIMPLEMENTED |
| REQ-REPORT-004 | ATOMIC | §7.9 | MAY | Defer PDF export to V0.2. | No | Future | UNIMPLEMENTED |
| REQ-REPORT-005 | ATOMIC | §23.8 | MUST | Provide get/regenerate report and Markdown/table export API capabilities; the concrete REST paths are suggested rather than mandatory. | AC-REPORT-005 | CHANGE-009 | UNIMPLEMENTED |
| REQ-MODELRUN-001 | ROLLUP | §20 | MUST | Persist a Model Run for every Terra High call. | AC-MODELRUN-001 | CHANGE-002/004/005/007/008/009 | UNIMPLEMENTED |
| REQ-MODELRUN-002 | ATOMIC | §20 | MUST | Store all listed Model Run provenance, payload, token, status/error, and timing fields. | AC-MODELRUN-002 | CHANGE-002/004 | UNIMPLEMENTED |
| REQ-MODELRUN-003 | ROLLUP | §20 | MUST | Support all six listed run types. | AC-MODELRUN-003 | CHANGE-002..009 | UNIMPLEMENTED |
| REQ-MODELRUN-004 | ATOMIC | §20 | MUST | Support viewing failures, retry, forced rerun, and Prompt-version comparison. | AC-MODELRUN-004 | CHANGE-004 | UNIMPLEMENTED |
| REQ-MODELRUN-005 | ROLLUP | §26 | MUST | Version/trace Research Plan, Prompt, extractor, clustering, curator, score formula, and Opportunity outputs. | AC-MODELRUN-005 | CHANGE-002..009 | UNIMPLEMENTED |
| REQ-MODELRUN-006 | ATOMIC | §26, §34.13 | MUST_NOT | Reanalysis must not overwrite an old Model Run or destroy version traceability. | AC-MODELRUN-006 | CHANGE-004 | UNIMPLEMENTED |
| REQ-UI-001 | ROLLUP | §7 | MUST | Provide all ten listed V0.1 route/page capabilities. | AC-UI-001 | CHANGE-001..009 | UNIMPLEMENTED |
| REQ-UI-002 | ROLLUP | §7.1 | MUST | Dashboard and project cards expose every listed project metric/action. | AC-UI-002 | CHANGE-001/007 | UNIMPLEMENTED |
| REQ-UI-003 | ATOMIC | §7.2 | MUST | New Research accepts a research question/direction and optional context, then enters Planner generation. | AC-UI-003 | CHANGE-002 | UNIMPLEMENTED |
| REQ-UI-004 | ATOMIC | §7.3 | MUST | Plan UI permits add/delete/edit/enable keywords, platform toggles, crawl limits, and sub-comment toggle. | AC-UI-004 | CHANGE-002 | UNIMPLEMENTED |
| REQ-UI-005 | ATOMIC | §7.4 | MUST | Collection UI provides required progress, login, retry, skip, stop, and partial-continue interactions. | AC-UI-005 | CHANGE-003 | UNIMPLEMENTED |
| REQ-UI-006 | ATOMIC | §7.5 | MUST | Demand overview provides statistics, list, filters, and map. | AC-UI-006 | CHANGE-007 | UNIMPLEMENTED |
| REQ-UI-007 | ATOMIC | §7.6 | MUST | Demand detail provides the listed explanation, evidence, score, children, and opportunity controls. | AC-UI-007 | CHANGE-007 | UNIMPLEMENTED |
| REQ-UI-008 | ATOMIC | §7.7 | MUST | Evidence UI exposes required filters and complete provenance. | AC-UI-008 | CHANGE-007 | UNIMPLEMENTED |
| REQ-UI-009 | ATOMIC | §7.8 | MUST | Opportunity Lab separates product/content opportunities and displays all listed product fields. | AC-UI-009 | CHANGE-008 | UNIMPLEMENTED |
| REQ-UI-010 | ROLLUP | §7.10 | MUST | Settings shows read-only GPT-5.6 Terra/high information, the seven platform states, and Content/Comment/Demand Signal/Demand Cluster/Model Run counts. | AC-UI-010 | CHANGE-001..009 | UNIMPLEMENTED |
| REQ-UI-011 | ROLLUP | §24.3 | MUST | Any multi-second task shows phase, completed/failed counts, current operation, and cancellable/retry state. | AC-UI-011 | CHANGE-001..009 | UNIMPLEMENTED |
| REQ-UI-012 | SCOPE_GUARD | §24.3 | MUST_NOT | Do not represent a long-running task only with an infinite spinner. | AC-UI-012 | CHANGE-001..009 | UNIMPLEMENTED |
| REQ-UI-013 | ROLLUP | §24.4 | MUST | Visually distinguish measured data from AI analysis and label analysis `Terra High 分析`. | AC-UI-013 | CHANGE-007/008/009 | UNIMPLEMENTED |
| REQ-UI-014 | ATOMIC | §24.1 | MUST | Make key numbers clickable to their composition and preserve an evidence → demand → opportunity information hierarchy. | AC-UI-014 | CHANGE-007 | UNIMPLEMENTED |
| REQ-UI-015 | SCOPE_GUARD | §24.1, §34.9 | MUST_NOT | Do not use a chat-box-centered or single-input/single-table UI in place of the complete visual workflow. | AC-UI-015 | CHANGE-001..009 | UNIMPLEMENTED |
| REQ-UI-016 | ATOMIC | §4.4, §7.10, §34.10 | MUST_NOT | Do not expose ordinary-user model switching or multi-model routing; show product runtime model read-only. | AC-UI-016 | CHANGE-002 | UNIMPLEMENTED |
| REQ-UI-017 | ATOMIC | §27.1 | MUST | Paginate or virtualize large lists and never render tens of thousands of Evidence rows in the DOM at once. | AC-UI-017 | CHANGE-007 | UNIMPLEMENTED |
| REQ-UI-018 | ATOMIC | §27.1 | SHOULD | Page transitions provide immediate feedback. | No | CHANGE-001..009 | UNIMPLEMENTED |
| REQ-RESILIENCE-001 | ATOMIC | §25.1, §34.6/14 | MUST_NOT | Never translate crawl failure/partial failure into “no demand” or discard the entire research. | AC-RESILIENCE-001 | CHANGE-003 | UNIMPLEMENTED |
| REQ-RESILIENCE-002 | ATOMIC | §25.2 | MUST | Preserve successful model batches, retry failed batches up to configured limit, store errors, and allow UI manual retry. | AC-RESILIENCE-002 | CHANGE-004 | UNIMPLEMENTED |
| REQ-RESILIENCE-003 | ATOMIC | §25.3, §34.7 | MUST_NOT | Never manufacture a default “Medium” conclusion or fake Signal after JSON failure. | AC-RESILIENCE-003 | CHANGE-004 | UNIMPLEMENTED |
| REQ-RESILIENCE-004 | ATOMIC | §25.4, §34.15 | MUST | Demand Detail exposes sample size, coverage, missing platforms, time span, and missing score dimensions. | AC-RESILIENCE-004 | CHANGE-006/007 | UNIMPLEMENTED |
| REQ-RESILIENCE-005 | ATOMIC | §25.4 | MUST_NOT | Do not equate small/insufficient samples with absence of demand. | AC-RESILIENCE-005 | CHANGE-006/007 | UNIMPLEMENTED |
| REQ-RESILIENCE-006 | ATOMIC | §23.9 | SHOULD | Provide SSE for listed project/job/progress/error/login events. | No | CHANGE-001/003 | UNIMPLEMENTED |
| REQ-RESILIENCE-007 | ROLLUP | §28 | MUST | Backend logs contain timestamp, project/job IDs, stage, level, message, and metadata; UI shows simplified events. | AC-RESILIENCE-007 | CHANGE-001..004 | UNIMPLEMENTED |
| REQ-EVAL-001 | ATOMIC | §30.1 | MUST | Maintain `evals/gold_set/` with manually labeled social comments and all listed fields. | AC-EVAL-001 | CHANGE-010 | UNIMPLEMENTED |
| REQ-EVAL-002 | ATOMIC | §30.2 | MUST | Evaluate demand precision/recall, payment precision/recall, Signal Type F1, JSON success, cluster purity, and merge accuracy. | AC-EVAL-002 | CHANGE-010 | UNIMPLEMENTED |
| REQ-EVAL-003 | ATOMIC | §30.3 | MUST | Run Gold Set regression before deploying any major Demand Signal Prompt change. | AC-EVAL-003 | CHANGE-010 | UNIMPLEMENTED |
| REQ-EVAL-004 | E2E | §33 | MUST | Use “AI漫剧创作者有什么真实需求？” as the mandatory end-to-end acceptance scenario covering all eight Then stages without CLI. | AC-EVAL-004 | CHANGE-010 | UNIMPLEMENTED |
| REQ-ARCH-001 | ATOMIC | §4.1 | MUST_NOT | Frontend must not own MediaCrawler process core, LLM judgment, clustering, or scoring. | AC-ARCH-001 | CHANGE-001..006 | UNIMPLEMENTED |
| REQ-ARCH-002 | ATOMIC | §4.2 | SHOULD | Use the suggested Python/FastAPI/SQLAlchemy/Alembic/PostgreSQL/pgvector-or-equivalent backend baseline. | No | CHANGE-001 | UNIMPLEMENTED |
| REQ-ARCH-003 | ROLLUP | §4.3 | MUST | Separate crawler, analysis, and clustering as three logical workers; they may share a process group in V0.1. | AC-ARCH-003 | CHANGE-001/003..005 | UNIMPLEMENTED |
| REQ-ARCH-004 | ROLLUP | §4.4 | MUST | Use only GPT-5.6 Terra with high reasoning for every listed semantic analysis task; product runtime is backend-configured. | AC-ARCH-004 | CHANGE-002/004/005/007/008/009 | UNIMPLEMENTED |
| REQ-ARCH-005 | ATOMIC | §4.5 | MUST | Abstract Embedding as `EmbeddingProvider` and restrict it to vectorization/similarity/micro-clustering. | AC-ARCH-005 | CHANGE-005 | UNIMPLEMENTED |
| REQ-ARCH-006 | ATOMIC | §4.5 | MUST_NOT | Embeddings must not judge payment, market size, product worth, or final business conclusions. | AC-ARCH-006 | CHANGE-005 | UNIMPLEMENTED |
| REQ-ARCH-007 | ROLLUP | §23 | MUST | Cover all Project/Planner/Crawl/Analysis/Demand/Evidence/Opportunity/Report/Event API capabilities; exact concrete paths remain suggested. | AC-ARCH-007 | CHANGE-001..009 | UNIMPLEMENTED |
| REQ-ARCH-008 | ROLLUP | §27.2 | MUST | Index project_id, platform, platform content/comment IDs, creator hash, publish time, Signal Type, Cluster ID, and score in PostgreSQL. | AC-ARCH-008 | CHANGE-001..007 | UNIMPLEMENTED |
| REQ-ARCH-009 | ATOMIC | §27.4 | MUST | Start with crawler concurrency 1, clustering concurrency 1, and configurable analysis concurrency. | AC-ARCH-009 | CHANGE-003..005 | UNIMPLEMENTED |
| REQ-PROJECT-016 | ATOMIC | DEC-006 | MUST | Use the confirmed 13-state Research Project vocabulary and transition graph; backend rejects every unlisted transition and exhaustive transition tests cover all state pairs. | AC-PROJECT-016 | CHANGE-001 | UNIMPLEMENTED |
| REQ-PROJECT-017 | ATOMIC | DEC-006 | MUST | FAILED records `failed_from_status`; retry returns only to that status, clients cannot select an arbitrary target, and CANCELLED is terminal. | AC-PROJECT-017 | CHANGE-001 | UNIMPLEMENTED |
| REQ-PROJECT-018 | ROLLUP | DEC-007 | MUST | Ordinary Project DELETE is soft delete with `deleted_at`; default list/get/Dashboard exclude deleted projects and source content/comments are not automatically deleted. CHANGE-001 establishes only the Project-owned soft-delete/exclusion subset; shared-Source retention remains UNIMPLEMENTED until CHANGE-003 creates real shared Source associations and verifies the full Requirement. | AC-PROJECT-018 | CHANGE-001/003 | UNIMPLEMENTED |
| REQ-PROJECT-019 | ATOMIC | DEC-007 | MAY | A future independent PURGE may remove project-owned derived data and shared-source associations subject to reference safety; V0.1 need not provide Restore UI. | No | CHANGE-003/Future | UNIMPLEMENTED |
| REQ-CRAWL-015 | ATOMIC | §2.2, DEC-003 | MUST | Pause is available only during collection: WAITING/RUNNING jobs may enter PAUSED and all already collected Evidence is retained. | AC-CRAWL-015 | CHANGE-003 | UNIMPLEMENTED |
| REQ-CRAWL-016 | ATOMIC | §2.2, §9.5, DEC-003 | MUST | Resume sends PAUSED → WAITING → RUNNING; successful login detection sends LOGIN_REQUIRED → WAITING → RUNNING. | AC-CRAWL-016 | CHANGE-003 | UNIMPLEMENTED |
| REQ-CRAWL-017 | ATOMIC | DEC-003 | MUST | Stop and Cancel share terminal CANCELLED semantics while retaining data; Skip cancels only one platform and records `completion_reason=SKIPPED_BY_USER` without stopping other jobs/project. | AC-CRAWL-017 | CHANGE-003 | UNIMPLEMENTED |
| REQ-CRAWL-018 | ATOMIC | DEC-003 | MUST | Retry is allowed only from FAILED/PARTIAL_SUCCESS and creates an immutable new attempt linked to the logical Crawl Job without overwriting prior execution. | AC-CRAWL-018 | CHANGE-003 | UNIMPLEMENTED |
| REQ-SSE-001 | ATOMIC | DEC-008 + CHANGE-001 Design Patch R1 | MUST | PostgreSQL/backend REST is the state source of truth; initial load uses Connect → `STREAM_READY` → Buffer → GET Snapshot → Reconcile → Live so no Snapshot-to-stream race window exists. | AC-SSE-001 | CHANGE-001 | UNIMPLEMENTED |
| REQ-SSE-002 | ATOMIC | DEC-008 + CHANGE-001 Design Patch R1 | MUST | Every committed observable Project mutation increments database `project_version` exactly once and its mutation event carries that committed version; transport `event_id` is separate, while heartbeat and `STREAM_READY` carry `observed_project_version` and never advance Project version. | AC-SSE-002 | CHANGE-001 | UNIMPLEMENTED |
| REQ-SSE-003 | ATOMIC | DEC-008 + CHANGE-001 Design Patch R1 | MUST | On disconnect the client repeats the complete Connect → `STREAM_READY` → Buffer → GET Snapshot → Reconcile handshake; correctness cannot depend on durable replay or an event store. | AC-SSE-003 | CHANGE-001 | UNIMPLEMENTED |
| REQ-SSE-004 | ATOMIC | DEC-008 + CHANGE-001 Design Patch R1 | MUST | SSE provides heartbeat, current-stream ordering, duplicate/stale-version rejection, and deterministic reconciliation so events at or below the current version cannot overwrite or reapply newer state. | AC-SSE-004 | CHANGE-001 | UNIMPLEMENTED |
| REQ-UI-019 | ATOMIC | §7.10 | MAY | Settings may provide project cleanup, model-cache cleanup, and score-recalculation maintenance actions. | No | CHANGE-001/004/006 | UNIMPLEMENTED |
| REQ-API-001 | ATOMIC | §23.2 | MUST | Provide API capabilities to generate/update a Research Plan and start confirmed research; concrete paths may differ. | AC-API-001 | CHANGE-002 | UNIMPLEMENTED |
| REQ-API-002 | ATOMIC | §23.3 | MUST | Provide API capabilities to list Crawl Jobs and retry/cancel/resume an eligible job; concrete paths may differ. | AC-API-002 | CHANGE-003 | UNIMPLEMENTED |
| REQ-API-003 | ATOMIC | §23.4 | MUST | Provide API capabilities to analyze Signals, cluster, score, and reanalyze; concrete paths may differ. | AC-API-003 | CHANGE-004..006 | UNIMPLEMENTED |
| REQ-API-004 | ATOMIC | §23.5 | MUST | Provide API capabilities to list/get demands and analyze a demand; concrete paths may differ. | AC-API-004 | CHANGE-007 | UNIMPLEMENTED |
| REQ-API-005 | ATOMIC | §23.6 | MUST | Provide API capabilities to list project Evidence and get one Evidence item; concrete paths may differ. | AC-API-005 | CHANGE-007 | UNIMPLEMENTED |
| REQ-API-006 | ATOMIC | §23.7 | MUST | Provide API capabilities to create demand Opportunities and list project Opportunities; concrete paths may differ. | AC-API-006 | CHANGE-008 | UNIMPLEMENTED |
| REQ-API-007 | ROLLUP | §23.9 | MUST | Provide project event-notification capability covering the listed status/progress/error/login event types. | AC-API-007 | CHANGE-001/003..006 | UNIMPLEMENTED |
| REQ-API-008 | ATOMIC | §23 | SHOULD | Use the concrete REST path shapes listed in §23 as design guidance; equivalent paths are allowed. | No | CHANGE-001..009 | UNIMPLEMENTED |
| REQ-DATA-001 | ATOMIC | §21.1 | MUST | Persist `research_project` with id UUID PK, name, original_query, context, status, planner_version, created_at, updated_at, and completed_at. | AC-DATA-001 | CHANGE-001 | UNIMPLEMENTED |
| REQ-DATA-002 | ATOMIC | §21.2 | MUST | Persist `research_query` with id, research_project_id, group_type, keyword, enabled, AI/USER source, and created_at. | AC-DATA-002 | CHANGE-002 | UNIMPLEMENTED |
| REQ-DATA-003 | ATOMIC | §21.3 | MUST | Persist `crawl_job` with id, project/platform/status, config/progress JSON, error, and lifecycle timestamps. | AC-DATA-003 | CHANGE-003 | UNIMPLEMENTED |
| REQ-DATA-004 | ATOMIC | §21.4, §10.1 | MUST | Include a `source_content` business table conforming to the complete Source Content schema. | AC-DATA-004 | CHANGE-003 | UNIMPLEMENTED |
| REQ-DATA-005 | ATOMIC | §21.5, §10.2 | MUST | Include a `source_comment` business table conforming to the complete Source Comment schema. | AC-DATA-005 | CHANGE-003 | UNIMPLEMENTED |
| REQ-DATA-006 | ATOMIC | §21.6 | MUST | Include a `demand_signal` business table that persists structured Demand Signal Extractor results and Evidence linkage. | AC-DATA-006 | CHANGE-004 | UNIMPLEMENTED |
| REQ-DATA-007 | ATOMIC | §21.7, §15 | MUST | Include a `demand_cluster` business table conforming to the Demand Cluster schema. | AC-DATA-007 | CHANGE-005 | UNIMPLEMENTED |
| REQ-DATA-008 | ATOMIC | §21.8 | MUST | Include `demand_cluster_signal` with cluster_id, signal_id, membership_type, and created_at. | AC-DATA-008 | CHANGE-005 | UNIMPLEMENTED |
| REQ-DATA-009 | ATOMIC | §21.9, §17 | MUST | Include a `demand_snapshot` business table conforming to the Snapshot schema. | AC-DATA-009 | CHANGE-006 | UNIMPLEMENTED |
| REQ-DATA-010 | ATOMIC | §21.10 | MUST | Include `opportunity` with id, project/cluster linkage, PRODUCT/CONTENT type, payload_json, model_run_id, and timestamps. | AC-DATA-010 | CHANGE-008 | UNIMPLEMENTED |
| REQ-DATA-011 | ATOMIC | §21.11, §20 | MUST | Include a `model_run` business table conforming to the complete Model Run schema. | AC-DATA-011 | CHANGE-002/004 | UNIMPLEMENTED |
| REQ-ARCH-010 | ATOMIC | §4.1 | SHOULD | Use the suggested Next.js 15+/React 19+/TypeScript/Tailwind frontend baseline; DeepPoint structure/components remain optional reference. | No | CHANGE-001 | UNIMPLEMENTED |
| REQ-ARCH-011 | ROLLUP | §4.1 | MUST | Limit frontend responsibilities to pages, interactions, state display, charts/maps, API calls, and SSE/stream display. | AC-ARCH-011 | CHANGE-001..009 | UNIMPLEMENTED |
| REQ-ARCH-012 | ROLLUP | §4.2 | MUST | Backend owns Research Project, Crawl Job, Evidence, Signal, Cluster, Score, Opportunity, Model Run, scheduling, API, and SSE responsibilities. | AC-ARCH-012 | CHANGE-001..009 | UNIMPLEMENTED |
| REQ-ARCH-013 | ATOMIC | §4.3 | MAY | The three logical workers may run in the same process group in V0.1; independent deployment is not required. | No | CHANGE-001/003..005 | UNIMPLEMENTED |
| REQ-RESILIENCE-008 | ATOMIC | §28 | MAY | Development mode may expose expanded technical logs; ordinary UI need not show all low-level logs. | No | CHANGE-001..004 | UNIMPLEMENTED |
| REQ-FUTURE-001 | ATOMIC | §31.1 | MUST | V0.1 architecture reserves an extension point for future socai Deep Verify without implementing that V0.2 capability. | AC-FUTURE-001 | CHANGE-007 | UNIMPLEMENTED |
| REQ-FUTURE-002 | ATOMIC | §31.2 | MUST | V0.1 architecture reserves future Trend Signal storage separately from Demand Signal. | AC-FUTURE-002 | CHANGE-004/006 | UNIMPLEMENTED |
| REQ-FUTURE-003 | ATOMIC | §31.3 | MUST | V0.1 architecture reserves a future Content Opportunity handoff boundary for CreatorOS without implementing the integration. | AC-FUTURE-003 | CHANGE-008 | UNIMPLEMENTED |
| REQ-GOVERNANCE-001 | ATOMIC | §37.1 | SHOULD | Read the complete Spec Baseline before future OpenSpec/Codex work. | No | ALL | UNIMPLEMENTED |
| REQ-GOVERNANCE-002 | ATOMIC | §37.2 | SHOULD | Inspect actual repository state before future Change work. | No | ALL | UNIMPLEMENTED |
| REQ-GOVERNANCE-003 | ATOMIC | §37.3 | SHOULD | Use OpenSpec to create one clear Change at a time. | No | ALL | UNIMPLEMENTED |
| REQ-GOVERNANCE-004 | ATOMIC | §37.4 | SHOULD | Limit each Change to one §32 stage or a sufficiently small substage. | No | ALL | UNIMPLEMENTED |
| REQ-GOVERNANCE-005 | SCOPE_GUARD | §37.5 | MUST_NOT | Do not implement future-Change capabilities inside the active Change. | AC-GOVERNANCE-005 | ALL | UNIMPLEMENTED |
| REQ-GOVERNANCE-006 | SCOPE_GUARD | §37.6 | MUST_NOT | Do not change the mandated analysis model without explicit user authorization. | AC-GOVERNANCE-006 | ALL | UNIMPLEMENTED |
| REQ-GOVERNANCE-007 | ATOMIC | §37.7 | MUST | Keep Terra reasoning effort fixed to High for product semantic analysis. | AC-GOVERNANCE-007 | CHANGE-002..009 | UNIMPLEMENTED |
| REQ-GOVERNANCE-008 | SCOPE_GUARD | §37.8 | MUST_NOT | Do not adopt DeepPoint scoring as NeedRadar's final scoring implementation. | AC-GOVERNANCE-008 | CHANGE-006 | UNIMPLEMENTED |
| REQ-GOVERNANCE-009 | SCOPE_GUARD | §37.9 | MUST_NOT | Do not expose MediaCrawler's UI directly as NeedRadar's primary product UI. | AC-GOVERNANCE-009 | CHANGE-003 | UNIMPLEMENTED |
| REQ-GOVERNANCE-010 | ATOMIC | §37.10 | MUST | Every implementation commit includes corresponding tests and acceptance results. | AC-GOVERNANCE-010 | ALL | UNIMPLEMENTED |
| REQ-GOVERNANCE-011 | ATOMIC | §37.11 | MUST | Every schema change includes a migration. | AC-GOVERNANCE-011 | ALL | UNIMPLEMENTED |
| REQ-GOVERNANCE-012 | ATOMIC | §37.12 | MUST | Every LLM Prompt is versioned. | AC-GOVERNANCE-012 | CHANGE-002/004/005/007..009 | UNIMPLEMENTED |
| REQ-GOVERNANCE-013 | ATOMIC | §37.13 | MUST | Every Demand Score rule has unit tests. | AC-GOVERNANCE-013 | CHANGE-006 | UNIMPLEMENTED |
| REQ-GOVERNANCE-014 | ATOMIC | §37.14 | MUST | Every Research Project state transition has tests. | AC-GOVERNANCE-014 | CHANGE-001 | UNIMPLEMENTED |
| REQ-GOVERNANCE-015 | ATOMIC | §37.15 | MUST | Every completed Change reports implementation scope, file changes, database changes, test results, incomplete items, and acceptance conclusion. | AC-GOVERNANCE-015 | ALL | UNIMPLEMENTED |
| REQ-FOUNDATION-001 | ATOMIC | §32 CHANGE-001 | MUST | Foundation provides an executable local Web/API boundary with a health contract and verified PostgreSQL connectivity, without implementing later business capabilities. | AC-FOUNDATION-001 | CHANGE-001 | UNIMPLEMENTED |

## R2 Baseline normative coverage audit

The complete baseline was reread section by section. The table records where each normative area is indexed; it does not replace the source language.

| Baseline area | Catalog coverage | Audit note |
|---|---|---|
| §2 goals, success, non-goals | REQ-PROJECT, REQ-SCOPE, REQ-CRAWL-015..016, REQ-REPORT | Pause/resume and all individual non-goals are explicit. |
| §4 technical constraints | REQ-ARCH-001..013, REQ-GOVERNANCE-007 | Frontend/backend/worker/model/embedding responsibilities and suggestions retain their source strength. |
| §7 pages | REQ-UI-001..019, REQ-DEMAND, REQ-REPORT | Settings display remains MUST; maintenance actions are isolated as MAY. |
| §9–20 business rules | REQ-CRAWL, REQ-EVIDENCE, REQ-SIGNAL, REQ-CLUSTER, REQ-SCORE, REQ-DEMAND, REQ-OPPORTUNITY, REQ-MODELRUN | Confirmed crawl controls supplement rather than rewrite baseline rules. |
| §21 database structure | REQ-DATA-001..011, REQ-EVIDENCE-005 | Each minimum business table has its own structural Requirement; shared-source association remains a recorded design decision. |
| §22 state machine | REQ-PROJECT-009..012, REQ-PROJECT-016..017 | Original suggested vocabulary remains SHOULD/MAY; the user-confirmed exact machine is separately mandatory. |
| §23 API | REQ-PROJECT-013, REQ-API-001..008, REQ-REPORT-005, REQ-ARCH-007 | Capabilities are MUST; concrete path shapes are SHOULD guidance. |
| §24 UI | REQ-UI-011..016 | Progress, spinner prohibition, traceable metrics, and AI/statistics separation are mapped. |
| §25 resilience | REQ-RESILIENCE-001..005, REQ-SIGNAL-009 | Failure, batch retry, JSON failure, and insufficient-data behavior are mapped. |
| §26 traceability | REQ-EVIDENCE-007, REQ-MODELRUN-005..006 | Both score-to-source and summary-to-model-input chains are covered. |
| §27 performance/resources | REQ-UI-017..018, REQ-ARCH-008..009, REQ-SIGNAL-010..013 | Immediate feedback remains SHOULD; pagination/index/batching/cache/concurrency preserve source strength. |
| §28 logging | REQ-RESILIENCE-007..008 | Backend structured logging is mandatory; expanded developer UI logs remain optional. |
| §29 export | REQ-REPORT-002..003 | Markdown and the unresolved CSV/Excel table export wording remain tracked without resolving DEC-004. |
| §30 evaluation | REQ-EVAL-001..003 | Gold Set, metrics, and prompt regression are mandatory. |
| §31 future reservations | REQ-FUTURE-001..003, REQ-EVIDENCE-010 | V0.2 features are not implemented; required architectural extension boundaries are explicit. |
| §33 E2E | REQ-EVAL-004 | Classified E2E and cannot PASS before the complete scenario runs. |
| §34 red lines | REDLINE-AC-001..015 and linked Requirements | All fifteen remain independent blocking acceptances. |
| §35 priority | REQ-PROJECT-015 | P0→P1→P2 resource-constrained order remains mandatory. |
| §37 Codex/OpenSpec governance | REQ-GOVERNANCE-001..015 and AGENTS.md | Advice remains SHOULD; explicit MUST/MUST_NOT statements retain their force. |

Audit result: no normative statement identified in the listed areas remains intentionally unmapped. Suggestions and optional capabilities were not promoted to mandatory requirements.
