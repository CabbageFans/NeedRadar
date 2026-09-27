# NeedRadar 需求说明书（OpenSpec 开发版）

> 文档版本：v1.0  
> 目标阶段：V0.1 本地自用版  
> 开发方式：OpenSpec + Codex  
> 产品形态：本地 Web 可视化应用  
> 唯一大模型：GPT-5.6 Terra，reasoning.effort = high  
> 主要数据采集底座：MediaCrawler  
> 前端起点：可参考/复用 DeepPoint 的页面与交互骨架，但 NeedRadar 业务模型、需求分析链路和评分体系以本说明书为准

---

## 0. 文档用途

本说明书用于后续通过 OpenSpec 驱动 NeedRadar 的需求拆解、变更管理、设计和开发。

后续任何 Codex/OpenSpec 指令均应以本说明书为最高业务约束，除非用户明确修改需求。

本说明书强调以下原则：

1. NeedRadar 是“真实需求发现工具”，不是通用爬虫 UI。
2. 用户通过可视化页面完成全部正常操作，不依赖命令行。
3. MediaCrawler 仅负责数据采集，不承担需求判断。
4. GPT-5.6 Terra High 是唯一承担语义判断、研究规划、需求提取、需求合并和机会分析的大模型。
5. Embedding 模型只负责文本向量化，不参与市场判断，不视为第二个分析大模型。
6. Demand Score 必须尽量由可追溯的结构化数据计算，不允许由大模型直接输出一个“市场分数”。
7. 每一个需求结论必须能够回溯到原始帖子/评论证据。
8. 第一版以“本地、自用、单用户、可验证”为优先，不建设 SaaS、多租户、付费、权限体系。
9. 第一版支持失败、部分成功和人工登录，不允许把采集失败误判为“没有需求”。
10. 不追求一次做成全网实时监控系统，先把“研究方向 → 真实需求 → 证据 → 产品机会”闭环做扎实。

---

# 1. 产品定义

## 1.1 产品名称

NeedRadar（需求雷达）

## 1.2 一句话定位

用户输入一个市场、行业、创作者类型或研究方向，NeedRadar 自动从中文社交平台采集真实内容与评论，识别真实需求信号，聚类形成需求地图，基于证据计算需求强度，并进一步生成产品机会和内容机会。

## 1.3 典型输入

- AI漫剧创作者
- 历史类自媒体创作者
- 科普账号运营
- 自媒体新手起号
- 短视频剪辑工具
- 独立开发者找需求
- 宠物博主运营
- 二手卖家

## 1.4 典型输出

以“AI漫剧创作者”为例，系统最终应输出：

- 研究覆盖的平台和关键词；
- 共采集多少帖子、视频、评论；
- 多少条内容被识别为真实 Demand Signal；
- Top 需求列表；
- 需求树/需求地图；
- 每个需求的讨论量、独立用户量、平台覆盖、趋势、付费信号、Workaround、现有方案不满；
- 每个需求对应的真实原帖/评论证据；
- 基于这些需求生成的产品机会；
- 基于这些需求生成的内容/选题机会；
- 一份可导出的研究报告。

---

# 2. 产品目标与非目标

## 2.1 V0.1 核心目标

V0.1 必须完成以下闭环：

> 输入研究方向 → Terra High 生成研究计划 → 用户确认 → MediaCrawler 采集 → 证据归一化 → Terra High 提取 Demand Signal → Embedding 聚类 → Terra High 合并/拆分需求 → 程序计算 Demand Score → 可视化需求地图 → 查看原始证据 → Terra High 生成产品机会 → 输出研究报告。

## 2.2 成功标准

V0.1 被认为“可用”，至少满足：

1. 用户完全通过 Web UI 创建、启动、暂停/失败重试、查看研究任务。
2. 至少可以对 MediaCrawler 支持的平台进行统一任务配置和采集。
3. 可将帖子与评论统一归一化到 NeedRadar 数据模型。
4. 可对评论/内容批量调用 Terra High，识别需求信号。
5. 可将大量需求信号聚成可浏览的需求簇。
6. 每个需求簇可以追溯到底层 Evidence。
7. Demand Score 的各维度可解释、可展开查看原始统计。
8. 用户可以从需求列表进入需求详情，并查看用户当前 Workaround 与付费信号。
9. 用户可以对需求生成产品机会。
10. 可导出 Markdown 和 Excel/CSV 研究结果。

## 2.3 V0.1 非目标

第一版明确不做：

- 多用户注册；
- 登录/会员/支付；
- 团队权限；
- SaaS 云服务；
- 手机 App；
- 自动私信用户；
- 自动营销；
- 自动发布社交内容；
- 自动联系潜在客户；
- 实时秒级监控全网；
- Kafka；
- 微服务拆分；
- Elasticsearch；
- Neo4j；
- 复杂 GraphRAG；
- 自建大模型；
- 多模型路由；
- 自动估算 TAM/SAM/SOM；
- 由大模型直接给“市场规模分”“蓝海分”“成功概率”。

---

# 3. 用户与使用环境

## 3.1 用户

V0.1 只有一个用户：产品所有者本人。

无需设计账户体系。

## 3.2 运行环境

- 本地 Mac 为主要使用环境；
- 浏览器访问 localhost Web UI；
- PostgreSQL 作为主数据库；
- MediaCrawler 作为本地采集进程；
- Chrome/Chromium 登录态由 MediaCrawler 使用；
- 后端可通过本地环境变量配置 OpenAI API Key；
- 所有正常产品操作必须在 Web UI 内完成。

## 3.3 用户不应接触的技术细节

正常使用过程中不要求用户：

- 编辑 Python 配置文件；
- 执行 MediaCrawler CLI；
- 手工运行 SQL；
- 手工执行聚类脚本；
- 修改 Prompt 文件；
- 选择大模型；
- 手工拼 API 请求。

开发/调试模式可以保留 CLI，但 UI 必须覆盖正常产品能力。

---

# 4. 技术基线与强约束

## 4.1 前端

建议：

- Next.js 15+
- React 19+
- TypeScript
- Tailwind CSS
- 可复用 DeepPoint 的前端结构与组件思想

前端只负责：

- 页面；
- 用户交互；
- 状态展示；
- 图表/需求地图；
- 调用 API；
- SSE/流式任务状态更新。

