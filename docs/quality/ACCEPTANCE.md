# Acceptance Contract

This contract derives from the read-only Spec Baseline. A requirement result is never PASS until the named verification is executed and its artifact is retained. Automated levels are `STATIC`, `UNIT`, `INTEGRATION`, `CONTRACT`, `E2E`, and `LIVE_INTEGRATION`; `MANUAL` is used only where visual semantics cannot be established by a reasonable automated assertion. SQLite cannot satisfy a PostgreSQL integration criterion. Mocks cannot satisfy a live criterion.

## A. Requirement Acceptance

### Project and Planner

| AC ID | Requirement ID | Given | When | Then | Verification Level | Planned Evidence |
|---|---|---|---|---|---|---|
| AC-PROJECT-001 | REQ-PROJECT-001 | A clean local install and the mandatory research query | The complete V0.1 scenario runs | Every baseline stage completes in order and remains traceable | E2E | Playwright trace, API/DB snapshots, export hashes |
| AC-PROJECT-002 | REQ-PROJECT-002 | Supported local Mac, browser, and PostgreSQL | NeedRadar starts | One user accesses the local Web product and persistence works | E2E | Startup log, browser trace, PostgreSQL record |
| AC-PROJECT-003 | REQ-PROJECT-003 | A user follows every normal V0.1 flow | The flow completes | No CLI/config/SQL/script/prompt/model/API manual step is required | E2E | Full journey trace and command-free runbook |
| AC-PROJECT-004 | REQ-PROJECT-004 | V0.1 routes, schema, and UI | Static scope audit runs | No account, billing, membership, multi-user, or team-permission feature exists | STATIC | Route/schema/dependency scope report |
| AC-PROJECT-005 | REQ-PROJECT-005 | V0.1 deployment and feature inventory | Scope audit runs | No SaaS/mobile/automated outreach, marketing, publishing, or contact feature exists | STATIC | Build and route inventory |
| AC-PROJECT-006 | REQ-PROJECT-006 | V0.1 architecture/dependencies | Architecture audit runs | No realtime-web monitor, Kafka, microservice split, Elasticsearch, Neo4j, or GraphRAG implementation exists | STATIC | Dependency and deployment manifest audit |
| AC-PROJECT-007 | REQ-PROJECT-007 | Model/config/output surfaces | Scope and output audit runs | No self-hosted/multi-model route or automatic market/success estimate exists | STATIC | Provider allowlist and output-schema audit |
| AC-PROJECT-008 | REQ-PROJECT-008 | A persisted project with generated downstream objects | Its aggregate is retrieved | Every listed object is associated and navigable from the project | INTEGRATION | PostgreSQL fixture and relationship assertions |
| AC-PROJECT-010 | REQ-PROJECT-010 | Approved transition table | Legal and illegal transitions are requested | Backend accepts only legal transitions and records the result | UNIT | Exhaustive transition test matrix |
| AC-PROJECT-011 | REQ-PROJECT-011 | API status conflicts with any locally derived UI guess | UI renders project status | Display follows backend status only | E2E | Injected-state Playwright assertion |
| AC-PROJECT-013 | REQ-PROJECT-013 | Project API contract and real PostgreSQL | Create/list/get/delete capabilities are invoked through any conforming paths | CRUD behavior is available and DELETE follows confirmed soft-delete semantics | INTEGRATION | API contract trace and PostgreSQL row assertions |
| AC-PROJECT-014 | REQ-PROJECT-014 | Empty database and Dashboard | User creates an empty project | Card appears with its backend-owned status | E2E | Playwright trace plus PostgreSQL row |
| AC-PROJECT-015 | REQ-PROJECT-015 | Resource-constrained planning | Plan order is inspected | P0 work precedes P1 and P2 unless user explicitly changes priority | STATIC | OpenSpec proposal/task mapping audit |
| AC-PROJECT-016 | REQ-PROJECT-016 | Confirmed 13-state transition matrix | Every source/target pair is attempted | Every listed transition succeeds and every unlisted transition is rejected by backend | UNIT | Exhaustive state-pair test report |
| AC-PROJECT-017 | REQ-PROJECT-017 | Project fails from each retryable stage and a cancelled project | Retry/arbitrary-target commands are attempted | failed_from_status persists, retry returns only there, arbitrary target rejects, and CANCELLED cannot transition | UNIT | Table-driven failure/retry/terminal tests |
| AC-PROJECT-018 | REQ-PROJECT-018 | Project with and without shared Source references | Ordinary DELETE then list/get/Dashboard queries run | deleted_at is set, project is excluded by default, and Source rows remain | INTEGRATION | PostgreSQL before/after rows and API/UI assertions |
| AC-SCOPE-001 | REQ-SCOPE-001 | V0.1 routes/schema | Scope audit runs | No multi-user registration exists | STATIC | Route/schema inventory |
| AC-SCOPE-002 | REQ-SCOPE-002 | V0.1 routes/schema | Scope audit runs | No product login exists | STATIC | Route/schema inventory |
| AC-SCOPE-003 | REQ-SCOPE-003 | V0.1 routes/schema | Scope audit runs | No membership feature exists | STATIC | Route/schema inventory |
| AC-SCOPE-004 | REQ-SCOPE-004 | V0.1 routes/schema | Scope audit runs | No payment or billing feature exists | STATIC | Route/schema/dependency inventory |
| AC-SCOPE-005 | REQ-SCOPE-005 | V0.1 routes/schema | Scope audit runs | No team-permission feature exists | STATIC | Route/schema inventory |
| AC-SCOPE-006 | REQ-SCOPE-006 | V0.1 deployment | Deployment audit runs | No SaaS cloud service is introduced | STATIC | Deployment manifest |
| AC-SCOPE-007 | REQ-SCOPE-007 | V0.1 clients | Build audit runs | No mobile App client exists | STATIC | Build target inventory |
| AC-SCOPE-008 | REQ-SCOPE-008 | V0.1 integrations/jobs | Scope audit runs | No automatic private-message sender exists | STATIC | Job/integration inventory |
| AC-SCOPE-009 | REQ-SCOPE-009 | V0.1 integrations/jobs | Scope audit runs | No automatic marketing system exists | STATIC | Job/integration inventory |
| AC-SCOPE-010 | REQ-SCOPE-010 | V0.1 integrations/jobs | Scope audit runs | No automatic social publisher exists | STATIC | Job/integration inventory |
| AC-SCOPE-011 | REQ-SCOPE-011 | V0.1 integrations/jobs | Scope audit runs | No automatic prospect-contact system exists | STATIC | Job/integration inventory |
| AC-SCOPE-012 | REQ-SCOPE-012 | V0.1 scheduler | Scope audit runs | No second-level whole-web monitor exists | STATIC | Scheduler/route inventory |
| AC-SCOPE-013 | REQ-SCOPE-013 | V0.1 dependencies | Dependency audit runs | Kafka is absent | STATIC | Lockfile/dependency report |
| AC-SCOPE-014 | REQ-SCOPE-014 | V0.1 deployment | Architecture audit runs | Product is not split into microservices | STATIC | Deployment topology |
| AC-SCOPE-015 | REQ-SCOPE-015 | V0.1 dependencies | Dependency audit runs | Elasticsearch is absent | STATIC | Lockfile/service inventory |
| AC-SCOPE-016 | REQ-SCOPE-016 | V0.1 dependencies | Dependency audit runs | Neo4j is absent | STATIC | Lockfile/service inventory |
| AC-SCOPE-017 | REQ-SCOPE-017 | V0.1 dependencies/features | Scope audit runs | Complex GraphRAG is absent | STATIC | Dependency/feature inventory |
| AC-SCOPE-018 | REQ-SCOPE-018 | Model providers and deployment | Provider audit runs | No self-hosted analysis LLM or multi-model router exists | STATIC | Provider allowlist/deployment report |
| AC-SCOPE-019 | REQ-SCOPE-019 | Output schemas and scoring code | Scope audit runs | No automatic TAM/SAM/SOM or LLM market/blue-ocean/success score exists | STATIC | Schema/code dependency audit |
| AC-PLANNER-001 | REQ-PLANNER-001 | Planner API/UI | Missing query and then query+context are submitted | Missing query is rejected; context remains optional | CONTRACT | Schema validation fixtures |
| AC-PLANNER-002 | REQ-PLANNER-002 | Valid query and real configured Terra High provider | Planner is invoked | Provider returns schema-valid structured JSON linked to a Model Run | LIVE_INTEGRATION | Redacted request/response, run ID, schema result |
| AC-PLANNER-003 | REQ-PLANNER-003 | Generated/editable plan | Keyword groups are inspected | All six mandatory group types are supported | CONTRACT | Plan schema fixtures |
| AC-PLANNER-005 | REQ-PLANNER-005 | Generated plan | Confirmation page opens and is edited | Every required field is visible and the edited structure persists | E2E | Playwright trace and saved JSON |
| AC-PLANNER-006 | REQ-PLANNER-006 | Unconfirmed plan | Planner generation/edit/save occurs | No Crawl Job exists until explicit Start; Start creates jobs once | INTEGRATION | PostgreSQL assertions around confirmation |
| AC-PLANNER-007 | REQ-PLANNER-007 | Generic and demand-rich queries | Planner results are validated | Keywords are not labeled validated demands and a generic 3–5-term-only result is rejected | CONTRACT | Negative response fixtures |
| AC-PLANNER-008 | REQ-PLANNER-008 | Valid planner result | Keyword strategy is validated | Pain, help, price, and alternative-seeking strategies are represented | CONTRACT | Schema/semantic contract fixture |