前端不得直接承担：

- MediaCrawler 进程管理核心；
- LLM 业务判断；
- 数据聚类；
- 评分计算。

## 4.2 后端

建议：

- Python 3.11+
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- pgvector 或等价向量支持

后端负责：

- Research Project；
- Crawl Job；
- Evidence；
- Demand Signal；
- Cluster；
- Scoring；
- Opportunity；
- Model Run；
- 调度；
- API；
- SSE。

## 4.3 Worker

至少拆为逻辑上的三个 Worker：

1. `crawler_worker`
2. `analysis_worker`
3. `clustering_worker`

V0.1 不要求独立部署，可运行在同一进程组中。

## 4.4 大模型

唯一分析模型：

- Model: GPT-5.6 Terra
- Reasoning effort: High

所有以下任务必须使用 Terra High：

- Research Planner；
- Demand Signal Extractor；
- Cluster Curator；
- Demand Analyst；
- Opportunity Analyst；
- 研究报告中的语义解释。

前端不提供模型切换。

模型配置仅允许后端配置文件/环境变量管理，并在“设置”页面以只读方式展示当前模型。

## 4.5 Embedding

Embedding 必须抽象为独立 `EmbeddingProvider`。

用途仅包括：

- Demand Atom 向量化；
- 相似度；
- Micro Cluster。

Embedding 结果不得直接用于：

- 判断是否有付费意愿；
- 判断市场大小；
- 判断产品值得做；
- 生成最终业务结论。

---

# 5. 总体系统架构

```text
NeedRadar Web
    |
    | REST + SSE
    v
NeedRadar FastAPI
    |
    +-- Research Planner ------ Terra High
    |
    +-- Crawl Job Manager ----- PostgreSQL Queue
    |                             |
    |                             v
    |                        MediaCrawler Worker
    |                             |
    |                             v
    +----------------------- Evidence Store
                                  |
                                  v
                           Rule Noise Filter
                                  |
                                  v
                      Demand Signal Extractor
                             Terra High
                                  |
                                  v
                         Demand Signal Store
                                  |
                                  v
                       Embedding / Micro Cluster
                                  |
                                  v
                         Cluster Curator
                           Terra High
                                  |
                                  v
                           Demand Cluster
                                  |
              +-------------------+-------------------+
              |                   |                   |
              v                   v                   v
          Scoring             Evidence           Snapshots
              |                   |                   |
              +-------------------+-------------------+
                                  |
                                  v
                       Opportunity Analyst
                           Terra High
                                  |
                                  v
                      Product / Content Opportunity
```

---

# 6. 核心业务对象

## 6.1 Research Project

表示一次完整市场研究。

示例：

`AI漫剧创作者真实需求研究`

一个 Research Project 包含：

- 原始研究问题；
- 目标用户；
- 研究维度；
- 搜索词；
- 平台选择；
- 采集任务；
- Evidence；
- Demand Signal；
- Demand Cluster；
- Opportunity；
- 报告。

## 6.2 Evidence

Evidence 是 NeedRadar 的最小可信证据单元。

任何需求判断必须最终可回溯到 Evidence。

Evidence 可以来源于：

- 帖子；
- 视频标题/描述；
- 一级评论；
- 二级评论；
- 回答；
- 后续 V0.2 的 OCR/转写。

## 6.3 Demand Signal

Demand Signal 表示从一条 Evidence 中提取出的一个“需求原子”。

同一条 Evidence 可以产生 0～N 个 Demand Signal。

## 6.4 Demand Cluster

Demand Cluster 表示大量 Demand Signal 聚合形成的一个稳定需求。

示例：

`角色跨镜头视觉一致性`

可以包含二级需求：

- 脸部一致性；
- 服装一致性；
- 发型一致性；
- 多角色防串人。

## 6.5 Opportunity

Opportunity 分两类：

- Product Opportunity
- Content Opportunity

Opportunity 必须引用一个或多个 Demand Cluster。

---

# 7. 页面与信息架构

V0.1 至少包含以下页面。

## 7.1 `/dashboard`

首页/研究项目列表。

必须展示：

- 新建研究入口；
- 最近研究项目；
- 项目状态；
- Demand Cluster 数；
- Evidence 数；
- 覆盖平台数；
- 最近更新时间。

项目卡片至少包含：

- 项目名称；
- 原始研究问题；
- 状态；
- 进度；
- Top Demand；
- 进入项目按钮。

## 7.2 `/research/new`

创建研究。

用户输入：

- 研究方向/问题；
- 可选补充说明。

点击“生成研究计划”后进入 Terra Research Planner。

## 7.3 `/research/{id}/plan`

研究计划确认页。

必须展示：

- 目标用户；
- 研究目标；
- 研究维度；
- 搜索词树；
- 平台；
- 采集深度；
- 时间范围；
- 预计任务数。

用户必须能够：

- 新增关键词；
- 删除关键词；
- 修改关键词；
- 启用/禁用关键词；
- 启用/禁用平台；
- 调整每关键词内容数量；
- 调整每内容评论数量；
- 开关二级评论。

点击“开始研究”后才真正创建 Crawl Jobs。

## 7.4 `/research/{id}/crawl`

采集中心。

必须按平台展示：

- 状态；
- 当前关键词；
- 已完成关键词数；
- 内容数；
- 评论数；
- 错误数；
- 当前阶段；
- 最近日志；
- 是否需要登录。

用户必须能够：

- 重试失败平台；
- 跳过平台；
- 停止未完成任务；
- 在需要登录时看到明确提示；
- 继续后续分析已有部分数据。

## 7.5 `/research/{id}/demands`

需求总览。

必须包含：

### 顶部统计

- Evidence 数；
- 有效 Demand Signal 数；
- 独立 creator_hash 数；
- Demand Cluster 数；
- 平台数。

### 需求列表

字段至少包含：

- 需求名称；
- Demand Score；
- Evidence 数；
- Demand Signal 数；
- 独立用户数；
- 平台覆盖；
- 30 日趋势；
- Payment Signal 数；
- Workaround 数；
- 当前状态。

支持：

- 排序；
- 平台筛选；
- Score 筛选；
- Signal Type 筛选；
- 搜索；
- 时间范围筛选。

### 需求地图

以树状结构或分组视图展示：

- 一级主题；
- 二级需求；
- Demand Score；
- 规模和趋势。

## 7.6 `/research/{id}/demands/{demandId}`

需求详情页。

必须包含：

1. 需求名称；
2. 一句话需求定义；
3. Demand Score；
4. Score 各维度拆解；
5. Evidence 数；
6. 独立用户数；
7. 平台数；
8. 趋势；
9. 用户场景；
10. 用户任务；
11. 用户目标；
12. 用户痛点；
13. Workaround；
14. 已有方案；
15. 已有方案不足；
16. Payment Signal；
17. 用户原话；
18. 原始来源链接；
19. 子需求；
20. “分析产品机会”按钮。

## 7.7 `/research/{id}/evidence`

Evidence 浏览器。

支持：

- 平台筛选；
- 内容/评论筛选；
- Signal Type；
- Demand Cluster；
- 时间；
- 点赞量；
- 关键词；
- 原始文本搜索。

每条 Evidence 必须能够看到：

- evidence_id；
- 平台；
- source_content_id；
- comment_id（如果有）；
- parent_comment_id（如果有）；
- creator_hash；
- 发布时间；
- 点赞数；
- 原始文本；
- 来源 URL；
- 搜索关键词；
- 对应 Demand Signal；
- 对应 Demand Cluster。

## 7.8 `/research/{id}/opportunities`

机会实验室。

分为：

- 产品机会；
- 内容机会。

产品机会至少展示：

- 名称；
- 对应需求；
- 用户；
- 问题；
- 当前 Workaround；
- 产品价值；
- MVP；
- 必需能力；
- 不建议首版做的能力；
- 技术难度；
- 外部模型/API依赖；
- 开发复杂度分析；
- 维护复杂度分析；
- 需要继续验证的假设；
- 引用 Evidence。

注意：技术难度等属于 Terra 分析意见，UI 应标记为“AI分析”，不能和真实统计混为一谈。

## 7.9 `/research/{id}/report`

研究报告。

自动组合：

- 研究范围；
- 数据质量；
- 数据覆盖；
- Top 需求；
- 快速增长需求；
- 强付费信号需求；
- 高 Workaround 需求；
- Existing Solution 不满意需求；
- 产品机会；
- 内容机会；
- 局限性；
- Evidence 引用。

支持：

- Markdown 导出；
- CSV/Excel 数据导出。

PDF 可留到 V0.2。

## 7.10 `/settings`

设置页面。

必须展示：

### 模型

只读：

- GPT-5.6 Terra
- reasoning = high

### 平台状态

- 小红书；
- 抖音；
- B站；
- 知乎；
- 微博；
- 贴吧；
- 快手。

状态包括：

- READY
- LOGIN_REQUIRED
- RUNNING
- ERROR
- UNKNOWN

### 数据

展示：

- Content 数；
- Comment 数；
- Demand Signal 数；
- Demand Cluster 数；
- Model Run 数。

可提供：

- 清理指定项目；
- 清理模型缓存；
- 重新计算评分。

---

# 8. Research Planner 需求

## 8.1 输入

用户输入：

- query：必填；
- context：可选。

示例：

`AI漫剧创作者有什么真实需求？`

## 8.2 Terra High 输出结构

Research Planner 必须输出结构化 JSON。

建议 Schema：

```json
{
  "project_title": "AI漫剧创作者真实需求研究",
  "target_user": "AI漫剧创作者",
  "research_goal": "识别AI漫剧创作流程中的高频真实痛点、当前解决方案、付费信号和产品机会",
  "dimensions": [
    "选题与剧本",
    "角色设计",
    "分镜",
    "生图",
    "生视频",
    "配音",
    "剪辑",
    "素材管理",
    "账号运营",
    "成本与变现"
  ],
  "keyword_groups": [
    {
      "type": "DOMAIN",
      "keywords": []
    },
    {
      "type": "WORKFLOW",
      "keywords": []
    },
    {
      "type": "PAIN",
      "keywords": []
    },
    {
      "type": "REQUEST",
      "keywords": []
    },
    {
      "type": "PAYMENT",
      "keywords": []
    },
    {
      "type": "COMPETITOR",
      "keywords": []
    }
  ],
  "recommended_platforms": ["xhs", "dy", "bili", "zhihu"],
  "research_notes": []
}
```

## 8.3 关键词类型

至少支持：

- DOMAIN
- WORKFLOW
- PAIN
- REQUEST
- PAYMENT
- COMPETITOR

后续可增加：

- ALTERNATIVE
- ABANDON
- PRICE
- BEGINNER
- ADVANCED

## 8.4 Research Planner 验收

必须满足：

- 不直接把关键词当成“已经验证的需求”；
- 用户确认前不启动爬取；
- 输出必须是可编辑结构；
- 关键词必须有 group；
- 不允许只有 3～5 个泛化词；
- 必须包含寻找“痛点/求助/价格/替代方案”的关键词策略。

---

# 9. MediaCrawler 集成需求

## 9.1 支持平台

V0.1 UI 应支持 MediaCrawler 当前可用的七个平台：

- xhs
- dy
- ks
- bili
- wb
- tieba
- zhihu

默认建议勾选：

- xhs
- dy
- bili
- zhihu

## 9.2 Crawl Job

Research Project 下每个平台生成独立 Crawl Job。

建议状态：

```text
PENDING
WAITING
RUNNING
LOGIN_REQUIRED
PARTIAL_SUCCESS
SUCCESS
FAILED
CANCELLED
```

## 9.3 采集参数

每个平台至少保存：

- keywords；
- crawler_type；
- max_notes_per_keyword；
- max_comments_per_content；
- enable_comments；
- enable_sub_comments；
- start_page；
- created_at；
- started_at；
- finished_at。

## 9.4 V0.1 调度规则

为了本地稳定性：

- MediaCrawler Job 默认全局并发 = 1；
- 多个平台按队列执行；
- 用户可以看到队列顺序；
- 失败只影响当前平台，不终止整个 Research Project；
- 已采集 Evidence 必须保留；
- `PARTIAL_SUCCESS` 数据允许进入后续分析。

## 9.5 登录

若 MediaCrawler 需要二维码/浏览器登录：

- Job 进入 `LOGIN_REQUIRED`；
- UI 明确展示“需要完成登录”；
- 用户完成后可点击继续/重新检测；
- 不允许静默失败。