### Crawl and Evidence

| AC ID | Requirement ID | Given | When | Then | Verification Level | Planned Evidence |
|---|---|---|---|---|---|---|
| AC-CRAWL-003 | REQ-CRAWL-003 | Confirmed plan with N selected platforms | Research starts | Exactly one independently identifiable Crawl Job exists per platform | INTEGRATION | PostgreSQL job-count assertion |
| AC-CRAWL-005 | REQ-CRAWL-005 | A configured platform job | It is saved and progresses | All required config and lifecycle fields persist | INTEGRATION | Migration/schema and row assertions |
| AC-CRAWL-006 | REQ-CRAWL-006 | Multiple runnable platform jobs and default config | Worker schedules them | At most one MediaCrawler job runs and others remain queued | INTEGRATION | Worker concurrency event log |
| AC-CRAWL-007 | REQ-CRAWL-007 | Multiple queued jobs | Collection UI opens | Queue order is visible and matches backend order | E2E | UI screenshot/DOM assertions and API payload |
| AC-CRAWL-008 | REQ-CRAWL-008 | Two platform jobs with one forced failure | Workers finish | Failed job is isolated; other job/project data remains | INTEGRATION | Fault-injection DB/event record |
| AC-CRAWL-009 | REQ-CRAWL-009 | Partial-success collection with Evidence | User chooses continue | Existing Evidence remains and analysis accepts it | E2E | Playwright trace and row hashes |
| AC-CRAWL-010 | REQ-CRAWL-010 | Adapter reports interactive login required | Job/UI update and login completes | Job is LOGIN_REQUIRED, prompt is explicit, and continue/re-detect is available | LIVE_INTEGRATION | Real platform login-state recording |
| AC-CRAWL-011 | REQ-CRAWL-011 | Adapter reports login required | Events/UI are observed | No silent success/failure occurs and reason is visible | E2E | Adapter stub contract plus UI assertion |
| AC-CRAWL-012 | REQ-CRAWL-012 | Active and failed jobs | Collection page renders | Each required platform field is displayed accurately | E2E | Playwright field assertions |
| AC-CRAWL-013 | REQ-CRAWL-013 | Failed, queued/running, and partial jobs | User invokes retry/skip/stop/continue | Each approved command follows the confirmed transition contract and preserves data | E2E | Command-by-state Playwright matrix |
| AC-CRAWL-014 | REQ-CRAWL-014 | Real logged-in supported platform and confirmed plan | User starts research in UI | MediaCrawler runs without CLI, progress streams, and real source rows persist | LIVE_INTEGRATION | Controlled real-run log, trace, redacted source IDs |
| AC-CRAWL-015 | REQ-CRAWL-015 | WAITING and RUNNING jobs with collected Evidence | User pauses each job | Job enters PAUSED, work stops at a safe boundary, and all Evidence remains | INTEGRATION | Transition/event trace and Evidence row hashes |
| AC-CRAWL-016 | REQ-CRAWL-016 | PAUSED job and LOGIN_REQUIRED job after successful login detection | Resume/continue executes | Each job follows its confirmed WAITING then RUNNING path under backend control | INTEGRATION | State transition and scheduler assertions |
| AC-CRAWL-017 | REQ-CRAWL-017 | Active multi-platform jobs with collected data | Stop/Cancel one job and Skip another | Targets become CANCELLED, data remains, skipped reason is recorded, and other jobs/project continue | INTEGRATION | Multi-job state/data fixture |
| AC-CRAWL-018 | REQ-CRAWL-018 | Jobs in FAILED, PARTIAL_SUCCESS, and ineligible states | Retry is requested | Only eligible states create a linked immutable new attempt; old attempts remain unchanged | INTEGRATION | Attempt lineage and negative-state assertions |
| AC-EVIDENCE-001 | REQ-EVIDENCE-001 | Duplicate content/comments including non-global comment IDs | Ingest runs twice | Unique constraints prevent duplicate source rows without rejecting distinct comments | INTEGRATION | PostgreSQL unique-constraint tests |
| AC-EVIDENCE-002 | REQ-EVIDENCE-002 | Representative content payload with unknown fields | Normalization runs | Every listed content field and raw payload persist correctly | INTEGRATION | Source fixture-to-row assertions |
| AC-EVIDENCE-003 | REQ-EVIDENCE-003 | Representative nested comment payload | Normalization runs | Every listed comment field and parent/source references persist | INTEGRATION | Nested comment fixture assertions |
| AC-EVIDENCE-004 | REQ-EVIDENCE-004 | Platform omits a metric | Normalization runs | Stored metric is NULL, never synthetic zero | UNIT | Normalizer boundary test |
| AC-EVIDENCE-005 | REQ-EVIDENCE-005 | Two projects collect the same source item | Both ingests complete | One source row has two project associations and no copied payload | INTEGRATION | PostgreSQL cardinality assertions |
| AC-EVIDENCE-006 | REQ-EVIDENCE-006 | Identical text from distinct sources and repeated ingestion | Evidence IDs are assigned | Sources retain stable distinct internal IDs; text is not a key | INTEGRATION | Identity/uniqueness fixture |
| AC-EVIDENCE-007 | REQ-EVIDENCE-007 | Any displayed demand conclusion | User drills into provenance | Path reaches immutable Evidence and original source URL/text | E2E | Demand-to-source Playwright trace |
| AC-EVIDENCE-008 | REQ-EVIDENCE-008 | Mixed Evidence dataset | Every specified filter/search is applied | Returned rows match each predicate and combinations | E2E | Parameterized Playwright/API tests |
| AC-EVIDENCE-009 | REQ-EVIDENCE-009 | Content and comment Evidence | Browser rows/details render | All required provenance and Signal/Cluster fields are accurate | E2E | DOM assertions against seeded DB |
| AC-EVIDENCE-010 | REQ-EVIDENCE-010 | V0.1 route/dependency inventory | Scope audit runs | No socai deep verify, OCR, or transcription implementation exists | STATIC | Route/dependency audit |