## 9.6 数据去重

至少保证：

- `platform + content_id` 唯一；
- `platform + comment_id` 唯一（平台没有全局唯一 ID 时结合 content_id）；
- 重复 Research Project 采到相同 Evidence 时复用原 Evidence，但保留 project 关联。

---

# 10. Evidence 数据归一化

## 10.1 Source Content

统一 Schema 至少包含：

```text
id
platform
platform_content_id
content_type
title
content
creator_hash
publish_time
url
like_count
comment_count
favorite_count
share_count
view_count
source_keyword
raw_payload
created_at
updated_at
```

平台不存在某字段时允许 NULL。

不得用 0 代替未知值。

## 10.2 Source Comment

至少包含：

```text
id
platform
platform_comment_id
source_content_id
parent_comment_id
creator_hash
content
publish_time
like_count
sub_comment_count
source_keyword
raw_payload
created_at
updated_at
```

## 10.3 Evidence ID

每条用于分析的 Evidence 必须生成 NeedRadar 内部稳定 ID，例如：

`EV-<uuid>`

分析链路不得使用“文本本身”作为唯一键。

---

# 11. 噪声过滤

在调用 Terra High 前，必须先执行无模型规则过滤。

## 11.1 应过滤

- 空字符串；
- 纯 emoji；
- 纯 @；
- 纯数字；
- 纯“哈哈哈”等低信息回复；
- 完全重复文本；
- 明显抽奖/刷屏格式；
- 长度低于配置阈值且无需求关键词的文本。

## 11.2 不应过度过滤

以下短句仍可能是强需求，必须保留：

- “有工具吗？”
- “多少钱？”
- “怎么解决？”
- “求平替”
- “太贵了”
- “每次都要手改”

因此规则过滤必须提供白名单需求词机制。

## 11.3 过滤结果

保存：

- filtered = true/false；
- filter_reason；
- filter_version。

---

# 12. Demand Signal Engine

## 12.1 目标

Terra High 不直接总结“市场需求”，而是对 Evidence 做结构化需求原子提取。

## 12.2 Signal Type

V0.1 至少支持：

```text
PAIN
REQUEST
QUESTION
WORKAROUND
SWITCH
PRICE
WILLING_TO_PAY
CURRENTLY_PAYING
SEEKING_PAID_TOOL
FEATURE_REQUEST
FAILURE
TIME_COST
MANUAL_WORK
ABANDON
EXISTING_SOLUTION_COMPLAINT
```

同一 Evidence 可对应多个 Signal Type。

## 12.3 Demand Signal Schema

```json
{
  "evidence_id": "EV-xxx",
  "is_demand": true,
  "signal_types": ["PAIN", "WORKAROUND"],
  "user_type": "AI漫剧创作者",
  "scenario": "连续生成同一角色的多个镜头",
  "task": "生成连续镜头",
  "goal": "保持同一角色外貌与服装稳定",
  "pain": "人物在不同镜头中脸型和衣服发生变化",
  "current_solution": "重复上传角色参考图并多次重试",
  "solution_limitation": "仍然不能稳定保持一致",
  "desired_outcome": "一次绑定角色资产后跨镜头稳定复用",
  "pain_level": "HIGH",
  "recurrence": "REPEATED",
  "payment_signal": "NONE",
  "existing_solution": null,
  "existing_solution_sentiment": null,
  "evidence_quote": "原始证据中的相关片段",
  "confidence": "HIGH"
}
```

## 12.4 pain_level

固定枚举：

- LOW
- MEDIUM
- HIGH
- BLOCKING

## 12.5 recurrence

固定枚举：

- ONE_OFF
- OCCASIONAL
- REPEATED
- EVERY_TASK
- UNKNOWN

## 12.6 payment_signal

固定枚举：

- NONE
- PRICE_DISCUSSION
- SEEKING_PAID_TOOL
- WILLING_TO_PAY
- CURRENTLY_PAYING

## 12.7 existing_solution_sentiment

- POSITIVE
- NEUTRAL
- NEGATIVE
- SWITCHING
- UNKNOWN

## 12.8 关键约束

Terra 必须：

- 只基于当前 Evidence 提取；
- 不从自身知识补充用户没有说过的付费意愿；
- 不因为表达负面就自动判断愿意付费；
- 不把普通兴趣/赞美强行判为需求；
- evidence_quote 必须来自原文；
- 输出严格 JSON；
- 无需求时明确 `is_demand=false`。

## 12.9 批处理

禁止“一条评论一次 API”。

V0.1 应支持批处理，默认策略：

- 每批 40～100 条 Evidence；
- 根据字符/token 自动缩小；
- 每个输入 Evidence 有唯一 evidence_id；
- 输出必须逐条对应；
- 缺失项进入重试队列。

## 12.10 Model Run 缓存

以以下信息计算 input hash：

- prompt_version；
- model；
- reasoning；
- evidence_ids；
- evidence_text_hash。

相同输入不得重复调用模型，除非用户选择“强制重新分析”。

---

# 13. Embedding 与 Micro Clustering

## 13.1 Embedding 文本

禁止只对原始评论全文做 Embedding。

建议对标准化 Demand Atom 做 Embedding：

```text
user_type
+
scenario
+
task
+
goal
+
pain
+
desired_outcome
```

## 13.2 V0.1 算法

允许沿用/参考 DeepPoint：

- Embedding；
- Cosine；
- DBSCAN。

但必须封装为：

`ClusteringProvider`

为后续替换 HDBSCAN/ANN 保留空间。

## 13.3 大数据保护

若 Demand Signal 超过配置阈值（建议默认 20,000）：

- 不允许直接生成巨大 NxN distance matrix；
- 必须切换到更节省内存的聚类路径或分层聚类；
- V0.1 若暂未实现，应明确限制单次聚类数据量并在 UI 提示。

---

# 14. Cluster Curator

Micro Cluster 形成后，必须调用 Terra High 对 Cluster 进行语义整理。

Terra High 负责：

- 合并重复 Cluster；
- 拆分语义过宽 Cluster；
- 命名；
- 生成 parent/child 需求关系；
- 识别“同一痛点的不同表现”；
- 识别“看似相似但其实不同任务”的 Cluster。

禁止 Terra：

- 直接删除 Evidence；
- 修改原 Evidence；
- 凭空增加 Signal；
- 直接生成最终 Demand Score。

Cluster Curator 的每一次合并/拆分必须保存 Model Run 记录。

---

# 15. Demand Cluster 数据结构

至少包含：

```text
id
research_project_id
name
summary
parent_cluster_id
status
signal_count
evidence_count
unique_creator_count
platform_count
first_seen_at
last_seen_at
score
score_version
created_at
updated_at
```

Cluster 与 Signal 必须使用多对多关联表，不能复制 Signal 数据。

---

# 16. Demand Score v1

## 16.1 核心原则

Demand Score 必须：

- 程序计算；
- 0～100；
- 可解释；
- 每个维度可展开；
- 可以版本化；
- 数据不足时明确显示，而不是自动填 0。

## 16.2 初始维度

| 维度 | 权重 |
|---|---:|
| Breadth | 20 |
| Recurrence | 15 |
| Pain | 15 |
| Workaround | 10 |
| Payment | 15 |
| Unsatisfied Existing Solution | 10 |
| Trend | 10 |
| Cross-platform | 5 |
| 合计 | 100 |

## 16.3 Breadth

由以下数据计算：

- signal_count；
- unique_creator_count。

建议使用项目内 P95 + log1p 归一化，避免一个极大 Cluster 压制所有其他需求。

示意：

```text
norm(x) = clip(log1p(x) / log1p(project_p95(x)), 0, 1)
Breadth = 10 * norm(signal_count) + 10 * norm(unique_creator_count)
```

若 P95 <= 0，则该项视为数据不足。

## 16.4 Recurrence

将 recurrence 映射：

- ONE_OFF = 0.1
- OCCASIONAL = 0.35
- REPEATED = 0.7
- EVERY_TASK = 1.0
- UNKNOWN = 不计入有效样本

取 Cluster 内有效 Signal 加权均值 × 15。

## 16.5 Pain

映射：

- LOW = 0.1
- MEDIUM = 0.4
- HIGH = 0.75
- BLOCKING = 1.0

取有效 Signal 加权均值 × 15。

## 16.6 Workaround

统计以下 Signal：

- WORKAROUND
- MANUAL_WORK
- TIME_COST
- FAILURE
- ABANDON

结合：

- workaround_signal_count；
- workaround_unique_creator_count。

采用项目内归一化，最大 10 分。

## 16.7 Payment

仅统计有明确证据的：

- PRICE_DISCUSSION = 0.35
- SEEKING_PAID_TOOL = 0.65
- WILLING_TO_PAY = 1.0
- CURRENTLY_PAYING = 0.9

不得使用 Terra 主观“我觉得会付费”作为分数来源。

结合有效 Signal 数和独立用户数归一化，最大 15 分。

## 16.8 Unsatisfied Existing Solution

依据：

- EXISTING_SOLUTION_COMPLAINT；
- SWITCH；
- existing_solution_sentiment = NEGATIVE；
- existing_solution_sentiment = SWITCHING。

最大 10 分。

## 16.9 Trend

需要 Demand Snapshot 历史数据。

至少支持：

- 7 日；
- 30 日；
- 90 日。

若历史不足：

- UI 显示“数据不足”；
- Score 计算时对现有维度重新归一化权重；
- 禁止把 Trend 当 0 分。

## 16.10 Cross-platform

建议：

```text
1平台 = 0.25
2平台 = 0.50
3平台 = 0.75
>=4平台 = 1.0
```

× 5。

## 16.11 权重重分配

如果某维度缺少有效数据：

- 从总分中暂时移除该维度；
- 剩余维度按原权重比例重新缩放至 100；
- UI 必须展示“本次评分基于哪些维度”；
- 不得静默处理。

## 16.12 Score Version

所有 Demand Cluster 保存：

`score_version = "v1"`

后续公式修改不得覆盖历史版本。

---

# 17. Demand Snapshot / 趋势

每次研究完成或用户手工刷新时，为每个 Demand Cluster 保存 Snapshot。

至少保存：

```text
cluster_id
snapshot_date
signal_count
evidence_count
unique_creator_count
platform_count
payment_signal_count
workaround_signal_count
score
```

趋势展示至少支持：

- 7 日变化；
- 30 日变化；
- 90 日变化；
- 首次发现日期；
- 最近增长方向。

如果同一个需求在不同 Research Project 中语义相同，V0.1 不强制跨项目统一；V0.2 再考虑全局 Demand Identity。

---

# 18. Demand Analyst

Demand Detail 页面需要调用 Terra High 对 Cluster 做解释。

输入必须包括：

- Cluster 基础统计；
- 子需求；
- 代表 Evidence；
- Workaround Evidence；
- Payment Evidence；
- Existing Solution Evidence；
- 平台分布；
- 时间分布。

输出至少包括：

- 需求定义；
- 典型用户；
- 核心场景；
- 用户任务；
- 用户目标；
- 痛点；
- 为什么痛；
- 当前 Workaround；
- Workaround 为什么不好；
- 已有方案；
- 对已有方案的不满；
- 支持结论的 Evidence ID；
- 仍然不确定的问题。

所有核心结论必须引用 Evidence ID。

---

# 19. Opportunity Engine

## 19.1 触发

用户点击：

`分析产品机会`

才执行。

不要对所有需求自动全量调用 Terra，避免浪费。

## 19.2 Product Opportunity 输入

必须包含：

- Demand Cluster；
- Demand Score；
- Score breakdown；
- 代表 Evidence；
- Payment Signal；
- Workaround；
- Existing Solution；
- Unsatisfied Signal；
- 趋势；
- 用户自行配置的个人开发约束。

## 19.3 默认个人开发约束

可在设置中配置，初始默认：

```text
team_size = 1
employment_mode = spare_time
weekly_hours = 15
personal_gpu = false
mvp_target_weeks = 4
```

这些属于开发约束，不应影响 Demand Score，只影响 Opportunity 分析。

## 19.4 Product Opportunity 输出

至少包括：

- opportunity_name；
- target_user；
- problem；
- evidence_summary；
- current_workaround；
- value_proposition；
- mvp_features；
- non_goals；
- technical_dependencies；
- implementation_complexity；
- maintenance_complexity；
- major_risks；
- validation_hypotheses；
- validation_plan；
- evidence_ids。

## 19.5 Content Opportunity

针对自媒体选题，输出：