### Signal, Model Run, and resilience

| AC ID | Requirement ID | Given | When | Then | Verification Level | Planned Evidence |
|---|---|---|---|---|---|---|
| AC-SIGNAL-001 | REQ-SIGNAL-001 | Raw Evidence batch | Extractor pipeline starts | Versioned deterministic filter runs before any Terra call | INTEGRATION | Ordered pipeline event assertions |
| AC-SIGNAL-002 | REQ-SIGNAL-002 | One fixture per filter category plus controls | Filter runs | Enumerated noise is filtered and controls are retained | UNIT | Parameterized filter suite |
| AC-SIGNAL-003 | REQ-SIGNAL-003 | Short allowlisted demand phrases and short noise | Filter runs | Strong-demand phrases remain while noise filters | UNIT | Chinese phrase boundary fixtures |
| AC-SIGNAL-004 | REQ-SIGNAL-004 | Filtered and retained Evidence | Results persist | Boolean, reason, and version are stored correctly | INTEGRATION | PostgreSQL row assertions |
| AC-SIGNAL-005 | REQ-SIGNAL-005 | Schema fixtures using every Signal Type and combinations | Validation runs | All 16 values and multi-type arrays are accepted; unknown values reject | CONTRACT | JSON Schema test report |
| AC-SIGNAL-006 | REQ-SIGNAL-006 | Complete/invalid Signal payloads | Validation runs | Required fields/enums follow the baseline exactly | CONTRACT | Positive/negative schema fixtures |
| AC-SIGNAL-007 | REQ-SIGNAL-007 | Evidence with/without a demand | Extractor runs | Output cites only exact source text and emits false for no demand | CONTRACT | Provider response fixtures with quote-span checks |
| AC-SIGNAL-008 | REQ-SIGNAL-008 | Negative praise/interest/payment-absent fixtures | Extraction is evaluated | No unsupported demand/payment inference is emitted | CONTRACT | Adversarial fixture results |
| AC-SIGNAL-009 | REQ-SIGNAL-009 | Invalid JSON responses through all configured attempts | Parser pipeline runs | Repair then retry occurs; final run is FAILED and no Signal row is created | INTEGRATION | Attempt log and zero-row assertion |
| AC-SIGNAL-010 | REQ-SIGNAL-010 | 100 eligible comments | Extraction runs | Model call count demonstrates batching rather than one call per comment | INTEGRATION | Provider-spy call count |
| AC-SIGNAL-012 | REQ-SIGNAL-012 | Identical and changed inputs | Analysis repeats | Identical hash hits cache; each relevant change misses cache | UNIT | Hash/cache table-driven tests |
| AC-SIGNAL-013 | REQ-SIGNAL-013 | Cached successful run | User forces reanalysis | New immutable run executes and old run remains queryable | INTEGRATION | Run lineage rows |
| AC-MODELRUN-001 | REQ-MODELRUN-001 | Each Terra-powered workflow | Calls succeed/fail | Every provider call has a persistent Model Run | INTEGRATION | Cross-workflow foreign-key audit |
| AC-MODELRUN-002 | REQ-MODELRUN-002 | Successful and failed calls | Runs persist | Every listed field is stored with correct nullability | INTEGRATION | Schema and row fixture report |
| AC-MODELRUN-003 | REQ-MODELRUN-003 | One fixture per run type | Runs persist | All six types validate and are queryable | CONTRACT | Enum/schema test report |
| AC-MODELRUN-004 | REQ-MODELRUN-004 | Failed and historical-version runs | User views/retries/forces/compares | Each operation is available and maintains lineage | E2E | Playwright trace and lineage rows |
| AC-MODELRUN-005 | REQ-MODELRUN-005 | Two versions of each named artifact | Audit query runs | Version/provenance resolves the exact inputs and outputs | INTEGRATION | Provenance graph fixture |
| AC-MODELRUN-006 | REQ-MODELRUN-006 | Existing Model Run | Reanalysis occurs | Original row/payload remains unchanged and a new run is linked | INTEGRATION | Before/after row hashes |
| AC-RESILIENCE-001 | REQ-RESILIENCE-001 | Partial and total crawl failures | Project/UI settle | UI says failure/partial, never “no demand”, and retained data remains | E2E | Fault-injection Playwright trace |
| AC-RESILIENCE-002 | REQ-RESILIENCE-002 | Multi-batch run with one persistent failure | Automatic then manual retry executes | Successful batches remain, failure/error/limit persist, manual retry targets failure | INTEGRATION | Batch ledger assertions |
| AC-RESILIENCE-003 | REQ-RESILIENCE-003 | Exhausted JSON repair/retry | Output tables and UI are inspected | No default Medium or fake Signal exists; failure is explicit | INTEGRATION | Negative DB assertion and UI state |
| AC-RESILIENCE-004 | REQ-RESILIENCE-004 | Sparse coverage fixture | Demand detail opens | All five insufficiency/context fields are shown | E2E | Playwright DOM assertions |
| AC-RESILIENCE-005 | REQ-RESILIENCE-005 | Sparse nonzero demand fixture | Analysis/UI renders | Result is “insufficient data” where applicable, not “no demand” | E2E | Seeded scenario trace |
| AC-RESILIENCE-007 | REQ-RESILIENCE-007 | Representative lifecycle | Backend and UI events are inspected | Backend records every required log field and UI shows simplified events | INTEGRATION | Structured log schema assertions |