- 用户最常问的问题；
- 高增长话题；
- Workaround 教程需求；
- 工具对比需求；
- 入门需求；
- 价格/成本问题；
- 容易引发评论的争议点；
- 对应 Evidence。

不得把“热”自动等于“值得做产品”。

---

# 20. Model Run 记录

所有 Terra High 调用必须保存 Model Run。

至少包含：

```text
id
research_project_id
run_type
model
reasoning_effort
prompt_version
input_hash
input_refs
request_payload
response_payload
status
error
input_tokens
output_tokens
reasoning_tokens
started_at
finished_at
```

`run_type` 至少支持：

```text
RESEARCH_PLANNER
DEMAND_SIGNAL
CLUSTER_CURATOR
DEMAND_ANALYST
OPPORTUNITY_ANALYST
REPORT_ANALYST
```

需要支持：

- 查看失败；
- 重试；
- 强制重新运行；
- Prompt 版本对比。

---

# 21. 数据库核心表

V0.1 至少包含以下 11 张业务表。

## 21.1 research_project

核心字段：

```text
id UUID PK
name
original_query
context
status
planner_version
created_at
updated_at
completed_at
```

## 21.2 research_query

```text
id
research_project_id
group_type
keyword
enabled
source = AI | USER
created_at
```

## 21.3 crawl_job

```text
id
research_project_id
platform
status
config_json
progress_json
error
created_at
started_at
finished_at
```

## 21.4 source_content

见 Evidence Schema。

## 21.5 source_comment

见 Evidence Schema。

## 21.6 demand_signal

保存 Demand Signal Extractor 的结构化结果。

## 21.7 demand_cluster

保存稳定需求簇。

## 21.8 demand_cluster_signal

```text
cluster_id
signal_id
membership_type
created_at
```

## 21.9 demand_snapshot

保存趋势快照。

## 21.10 opportunity

```text
id
research_project_id
cluster_id
type = PRODUCT | CONTENT
payload_json
model_run_id
created_at
updated_at
```

## 21.11 model_run

保存所有模型调用。

## 21.12 关联表说明

如同一 Source Evidence 被多个 Research Project 使用，需要额外项目关联表，禁止复制源数据。

建议增加：

- `research_source_content`
- `research_source_comment`

若实现简单，可在 V0.1 阶段先在 source 表增加 `research_project_id`，但必须在 OpenSpec 设计阶段明确是否接受未来迁移成本。

---

# 22. Research Project 状态机

建议：

```text
DRAFT
PLANNING
PLAN_READY
CRAWLING
CRAWL_PARTIAL
ANALYZING_SIGNALS
CLUSTERING
CURATING_CLUSTERS
SCORING
READY
FAILED
CANCELLED
```

状态转换必须由后端统一管理。

前端不得自己推测状态。

允许：

`CRAWL_PARTIAL → ANALYZING_SIGNALS`

表示部分平台失败但用户选择继续分析。

---

# 23. API 需求

以下为建议 REST API，不要求路径完全一致，但能力必须覆盖。

## 23.1 Project

```text
POST   /api/research
GET    /api/research
GET    /api/research/{id}
DELETE /api/research/{id}
```

## 23.2 Planner

```text
POST /api/research/{id}/plan/generate
PUT  /api/research/{id}/plan
POST /api/research/{id}/start
```

## 23.3 Crawl

```text
GET  /api/research/{id}/crawl-jobs
POST /api/crawl-jobs/{jobId}/retry
POST /api/crawl-jobs/{jobId}/cancel
POST /api/crawl-jobs/{jobId}/resume
```

## 23.4 Analysis

```text
POST /api/research/{id}/analyze-signals
POST /api/research/{id}/cluster
POST /api/research/{id}/score
POST /api/research/{id}/reanalyze
```

## 23.5 Demand

```text
GET  /api/research/{id}/demands
GET  /api/research/{id}/demands/{demandId}
POST /api/research/{id}/demands/{demandId}/analyze
```

## 23.6 Evidence

```text
GET /api/research/{id}/evidence
GET /api/evidence/{evidenceId}
```

## 23.7 Opportunity

```text
POST /api/research/{id}/demands/{demandId}/opportunities
GET  /api/research/{id}/opportunities
```

## 23.8 Report

```text
GET  /api/research/{id}/report
POST /api/research/{id}/report/regenerate
GET  /api/research/{id}/export/markdown
GET  /api/research/{id}/export/csv
```

## 23.9 Events

建议：

```text
GET /api/research/{id}/events
```

使用 SSE 推送：

- 项目状态；
- Crawl Job 状态；
- 当前关键词；
- 计数；
- 分析批次；
- 聚类进度；
- 错误；
- 登录需求。

---

# 24. 前端交互要求

## 24.1 总原则

NeedRadar 是数据研究产品，UI 应：

- 信息密度高；
- 分层明确；
- 以“证据 → 需求 → 机会”为主线；
- 不做无意义的 AI 聊天框中心设计；
- 不用大面积装饰图取代真实数据；
- 关键数字必须可点击查看组成。

## 24.2 导航

建议左侧导航：

```text
Dashboard
Research
Demands
Opportunities
Settings
```

进入 Project 后二级导航：

```text
Overview
Plan
Collection
Demands
Evidence
Opportunities
Report
```

## 24.3 进度可见

任何超过数秒的任务必须有：

- 当前阶段；
- 完成数量；
- 失败数量；
- 当前操作；
- 可取消/重试状态。

禁止只有一个无限 Spinner。

## 24.4 AI 与真实数据区分

UI 必须视觉区分：

### 真实数据

- Evidence 数；
- 用户数；
- Signal 数；
- 趋势；
- 平台；
- 时间；
- 点赞；
- 评论原文。

### AI 分析

- 根因；
- 产品机会；
- 技术难度；
- 维护复杂度；
- 建议。

AI 分析模块需要标注：

`Terra High 分析`

避免用户把模型判断当统计事实。

---

# 25. 任务容错

## 25.1 采集失败

若某个平台失败：

- 保存已获取数据；
- Crawl Job = PARTIAL_SUCCESS 或 FAILED；
- Project 不自动失败；
- 用户可以选择“基于已有数据继续”。

## 25.2 模型批次失败

若 Demand Signal 某批失败：

- 已成功批次不得回滚；
- 失败批次进入 retry；
- 状态记录 error；
- 最多自动重试配置次数；
- 仍失败则允许用户从 UI 手工重试。

## 25.3 JSON 解析失败

不能像普通 Prompt 应用一样生成默认“Medium”结论。

必须：

1. 尝试 JSON repair；
2. 失败则重试模型；
3. 仍失败则标记 Model Run FAILED；
4. 不产生假的 Demand Signal。

## 25.4 数据不足

Demand Detail 必须显示：

- 样本量；
- 数据覆盖；
- 缺失平台；
- 时间跨度；
- Score 缺失维度。

不允许仅因为样本少就自动说“没有需求”。

---

# 26. 可重复与可追踪

以下所有对象必须版本化或可追踪：

- Research Plan；
- Prompt；
- Demand Signal Extractor；
- Clustering；
- Cluster Curator；
- Score Formula；
- Opportunity。

用户必须能够回答：

> “这个需求为什么会出现在Top 10？”

至少可追踪到：

```text
Demand Score
 → 各维度
 → Demand Signals
 → Evidence
 → 原始帖子/评论
```

以及：

```text
Demand Summary
 → Model Run
 → Prompt Version
 → 输入 Evidence
```

---

# 27. 性能与资源要求

V0.1 为本地单用户系统。

## 27.1 前端

- 页面切换应立即反馈；
- 大列表必须分页/虚拟化；
- 不一次在 DOM 渲染数万 Evidence。

## 27.2 数据库

必须对以下字段建立索引：

- project_id；
- platform；
- platform_content_id；
- platform_comment_id；
- creator_hash；
- publish_time；
- signal_type；
- cluster_id；
- score。

## 27.3 模型调用

- Demand Signal 必须批处理；
- Model Run 缓存；
- 相同输入不得重复调用；
- 用户可手工强制重跑。

## 27.4 Worker

初始：

- crawler concurrency = 1；
- analysis concurrency = 可配置，建议 2；
- clustering concurrency = 1。

---

# 28. 日志与可观察性

用户界面不需要展示底层全部技术日志，但后台必须记录。

至少：

```text
timestamp
project_id
job_id
stage
level
message
metadata
```

前端展示简化后的任务事件。

开发模式允许展开技术日志。

---

# 29. 导出需求

## 29.1 Markdown

包含完整研究报告和 Top Demand。

## 29.2 CSV / Excel

至少导出：

### Sheet/CSV 1：Demands

- demand_id
- name
- score
- signal_count
- unique_creator_count
- platform_count
- trend
- payment_signal_count
- workaround_count

### Sheet/CSV 2：Signals

- signal_id
- demand_id
- evidence_id
- signal_types
- task
- pain
- workaround
- payment_signal

### Sheet/CSV 3：Evidence

- evidence_id
- platform
- source_url
- creator_hash
- publish_time
- text
- like_count

---

# 30. Evaluation / Gold Set

NeedRadar 必须从 V0.1 就保留评估能力。

## 30.1 Gold Set

建立：

`evals/gold_set/`

人工标注真实社交评论。

至少字段：

```text
evidence_text
is_demand
signal_types
user_type
scenario
task
goal
pain
workaround
pain_level
recurrence
payment_signal
```

## 30.2 第一阶段指标

至少评估：

- Demand Detection Precision；
- Demand Detection Recall；
- Payment Signal Precision/Recall；
- Signal Type F1；
- JSON Success Rate；
- Cluster Purity（人工抽样）；
- Cluster Merge Accuracy（人工抽样）。

## 30.3 Prompt 更新原则

任何 Demand Signal Prompt 大改后，必须先在 Gold Set 上跑回归，再用于正式分析。

---

# 31. 未来 V0.2 预留能力

V0.1 不实现，但架构需预留：

## 31.1 socai Deep Verify

在 Demand Detail 增加：

`深度验证`

用于让 socai：

- 重新打开重点帖子；
- 深读正文；
- 展开更多评论/回复；
- OCR；
- 转写视频；
- 补充 Evidence。

## 31.2 Trend Signal

加入：

- 热榜；
- RSS；
- 内容供给变化；
- 外部趋势。

与 Demand Signal 分开存储。

## 31.3 CreatorOS 联动

NeedRadar 发现需求后，可把“内容机会”发送到未来的自媒体账号运营产品中。

例如：

```text
真实市场讨论
 → NeedRadar
 → Content Opportunity
 → CreatorOS 选题库
 → 制作/发布
 → 新评论
 → NeedRadar
```

---

# 32. V0.1 建议开发阶段（OpenSpec Change 划分）

后续 OpenSpec 建议不要一次创建一个巨大 change。

推荐拆成以下 Changes。

## CHANGE-001：Foundation

范围：

- monorepo/project skeleton；
- Next.js Web；
- FastAPI；
- PostgreSQL；
- Alembic；
- 基础数据模型；
- Project CRUD；
- SSE基础能力；
- Dashboard。

完成标准：

用户可以创建一个空 Research Project，并在 UI 中看到状态。

## CHANGE-002：Research Planner

范围：

- Terra High Provider；
- Research Planner Prompt；
- Plan Schema；
- 可视化编辑关键词树；
- 平台配置。

完成标准：

输入“AI漫剧创作者”，系统生成可编辑 Research Plan，用户确认后保存。

## CHANGE-003：MediaCrawler Adapter

范围：

- Crawl Job；
- Worker；
- MediaCrawler 子进程；
- 登录状态；
- 进度；
- Source Content / Comment 入库；
- 采集中心 UI。

完成标准：

从 UI 启动研究，可完成至少一个平台采集并看到真实 Evidence。

## CHANGE-004：Demand Signal Engine

范围：

- 噪声过滤；
- Terra High Demand Signal；
- Batch；
- Model Run；
- 缓存；
- Retry；
- Demand Signal 数据表；
- Evidence 页面 Signal 展示。

完成标准：

系统能从真实评论批量提取结构化 Demand Signal。

## CHANGE-005：Clustering & Demand Graph

范围：

- Embedding Provider；
- Micro Cluster；
- Terra Cluster Curator；
- Demand Cluster；
- parent/child；
- Cluster 与 Signal 关系。

完成标准：

数千 Demand Signal 可被归并为可浏览需求树。

## CHANGE-006：Scoring & Trend

范围：