### Clustering and score

| AC ID | Requirement ID | Given | When | Then | Verification Level | Planned Evidence |
|---|---|---|---|---|---|---|
| AC-CLUSTER-001 | REQ-CLUSTER-001 | A Signal with raw text and normalized atom | Embedding input is captured | Input is not raw-full-comment-only | CONTRACT | Provider request fixture |
| AC-CLUSTER-004 | REQ-CLUSTER-004 | Alternate clustering test provider | Provider is configured | Pipeline calls the abstraction without algorithm leakage | CONTRACT | Provider conformance suite |
| AC-CLUSTER-005 | REQ-CLUSTER-005 | Dataset above configured threshold | Clustering is requested | No NxN matrix path is invoked | UNIT | Memory-path instrumentation test |
| AC-CLUSTER-006 | REQ-CLUSTER-006 | Dataset above threshold | Clustering runs | Approved efficient path runs or UI blocks with explicit limit | E2E | Large-fixture trace and memory metrics |
| AC-CLUSTER-007 | REQ-CLUSTER-007 | Micro-clusters and real Terra provider | Curator runs | Required semantic merge/split/name/hierarchy work returns | LIVE_INTEGRATION | Redacted request/response and curated result |
| AC-CLUSTER-008 | REQ-CLUSTER-008 | Curator proposes forbidden mutations/scores | Validation applies result | Mutation is rejected and originals remain unchanged | INTEGRATION | Adversarial payload and row hashes |
| AC-CLUSTER-009 | REQ-CLUSTER-009 | Merge and split operations | They persist | Each operation resolves to an immutable Model Run | INTEGRATION | Join/lineage assertions |
| AC-CLUSTER-010 | REQ-CLUSTER-010 | Signals assigned to multiple clusters/relations | Persistence and re-query occur | Listed fields and M:N membership persist without copied/lost Signal/Evidence | INTEGRATION | PostgreSQL cardinality/hash checks |
| AC-SCORE-001 | REQ-SCORE-001 | Fixed cluster fixture with missing data | Score calculates twice | Deterministic 0–100 result, breakdown/version, and explicit missing state match | UNIT | Golden score fixtures |
| AC-SCORE-002 | REQ-SCORE-002 | Complete fixture | Breakdown calculates | Exactly eight dimensions use weights 20/15/15/10/15/10/10/5 | UNIT | Weight-sum assertion |
| AC-SCORE-004 | REQ-SCORE-004 | Every recurrence enum including UNKNOWN | Dimension calculates | Stated mappings apply, UNKNOWN is excluded, max is 15 | UNIT | Table-driven formula tests |
| AC-SCORE-005 | REQ-SCORE-005 | Every pain enum | Dimension calculates | Stated mappings and max 15 apply | UNIT | Table-driven formula tests |
| AC-SCORE-006 | REQ-SCORE-006 | Qualifying/nonqualifying Signals | Workaround calculates | Only specified types/counts contribute and result ≤10 | UNIT | Positive/negative golden fixtures |
| AC-SCORE-007 | REQ-SCORE-007 | Every explicit payment enum with creator counts | Payment calculates | Stated mappings/evidence inputs apply and result ≤15 | UNIT | Payment golden fixtures |
| AC-SCORE-008 | REQ-SCORE-008 | AI opinion without payment Signal | Score calculates | Payment contribution is zero/insufficient per confirmed formula, never inferred | UNIT | Negative payment fixture |
| AC-SCORE-009 | REQ-SCORE-009 | Complaint/switch and unrelated Signals | Dimension calculates | Only listed sources contribute and result ≤10 | UNIT | Table-driven fixtures |
| AC-SCORE-010 | REQ-SCORE-010 | Sufficient and insufficient 7/30/90 snapshots | Trend calculates | Windows use history; absent history is missing, never zero | UNIT | Snapshot golden fixtures |
| AC-SCORE-012 | REQ-SCORE-012 | One or more missing dimensions | Total calculates and UI renders | Missing dimensions are removed, remaining weights rescale to 100, disclosure is visible | E2E | Unit math report plus UI assertion |
| AC-SCORE-013 | REQ-SCORE-013 | Existing v1 historical score and changed formula | Recalculation/version migration runs | Old version remains immutable and new result has a distinct version | INTEGRATION | Before/after score history rows |

### Demand, Opportunity, and Report

| AC ID | Requirement ID | Given | When | Then | Verification Level | Planned Evidence |
|---|---|---|---|---|---|---|
| AC-DEMAND-001 | REQ-DEMAND-001 | Seeded project | Demand overview opens | All five top statistics equal DB aggregates | E2E | DOM-to-query assertions |
| AC-DEMAND-002 | REQ-DEMAND-002 | Seeded clusters | List opens | Every required column/value is present and accurate | E2E | Playwright table assertions |
| AC-DEMAND-003 | REQ-DEMAND-003 | Varied seeded clusters | Sort/filter/search/time controls run | Each control and combination returns correct rows | E2E | Parameterized Playwright tests |
| AC-DEMAND-004 | REQ-DEMAND-004 | Parent/child clusters | Map/group view opens | Topic, child, score, scale, and trend display correctly | E2E | Tree assertions and snapshot |
| AC-DEMAND-005 | REQ-DEMAND-005 | Evidence-rich cluster | Detail opens | All 20 required facts/actions are present and traceable | E2E | DOM checklist and click trace |
| AC-DEMAND-006 | REQ-DEMAND-006 | Complete analyst input and real provider | Analysis runs | Output contains every required field, uncertainty, and valid Evidence IDs | LIVE_INTEGRATION | Redacted Model Run and citation validator |
| AC-DEMAND-007 | REQ-DEMAND-007 | Completion and manual refresh across dates | Snapshots save and trends query | Required fields/windows/first-seen/direction are correct | INTEGRATION | Time-controlled PostgreSQL fixtures |
| AC-OPPORTUNITY-001 | REQ-OPPORTUNITY-001 | Product/content records | They persist/query | Type validates and each references one or more Clusters | INTEGRATION | FK/type assertions |
| AC-OPPORTUNITY-002 | REQ-OPPORTUNITY-002 | Demand detail before user action | Page loads, then user clicks Analyze | No call precedes click; one intentional analysis begins after | E2E | Provider-spy/Playwright trace |
| AC-OPPORTUNITY-003 | REQ-OPPORTUNITY-003 | Many demands | Overview/background jobs run | No automatic bulk Opportunity provider calls occur | INTEGRATION | Provider call-count assertion |
| AC-OPPORTUNITY-004 | REQ-OPPORTUNITY-004 | Evidence-rich demand and constraints | Provider request is built | Request includes every required input category | CONTRACT | Request-schema fixture |
| AC-OPPORTUNITY-005 | REQ-OPPORTUNITY-005 | Identical demand data and changed personal constraints | Score and Opportunity rerun | Demand Score is unchanged while Opportunity input/output may change | UNIT | Independence fixture |
| AC-OPPORTUNITY-006 | REQ-OPPORTUNITY-006 | Real provider and valid demand | Product/content analysis runs | All baseline output fields/topics and valid Evidence IDs exist | LIVE_INTEGRATION | Redacted runs and schema/citation report |
| AC-OPPORTUNITY-007 | REQ-OPPORTUNITY-007 | High-heat weak-demand fixture | Opportunity renders | Heat is not asserted as product-worthiness and is visually separate from analysis | CONTRACT | Adversarial output validation |
| AC-REPORT-001 | REQ-REPORT-001 | Completed project | Report generates | Every required section and Evidence citation is present | E2E | Report schema/snapshot and link checks |
| AC-REPORT-002 | REQ-REPORT-002 | Completed mandatory scenario | User exports | Markdown and user-confirmed table format(s) download successfully | E2E | Files, MIME/name checks, hashes |
| AC-REPORT-003 | REQ-REPORT-003 | Known dataset | Table export opens | Demands/Signals/Evidence datasets contain every listed column and correct rows | CONTRACT | Parsed CSV/XLSX schema and content assertions |
| AC-REPORT-005 | REQ-REPORT-005 | Completed project | Report get/regenerate and Markdown/table export capabilities are invoked | All capabilities work regardless of equivalent concrete route naming | CONTRACT | API capability conformance suite |

### UI, architecture, and evaluation