- Demand Score v1；
- Score breakdown；
- Snapshot；
- 数据不足处理；
- 排序筛选。

完成标准：

Top Demand 可以按真实结构化数据排名，并能解释每一分从哪里来。

## CHANGE-007：Demand UX

范围：

- Demand List；
- Demand Map；
- Demand Detail；
- Evidence Drawer；
- Workaround；
- Payment；
- platform/time filters。

完成标准：

用户可以从总览进入一个需求，并一直追溯到原始评论。

## CHANGE-008：Opportunity Lab

范围：

- Terra Opportunity Analyst；
- Product Opportunity；
- Content Opportunity；
- 用户个人开发约束；
- UI。

完成标准：

对一个 Demand 可以生成带 Evidence 的产品/MVP分析。

## CHANGE-009：Report & Export

范围：

- Research Report；
- Markdown；
- CSV/Excel；
- 数据质量信息。

完成标准：

可以导出完整研究成果。

## CHANGE-010：Evaluation

范围：

- Gold Set；
- Prompt Eval；
- Demand Precision/Recall；
- Payment Signal；
- Cluster人工检查流程。

完成标准：

Prompt和模型链路具有可重复评估能力。

---

# 33. V0.1 端到端验收场景

以“AI漫剧创作者”为强制验收案例。

## Given

用户打开 NeedRadar Dashboard。

## When

用户创建研究：

`AI漫剧创作者有什么真实需求？`

## Then 1：Plan

系统通过 Terra High 生成：

- 目标用户；
- 研究维度；
- 至少 6 类关键词组；
- 默认平台。

用户能够修改并确认。

## Then 2：Collection

用户点击“开始研究”。

系统：

- 生成平台 Crawl Job；
- 后台调用 MediaCrawler；
- UI 实时展示进度；
- Source Content/Comment 入库；
- 某个平台失败时仍保留其他平台数据。

## Then 3：Demand Signal

系统：

- 过滤低质量文本；
- 批量提交 Terra High；
- 提取结构化 Demand Signal；
- 所有 Signal 都保留 Evidence ID。

## Then 4：Cluster

系统：

- Embedding；
- Micro Cluster；
- Terra High 合并/拆分；
- 输出可浏览 Demand Cluster。

## Then 5：Score

系统：

- 程序计算 Demand Score；
- UI 可展开各维度；
- 缺少历史趋势时明确显示数据不足。

## Then 6：Demand Detail

用户点击：

`角色一致性`

可以看到：

- Signal 数；
- 独立用户数；
- 平台数；
- Score；
- Workaround；
- Payment Signal；
- 用户原话；
- 原始链接。

## Then 7：Opportunity

点击“分析产品机会”。

Terra High 基于实际 Demand 数据与 Evidence，生成：

- 产品机会；
- MVP；
- 技术难度；
- 验证计划；
- Evidence 引用。

## Then 8：Report

用户可以导出本次研究 Markdown + 表格数据。

整个过程无需执行命令行。

---

# 34. 不可违反的验收红线

以下任一情况出现，应视为需求未满足：

1. 用户需要手工运行 MediaCrawler 才能完成正常使用。
2. Demand Score 主要由 Terra 主观打分。
3. 一个需求无法追溯到真实 Evidence。
4. 直接把普通评论量当成需求量。
5. 付费意愿来自 AI 推测，而不是原始 Signal。
6. 采集失败后 UI 显示“没有相关需求”。
7. JSON 解析失败时系统自动生成默认“Medium”结论。
8. 聚类后只保留摘要，丢失原始 Signal/Evidence。
9. 前端只有一个输入框和一张结果表，没有项目、采集、需求、证据、机会等完整可视化流程。
10. 模型切换暴露给普通用户并形成多模型复杂路由。
11. 需求地图的分数无法解释。
12. 使用字符串文本作为 Evidence 唯一标识，导致相同评论覆盖来源。
13. 重新分析时覆盖旧 Model Run，无法追踪版本。
14. 部分平台失败导致整项研究全部丢失。
15. 用“样本不足”直接等价于“没有需求”。

---

# 35. 开发优先级

若开发资源有限，优先级必须按以下顺序：

## P0

- Research Project
- Planner
- MediaCrawler
- Evidence
- Demand Signal
- Cluster
- Demand Score
- Demand List / Detail
- Evidence Trace

## P1

- Opportunity
- Report
- Trend Snapshot
- Export
- Gold Set/Eval

## P2

- socai Deep Verify
- Trend Signal
- CreatorOS联动
- 更复杂的全局Demand Graph

---

# 36. 最终产品原则

NeedRadar 不追求告诉用户：

> “AI认为这个项目有92%的成功概率。”

NeedRadar 应该告诉用户：

> “过去一段时间，在这些平台、这些帖子和这些评论中，有多少独立用户反复表达了同一种问题；他们在什么场景遇到；现在怎么绕过去；哪些人讨论价格或正在付费；哪些现有方案仍然让他们不满意；这些结论对应哪些真实证据。”

然后再由 Terra High 基于这些真实证据帮助用户理解：

> “这个问题可能对应什么产品机会，以及下一步应该验证什么。”

**Evidence 是事实层，Demand 是结构层，Score 是计算层，Terra 是解释层，Opportunity 是决策辅助层。四层不能混淆。**

---

# 37. 后续 OpenSpec / Codex 使用约定

后续新对话中，如基于本说明书生成 Codex 指令，建议强制要求：

1. 先读取本说明书；
2. 检查目标代码仓库现状；
3. 使用 OpenSpec 创建单一明确 Change；
4. 每次 Change 只覆盖本说明书第 32 节中的一个阶段或一个足够小的子阶段；
5. 不跨 Change 偷做未来能力；
6. 不擅自更换大模型；
7. Terra 必须固定 High；
8. 不把 DeepPoint 现有 scoring 作为最终实现；
9. 不把 MediaCrawler UI 直接暴露成主产品 UI；
10. 每次提交必须包含对应测试与验收结果；
11. 任何 Schema 改动必须有 migration；
12. 所有 LLM Prompt 必须版本化；
13. 所有 Demand Score 逻辑必须有单元测试；
14. 所有 Research Project 状态转换必须有测试；
15. 每次 Change 完成后输出：实现范围、文件变更、数据库变更、测试结果、未完成项、是否满足验收标准。