| AC ID | Requirement ID | Given | When | Then | Verification Level | Planned Evidence |
|---|---|---|---|---|---|---|
| AC-UI-001 | REQ-UI-001 | Built V0.1 app | Route capability audit runs | All ten page capabilities are reachable through UI navigation | E2E | Route/navigation Playwright report |
| AC-UI-002 | REQ-UI-002 | Project fixtures | Dashboard renders | Entry/list/card display every listed field and action | E2E | DOM checklist |
| AC-UI-003 | REQ-UI-003 | New Research page | Query-only and query+context submit | Inputs persist and start Planner generation | E2E | Playwright form trace |
| AC-UI-004 | REQ-UI-004 | Generated plan | User exercises every plan editor control | Each edit persists and affects confirmed plan only | E2E | Parameterized editor trace |
| AC-UI-005 | REQ-UI-005 | Jobs in each relevant state | Collection UI opens and actions run | Progress/login/retry/skip/stop/continue are accurate and usable | E2E | State/action matrix trace |
| AC-UI-006 | REQ-UI-006 | Seeded demand data | Overview opens | Statistics, list, filters, and map are usable | E2E | Playwright feature checklist |
| AC-UI-007 | REQ-UI-007 | Seeded demand | Detail opens | Explanation/evidence/score/children/opportunity controls work | E2E | Drill-down trace |
| AC-UI-008 | REQ-UI-008 | Mixed Evidence | Evidence UI opens | Required filters/provenance work end to end | E2E | Search/filter trace |
| AC-UI-009 | REQ-UI-009 | Product/content Opportunities | Lab opens | Types are separated and all product fields render | E2E | DOM assertions |
| AC-UI-010 | REQ-UI-010 | Configured app with data/platform states | Settings opens | Read-only model/reasoning, all seven platform states, and all five data counts display accurately | E2E | Settings Playwright report |
| AC-UI-011 | REQ-UI-011 | Task lasting over several seconds | User observes it | Phase, completed/failed counts, current action, and valid cancel/retry state update | E2E | Timed task trace |
| AC-UI-012 | REQ-UI-012 | Long task | UI renders | At least required progress context accompanies any spinner | E2E | DOM negative assertion |
| AC-UI-013 | REQ-UI-013 | Screen containing statistics and AI analysis | Visual review is performed | Two categories are visually distinct and analysis bears `Terra High 分析` | MANUAL | Approved annotated screenshot checklist |
| AC-UI-014 | REQ-UI-014 | Overview with key metrics | User clicks each metric | Composition/detail opens along evidence→demand→opportunity hierarchy | E2E | Click-path trace |
| AC-UI-015 | REQ-UI-015 | Completed UI | Information architecture audit runs | Full project/collection/demand/evidence/opportunity flow exists; no chat-only substitute | E2E | Navigation coverage report |
| AC-UI-016 | REQ-UI-016 | Ordinary user and settings UI | UI/API surfaces are inspected | Model is read-only and no model switch/router is exposed | E2E | DOM/route negative assertions |
| AC-UI-017 | REQ-UI-017 | Dataset with tens of thousands of Evidence rows | Large list opens and scrolls/pages | DOM stays bounded and server/client pagination or virtualization works | E2E | DOM node-count and paging trace |
| AC-ARCH-001 | REQ-ARCH-001 | Frontend bundle/source graph | Boundary audit runs | No crawler process, semantic judgment, clustering, or scoring core executes client-side | STATIC | Dependency/import boundary report |
| AC-ARCH-003 | REQ-ARCH-003 | Runtime composition | Worker roles start | Three logical worker roles are independently identifiable/configurable | INTEGRATION | Process/task registry assertions |
| AC-ARCH-004 | REQ-ARCH-004 | Every semantic run type | Provider requests and settings are audited | Resolved product runtime is Terra with high reasoning, backend-controlled | CONTRACT | Provider request snapshots/config allowlist |
| AC-ARCH-005 | REQ-ARCH-005 | Alternate embedding test provider | Pipeline runs | Provider abstraction handles only vector/similarity/micro-cluster use | CONTRACT | Interface conformance tests |
| AC-ARCH-006 | REQ-ARCH-006 | Embedding outputs and business pipeline | Boundary tests run | No payment/market/product/final conclusion derives from embedding alone | UNIT | Taint/dependency fixture |
| AC-ARCH-007 | REQ-ARCH-007 | All V0.1 API capability suites | Capability audit runs across Changes | Every Project/Planner/Crawl/Analysis/Demand/Evidence/Opportunity/Report/Event capability is implemented; path spelling is not the criterion | CONTRACT | Aggregated API capability report |
| AC-ARCH-008 | REQ-ARCH-008 | Migrated PostgreSQL schema | Index audit runs | Every baseline-named lookup/sort field has an effective index | INTEGRATION | Catalog query and representative EXPLAIN plans |
| AC-ARCH-009 | REQ-ARCH-009 | Default worker configuration | Workers schedule representative jobs | Crawler and clustering concurrency are 1 and analysis concurrency is configurable | INTEGRATION | Configuration and concurrency event assertions |
| AC-ARCH-011 | REQ-ARCH-011 | Built frontend bundle and source graph | Responsibility audit runs | Client code is limited to the listed presentation/interaction/API/SSE responsibilities | STATIC | Import graph and boundary report |
| AC-ARCH-012 | REQ-ARCH-012 | Built backend modules | Responsibility audit runs | Each listed domain/service responsibility has a backend owner and no required domain responsibility is client-only | STATIC | Module ownership matrix |
| AC-EVAL-001 | REQ-EVAL-001 | Evaluation checkout | Gold Set schema validates | Directory and every labeled field exist under approved data policy | STATIC | Dataset manifest/schema report |
| AC-EVAL-002 | REQ-EVAL-002 | Versioned Gold Set and pipeline | Evaluation runs | All seven metric families are calculated and retained | INTEGRATION | Versioned evaluation report |
| AC-EVAL-003 | REQ-EVAL-003 | Major prompt change | Release gate runs | Gold Set regression completes before prompt becomes active; regression failure blocks | INTEGRATION | CI/gate log and metric diff |
| AC-EVAL-004 | REQ-EVAL-004 | Clean supported environment | Mandatory Chinese query runs through eight stages | Entire command-free scenario passes with traceable artifacts | E2E | Playwright trace, live evidence refs, exports |

### SSE, API, and data structure

| AC ID | Requirement ID | Given | When | Then | Verification Level | Planned Evidence |
|---|---|---|---|---|---|---|
| AC-SSE-001 | REQ-SSE-001 | Project state exists before page entry | Page initializes | Client connects SSE, receives `STREAM_READY`, buffers subsequent Project events, GETs the authoritative Snapshot, discards buffered mutation versions at or below Snapshot version, applies/reconciles newer versions in order, then enters live mode | E2E | Network-order Playwright trace plus deterministic handshake fixture |
| AC-SSE-002 | REQ-SSE-002 | Committed Project mutations and multiple idle intervals occur | Mutation, heartbeat, and `STREAM_READY` events are captured | Each mutation event has `event_id`, `project_id`, committed integer `project_version`, `event_type`, UTC `occurred_at`, and object `payload`; committed observable mutations increment Project version exactly once, while heartbeat/control events use separate transport identity plus `observed_project_version` and repeated heartbeats/`STREAM_READY` never change database `project_version` | CONTRACT | Event-schema, database-version, and non-mutating heartbeat/control fixtures |
| AC-SSE-003 | REQ-SSE-003 | SSE connection drops during handshake or after missed changes | Client reconnects | Client abandons the incomplete stream and repeats Connect → `STREAM_READY` → Buffer → GET Snapshot → Reconcile, reaching correct committed state without durable replay | E2E | Disconnect/reconnect network trace plus deterministic handshake-disconnect fixture |
| AC-SSE-004 | REQ-SSE-004 | Heartbeats, duplicate events, and out-of-order old/equal-version mutation events occur | Stream/client handles them | Heartbeat keeps connection observable, current-stream ordering holds, and any mutation event with `project_version <= currentVersion` is ignored without regressing or reapplying observable state | CONTRACT | Timed stream, duplicate, and stale-event fixtures |

`AC-PROJECT-018` retains its full shared-Source PostgreSQL acceptance threshold. CHANGE-001 may retain only partial evidence for Project soft-delete/default exclusion; the AC Result remains `UNIMPLEMENTED` until CHANGE-003 creates real shared Source associations and verifies that deleting one Project preserves shared Source rows and the other Project's access.
| AC-API-001 | REQ-API-001 | Planner API implementation | Capability conformance suite runs | Generate/update/start capabilities exist independent of exact paths | CONTRACT | OpenAPI/request-response capability report |
| AC-API-002 | REQ-API-002 | Crawl API implementation | Capability conformance suite runs | List/retry/cancel/resume capabilities exist and enforce confirmed state rules | CONTRACT | State-aware API contract report |
| AC-API-003 | REQ-API-003 | Analysis API implementation | Capability conformance suite runs | Signal analysis, clustering, scoring, and reanalysis capabilities exist | CONTRACT | API capability report |
| AC-API-004 | REQ-API-004 | Demand API implementation | Capability conformance suite runs | Demand list/get/analyze capabilities exist | CONTRACT | API capability report |
| AC-API-005 | REQ-API-005 | Evidence API implementation | Capability conformance suite runs | Project Evidence list and single Evidence get capabilities exist | CONTRACT | API capability report |
| AC-API-006 | REQ-API-006 | Opportunity API implementation | Capability conformance suite runs | Opportunity create and project list capabilities exist | CONTRACT | API capability report |
| AC-API-007 | REQ-API-007 | Event notification implementation | Each listed event category is emitted | Project/job status, keyword, counts, batch/cluster progress, errors, and login notifications are available | CONTRACT | Event-type conformance report |
| AC-DATA-001 | REQ-DATA-001 | Fresh migration | research_project schema is inspected | Table and every required field/type exist | INTEGRATION | PostgreSQL catalog assertions |
| AC-DATA-002 | REQ-DATA-002 | Fresh migration | research_query schema is inspected | Table and every required field/source enum exist with project relation | INTEGRATION | PostgreSQL catalog/FK assertions |
| AC-DATA-003 | REQ-DATA-003 | Fresh migration | crawl_job schema is inspected | Table and every required config/progress/error/time field exist | INTEGRATION | PostgreSQL catalog assertions |
| AC-DATA-004 | REQ-DATA-004 | Fresh migration | source_content schema is inspected | Business table conforms to Source Content requirements | INTEGRATION | PostgreSQL catalog-to-schema report |
| AC-DATA-005 | REQ-DATA-005 | Fresh migration | source_comment schema is inspected | Business table conforms to Source Comment requirements | INTEGRATION | PostgreSQL catalog-to-schema report |
| AC-DATA-006 | REQ-DATA-006 | Fresh migration and Signal fixture | demand_signal persists/reloads | Structured result and stable Evidence relation round-trip | INTEGRATION | Schema plus row round-trip |
| AC-DATA-007 | REQ-DATA-007 | Fresh migration | demand_cluster schema is inspected | Business table conforms to Cluster requirements | INTEGRATION | PostgreSQL catalog-to-schema report |
| AC-DATA-008 | REQ-DATA-008 | Fresh migration and memberships | demand_cluster_signal persists/reloads | All four fields and M:N uniqueness/references work | INTEGRATION | Catalog, FK, and cardinality assertions |
| AC-DATA-009 | REQ-DATA-009 | Fresh migration and dated fixture | demand_snapshot persists/reloads | Business table conforms to Snapshot requirements | INTEGRATION | Catalog and time-series row assertions |
| AC-DATA-010 | REQ-DATA-010 | Fresh migration and both opportunity types | opportunity persists/reloads | All fields, enum, project/cluster/model references, and timestamps work | INTEGRATION | Catalog/FK/round-trip assertions |
| AC-DATA-011 | REQ-DATA-011 | Fresh migration and successful/failed run fixtures | model_run persists/reloads | Business table conforms to complete Model Run requirements | INTEGRATION | Catalog and payload/provenance round-trip |

### Future boundaries and engineering governance

| AC ID | Requirement ID | Given | When | Then | Verification Level | Planned Evidence |
|---|---|---|---|---|---|---|
| AC-FUTURE-001 | REQ-FUTURE-001 | V0.1 Demand Detail architecture | Extension-boundary audit runs | Deep Verify can be added later without implementing or coupling its V0.2 workflow now | STATIC | Interface/architecture note |
| AC-FUTURE-002 | REQ-FUTURE-002 | V0.1 Signal data model | Extension-boundary audit runs | Future Trend Signal has a separate extension boundary and is not stored as Demand Signal | STATIC | Schema ownership note |
| AC-FUTURE-003 | REQ-FUTURE-003 | V0.1 Content Opportunity boundary | Extension-boundary audit runs | Future CreatorOS handoff can attach without an implemented integration | STATIC | Interface/architecture note |
| AC-GOVERNANCE-005 | REQ-GOVERNANCE-005 | Active OpenSpec Change scope | Changed files/tasks are audited | No future-Change capability is implemented | STATIC | Scope-to-diff report |
| AC-GOVERNANCE-006 | REQ-GOVERNANCE-006 | Approved product model policy | Provider/config diff is audited | Analysis model has not changed without explicit user instruction | STATIC | Config allowlist and decision reference |
| AC-GOVERNANCE-007 | REQ-GOVERNANCE-007 | Every semantic provider request | Contract audit runs | reasoning effort is High | CONTRACT | Request snapshot report |
| AC-GOVERNANCE-008 | REQ-GOVERNANCE-008 | Scoring implementation | Dependency/formula audit runs | DeepPoint scoring is not the final NeedRadar score | STATIC | Formula provenance report |
| AC-GOVERNANCE-009 | REQ-GOVERNANCE-009 | NeedRadar navigation/UI | UI ownership audit runs | MediaCrawler UI is not exposed as the primary product UI | E2E | Navigation trace |
| AC-GOVERNANCE-010 | REQ-GOVERNANCE-010 | Implementation commit | Change evidence is reviewed | Corresponding tests and acceptance results are present | STATIC | Commit/Change evidence checklist |
| AC-GOVERNANCE-011 | REQ-GOVERNANCE-011 | Any schema diff | Change evidence is reviewed | A matching migration exists and is tested | STATIC | Schema-to-migration audit |
| AC-GOVERNANCE-012 | REQ-GOVERNANCE-012 | Any LLM prompt | Prompt inventory is audited | Every prompt has a stable version identifier | STATIC | Prompt manifest |
| AC-GOVERNANCE-013 | REQ-GOVERNANCE-013 | Every Demand Score rule | Test inventory runs | Each rule has unit coverage including boundaries | UNIT | Rule-to-test matrix |
| AC-GOVERNANCE-014 | REQ-GOVERNANCE-014 | Confirmed Project transition matrix | State test inventory runs | Every allowed and forbidden transition is covered | UNIT | Exhaustive transition coverage report |
| AC-GOVERNANCE-015 | REQ-GOVERNANCE-015 | Completed Change | Completion report is inspected | All six required report categories are present | STATIC | Change completion checklist |
| AC-FOUNDATION-001 | REQ-FOUNDATION-001 | Clean local environment with real PostgreSQL | Foundation Web/API boundary starts and health is queried | Web and API health respond, PostgreSQL connectivity is proven, and no future business capability is presented as implemented | INTEGRATION | Startup/health logs and PostgreSQL probe |

## B. Red-Line Acceptance

Every red line is independent. Any `FAIL` blocks acceptance of the corresponding Change and the project gate. A red-line PASS still requires its underlying requirement acceptance to pass.

| AC ID | Requirement ID | Given | When | Then | Verification Level | Planned Evidence |
|---|---|---|---|---|---|---|
| REDLINE-AC-001 | REQ-PROJECT-003, REQ-CRAWL-014 | Normal supported use | User completes collection | No manual MediaCrawler command is required | LIVE_INTEGRATION | Command-free real-platform trace |
| REDLINE-AC-002 | REQ-SCORE-001, REQ-SCORE-008 | Scored demand | Score provenance is audited | Program data, not Terra subjective score, determines Demand Score | UNIT | Formula dependency/golden tests |
| REDLINE-AC-003 | REQ-EVIDENCE-007 | Any demand | Provenance traversal runs | Original real Evidence is reachable | E2E | Drill-down trace |
| REDLINE-AC-004 | REQ-SCORE-001 | Comments containing non-demand discussion | Counts calculate | Ordinary comment volume is not treated as demand volume | UNIT | Negative counting fixture |
| REDLINE-AC-005 | REQ-SCORE-008 | Payment-absent Evidence plus AI speculation | Payment computes | No payment contribution appears | UNIT | Negative payment fixture |
| REDLINE-AC-006 | REQ-RESILIENCE-001 | Crawl failure | UI settles | Failure is not presented as no demand | E2E | Fault-injection trace |
| REDLINE-AC-007 | REQ-SIGNAL-009, REQ-RESILIENCE-003 | Exhausted invalid JSON | Pipeline completes | Run fails explicitly and no default Medium/fake Signal exists | INTEGRATION | Attempt log and zero-row check |
| REDLINE-AC-008 | REQ-CLUSTER-010 | Completed clustering | Referential audit runs | All original Signals/Evidence remain linked, not summary-only | INTEGRATION | Cardinality/hash audit |
| REDLINE-AC-009 | REQ-UI-015 | Completed product | Navigation audit runs | Complete project/collection/demand/evidence/opportunity workflow exists | E2E | Route and user-journey coverage |
| REDLINE-AC-010 | REQ-UI-016 | Ordinary-user UI | Surface audit runs | No model switching or multi-model routing is exposed | E2E | Negative DOM/API assertion |
| REDLINE-AC-011 | REQ-SCORE-001, REQ-SCORE-012 | Any score | User expands it | Every point and missing dimension is explainable | E2E | Breakdown-to-source trace |
| REDLINE-AC-012 | REQ-EVIDENCE-006 | Identical text from two sources | IDs generate | Distinct stable Evidence identities and origins remain | INTEGRATION | Identity fixture |
| REDLINE-AC-013 | REQ-MODELRUN-006 | Existing run | Reanalysis occurs | Old run remains immutable and traceable | INTEGRATION | Before/after row hashes |
| REDLINE-AC-014 | REQ-CRAWL-008, REQ-RESILIENCE-001 | One of multiple platforms fails | Research continues | Other platform data and project remain available | E2E | Multi-platform fault trace |
| REDLINE-AC-015 | REQ-RESILIENCE-004, REQ-RESILIENCE-005 | Insufficient sample | Detail renders | Insufficient data is disclosed and not equated to no demand | E2E | Sparse-data trace |
