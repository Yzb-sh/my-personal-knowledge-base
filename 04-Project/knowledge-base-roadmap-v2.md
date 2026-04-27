# 个人知识库后续发展计划书 v2.0

## Context

用户是一位量化策略研发从业者，已完成知识库基础搭建（Phase 1）：
- Vault 结构、9 个模板、6 个 MOC、CLAUDE.md 就位
- 8 条永久笔记（SQL 数据库方向 + Parquet/Python 方向）
- Obsidian 配置好 Templater + Calendar + Dataview
- Git 仓库初始化（1 次提交），但未推送到远程

用户现在希望将知识库发展为**移动可访问、AI 增强的个人知识系统**，具体需求：
1. **手机端交互**：通过小龙虾（qclaw/腾讯版OpenClaw）在 iPhone 上与知识库对话
2. **智能问答**：提问时自动检索已有笔记，基于笔记内容回答
3. **自动创建笔记**：新知识点由 LLM 自动生成符合 Zettelkasten 规范的原子笔记
4. **持久化保存**：计划书保存到项目中，可在新 Claude Code 会话中继续实施

**用户环境**：
- iOS (iPhone) 作为移动端
- 24 小时开机的 Windows PC 作为服务端
- QClaw 已配置微信和飞书通道（网关端口 28789）
- 开发经验以 Python 脚本为主，无 Web 框架经验
- 每周投入 <5 小时

---

## Phase 0：立即任务（今天，约 1 小时）

### 0.1 文件名去时间戳

**现状**：`202604271500 - Row Storage vs Column Storage.md` -- 图谱中节点很长
**目标**：`Row Storage vs Column Storage.md` -- 干净短标题

**操作**：
1. 重命名 03-Zettel/ 下所有 8 条笔记，去掉 `YYYYMMDDHHmm - ` 前缀
2. 更新所有 MOC 文件中对这些笔记的 wikilinks
3. 更新笔记之间的互相引用链接
4. 更新 CLAUDE.md 中的命名规则：永久笔记文件名 = 描述性标题，时间信息仅保留在 frontmatter 的 `created` 字段

**受影响文件**：
```
03-Zettel/Row Storage vs Column Storage.md          (原 202604271500 - ...)
03-Zettel/OLTP vs OLAP.md                           (原 202604271510 - ...)
03-Zettel/Database Partitioning.md                   (原 202604271520 - ...)
03-Zettel/Time-Series Database.md                    (原 202604271530 - ...)
03-Zettel/MongoDB vs MySQL vs ClickHouse.md          (原 202604271540 - ...)
03-Zettel/L2 Market Data Storage Strategy.md         (原 202604271550 - ...)
03-Zettel/Parquet File Format.md                     (原 202604271600 - ...)
03-Zettel/Processing Parquet with Python.md          (原 202604271610 - ...)
01-Atlas/MOC-SQL.md                                  (更新链接)
01-Atlas/MOC-Python.md                               (更新链接)
01-Atlas/MOC-Quantitative-Strategy.md                (更新链接)
CLAUDE.md                                            (更新命名规则)
09-Templates/T-Zettel.md                             (更新文件名示例)
```

### 0.2 提交并推送到 GitHub

1. 创建 GitHub 私有仓库
2. `git remote add origin <url>`
3. 提交所有未跟踪和已修改的文件
4. `git push -u origin main`

---

## 总体架构设计

```
┌─────────────────────────────────────────────────────┐
│                    iPhone                            │
│  ┌──────────────┐    ┌──────────────┐               │
│  │   微信 App    │    │ Obsidian App │               │
│  │  (AI 对话)    │    │  (阅读笔记)   │               │
│  └──────┬───────┘    └──────┬───────┘               │
│         │                   │ (git pull/push)        │
└─────────┼───────────────────┼────────────────────────┘
          │ (微信通道)         │
          ▼                   ▼
┌─────────────────────────────────────────────────────┐
│              Windows PC (24h)                        │
│                                                      │
│  ┌──────────────────────────────────────┐            │
│  │  QClaw Gateway (port 28789)          │            │
│  │  ├─ kb-qa skill    (知识问答)        │            │
│  │  ├─ kb-add skill   (创建笔记)        │            │
│  │  ├─ kb-quiz skill  (自我测验)        │            │
│  │  └─ kb-review skill(每日复习)        │            │
│  └──────────────┬───────────────────────┘            │
│                 │ exec: python kb_tool.py ...        │
│                 ▼                                     │
│  ┌──────────────────────────────────────┐            │
│  │  FastAPI Server (port 28790)         │            │
│  │  ├─ POST /search   (语义搜索)        │            │
│  │  ├─ POST /check    (知识存在性检查)   │            │
│  │  ├─ POST /create   (生成并保存笔记)   │            │
│  │  ├─ GET  /review   (获取复习项目)     │            │
│  │  └─ GET  /stats    (知识图谱统计)     │            │
│  └──────────────┬───────────────────────┘            │
│                 │                                     │
│     ┌───────────┼──────────────┐                     │
│     ▼           ▼              ▼                     │
│  ChromaDB   Claude API    Knowledge Base             │
│  (向量索引)   (笔记生成)    (Markdown 文件)            │
│     └───────────┴──────────────┘                     │
│                 │ git commit + push                   │
│                 ▼                                     │
│           GitHub / Gitee                              │
└─────────────────────────────────────────────────────┘
```

### 移动端分工

| 任务 | 界面 | 理由 |
|------|------|------|
| AI 对话（问答、创建笔记、测验） | 微信 → QClaw | 随时可用，无需打开其他 App |
| 阅读笔记（完整格式） | Obsidian iOS | 富 Markdown、图谱视图、反向链接 |
| 浏览 MOC 和知识结构 | Obsidian iOS | 可视化知识图谱 |
| 每日复习推送 | 微信推送（QClaw cron） | 被动提醒，无需主动打开 |
| 深度编辑 | PC 端 Obsidian / Claude Code | 复杂操作在桌面端完成 |

### 关键设计原则

1. **微信通道已是远程可用的**：微信消息经腾讯服务器路由，QClaw 在任何地方都可访问，不需要 Tailscale 或内网穿透
2. **单一写入入口**：所有 AI 创建的笔记通过 FastAPI → Git commit → push，避免冲突
3. **CLI 桥接**：QClaw 通过 `python kb_tool.py` CLI 工具调用 FastAPI，而非直接 HTTP 请求，方便调试
4. **移动端只读**：iPhone 上只读取笔记（git pull），不直接编辑，所有创建通过微信 → QClaw

---

## Phase 1：基础设施（第 1-2 周，约 8-10 小时）

### 前提条件

```bash
pip install anthropic chromadb sentence-transformers python-frontmatter
```

### 交付物

#### 1. `10-System/scripts/indexer.py` -- ChromaDB 索引引擎

功能：
- 解析所有 Markdown 文件的 frontmatter（python-frontmatter）
- 按 `##` 标题拆分为块（Core Definition / Technical Details / Application Example 等）
- 使用 `paraphrase-multilingual-MiniLM-L12-v2`（120MB，支持中英文）嵌入每个块
- 存入 ChromaDB，附带元数据：`{file_path, title, tags, domain, chunk_type}`
- 支持 `python indexer.py build`（全量重建）和 `python indexer.py update`（增量更新）

关键依赖：chromadb, sentence-transformers, python-frontmatter

索引策略（每条笔记拆分为多个块）：
```
笔记文件 → frontmatter 提取 → 按 ## 标题分块 → 每块嵌入 → ChromaDB 存储
```

#### 2. `10-System/scripts/server.py` -- FastAPI 后端

运行在 `localhost:28790`，端点：

```
POST /search
  Body: {"query": "列存储原理", "top_k": 5}
  Response: [{"title": "...", "file": "...", "score": 0.92, "snippet": "..."}]

POST /check
  Body: {"topic": "Kelly Criterion"}
  Response: {"exists": bool, "note": "...", "score": 0.87}

POST /index/rebuild
  Response: {"notes_indexed": 8, "chunks_created": 24}
```

启动方式：`uvicorn server:app --host 127.0.0.1 --port 28790`

#### 3. `10-System/scripts/kb_tool.py` -- CLI 工具（QClaw 调用入口）

```bash
python kb_tool.py search "列存储原理"
python kb_tool.py check "Kelly Criterion"
```

内部用 `requests.post("http://localhost:28790/search", ...)` 调用 FastAPI。

#### 4. QClaw Skill：`kb-qa`（知识库问答）

创建 `C:\Users\yzb\.qclaw\skills\kb-qa\SKILL.md`：

触发条件：用户提出关于知识领域的问题（检测数学/编程/SQL/量化关键词）
动作流程：
1. 执行 `python D:\...\kb_tool.py search "用户问题"`
2. 如果找到匹配笔记（score > 0.75）：返回笔记内容摘要
3. 如果未找到：告知用户该知识点尚未收录，询问是否需要创建笔记

#### 5. QClaw 项目配置

在 `C:\Users\yzb\.qclaw\workspace\projects\` 创建 `personal-knowledge-base` 项目目录，包含：
- `README.md` -- 项目说明
- `AUTONOMOUS_CONFIG.json` -- 配置 `codeRoot` 指向 `D:\YZB\Projects\my-personal-knowledge-base`
- `agent_templates/` -- 知识库助手模板

### 本阶段验证

```bash
# 1. 索引构建
python indexer.py build
# 期望输出：Indexed 8 notes, 24 chunks

# 2. 启动服务器
uvicorn server:app --host 127.0.0.1 --port 28790

# 3. 测试搜索
python kb_tool.py search "ClickHouse为什么快"
# 期望：返回 MongoDB vs MySQL vs ClickHouse 笔记

# 4. 通过微信测试
# 向 QClaw 发消息："列存储和行存储有什么区别？"
# 期望：返回 Row Storage vs Column Storage 笔记的内容
```

### 时间分配

| 任务 | 预计时间 |
|------|----------|
| 安装包 + 编写 indexer.py | 2-3h |
| 测试 ChromaDB 索引和搜索质量 | 1-2h |
| 编写 server.py（FastAPI） | 2h |
| 编写 kb_tool.py（CLI） | 1h |
| 创建 kb-qa skill + QClaw 项目 | 1-2h |
| 端到端测试 | 1h |

---

## Phase 2：智能笔记生成（第 3-6 周，约 20-25 小时）

### 交付物

#### 1. `10-System/scripts/generator.py` -- Zettel 笔记生成器

核心流程：
```
用户说"我刚学了 Kelly Criterion"
    │
    ▼
1. /check -- 搜索已有笔记（ChromaDB, 阈值 0.85）
    │ 已存在 → 提示用户复习/更新
    │ 不存在 ↓
2. 分类 domain -- LLM 分类到 math/quant/python/sql/methods
3. 查找关联笔记 -- ChromaDB 搜索 top 5 相关笔记
4. 调用 Claude API -- 按 T-Zettel 模板生成完整笔记
5. 校验 -- frontmatter 完整性、至少 2 个 Connections
6. 保存 -- 写入 03-Zettel/
7. 索引 -- 更新 ChromaDB
8. 更新 MOC -- 在相关 MOC 中插入链接
9. 提交 -- git add + commit + push
```

Claude API 调用模板（python 伪代码）：
```python
prompt = f"""创建一条 Zettelkasten 笔记，主题："{topic}"
领域：{domain}
相关已有笔记：{format_related(related_notes)}

严格按以下格式生成（参考 09-Templates/T-Zettel.md）：
---
id: "{timestamp}"
title: "{title}"
created: "{iso_datetime}"
updated: "{iso_datetime}"
tags:
  - type/zettel
  - domain/{domain}
  - mastery/1-introduced
aliases: []
---
# {title}

## Core Definition
（一段话说明概念）

## My Understanding
（用自己的话解释）

## Why It Matters
（对量化研究为什么重要）

## Technical Details
（公式、代码、精确定义）

## Application Example
（具体应用场景）

## Common Misconceptions
（常见误解）

## Connections
（链接到已有笔记，至少 2 个）

## References
-

规则：
- Core Definition 和 Technical Details 用中文
- My Understanding 要像真人说话
- Connections 必须链接到真实存在的笔记
"""
```

#### 2. FastAPI 新增端点

```
POST /create
  Body: {"topic": "Kelly Criterion", "context": "仓位管理公式", "domain": "quant/risk"}
  Response: {"status": "created", "file": "03-Zettel/Kelly Criterion.md", "connections": [...]}
```

#### 3. QClaw Skill：`kb-add`（创建笔记）

创建 `C:\Users\yzb\.qclaw\skills\kb-add\SKILL.md`

触发条件："我学了 X"、"添加关于 X 的笔记"、"创建 X 的笔记"
动作：
1. 调用 `python kb_tool.py check "X"`
2. 如果不存在：调用 `python kb_tool.py create "X" --context "用户提供的上下文"`
3. 确认创建成功，展示笔记摘要和连接

#### 4. QClaw Skill：`kb-quiz`（自我测验）

创建 `C:\Users\yzb\.qclaw\skills\kb-quiz\SKILL.md`

触发条件："考考我"、"quiz me"、"测试一下"
动作：
1. 随机选择 1-3 条笔记
2. 基于笔记内容生成问题
3. 等待用户回答
4. 评估答案，给出反馈

### 本阶段验证

```
1. 通过微信告诉 QClaw："我刚学了 Kelly Criterion，是关于仓位管理的"
   期望：QClaw 创建格式正确的笔记，自动添加到 MOC-Quantitative-Strategy

2. 再问 QClaw："什么是 Kelly Criterion？"
   期望：基于刚创建的笔记回答

3. 说"考考我"
   期望：QClaw 从已有笔记中出题

4. 说"我学了 Row Storage"（重复主题）
   期望：QClaw 检测到已有笔记，建议复习而非重复创建
```

### 时间分配（4 周内）

| 任务 | 预计时间 |
|------|----------|
| generator.py + Claude API 集成 | 5-6h |
| 校验逻辑 + 文件保存 + MOC 自动更新 | 4-5h |
| /create 端点 + kb-add skill | 3-4h |
| kb-quiz skill | 3-4h |
| RAG 问答增强（多笔记综合回答） | 3-4h |
| 测试 + 质量调优 + 创建 5-10 条测试笔记 | 3-4h |

---

## Phase 3：自动化学习系统（第 7-12 周，约 25-30 小时）

### 交付物

#### 1. `10-System/scripts/spaced_repetition.py` -- SM-2 间隔复习

- 为每条笔记维护复习计划
- 存储：`10-System/config/review_schedule.json`
- 字段：`note_id, ease_factor, interval, repetitions, next_review, last_quality`

#### 2. `10-System/scripts/knowledge_graph.py` -- NetworkX 知识图谱分析

- 从 wikilinks 构建有向图
- 检测孤立笔记（无入站链接）
- 识别桥接笔记（连接 2+ 领域）
- 计算图谱密度和领域内连通性

#### 3. FastAPI 新增端点

```
GET /review   -- 返回到期复习项目
GET /stats    -- 返回图谱统计（总笔记数、链接数、孤立笔记、桥接笔记）
```

#### 4. QClaw Skill：`kb-review`（每日复习）

触发条件："复习"、"review"，或由 QClaw cron 定时触发
动作：
1. 调用 `/review` 获取到期项目
2. 逐条展示笔记摘要
3. 提问测试
4. 根据回答质量更新 SM-2 参数

#### 5. QClaw Cron 定时任务

编辑 `C:\Users\yzb\.qclaw\cron\jobs.json`：

```json
{
  "kb-daily-push": {
    "schedule": "30 8 * * *",
    "message": "执行每日知识推送：调用 kb-review skill，选择 2-3 条到期复习笔记，通过微信发送给用户"
  },
  "kb-weekly-report": {
    "schedule": "0 10 * * 0",
    "message": "生成每周知识库报告：调用 /stats 端点，报告本周新增笔记、孤立笔记、建议连接"
  }
}
```

#### 6. Obsidian iOS 设置

- iPhone 安装 Obsidian App
- 方案 A（免费）：Working Copy App + Git clone → 在 Obsidian 中打开
- 方案 B（付费，体验更好）：Obsidian Sync（$4/月）
- 移动端只读，所有创建通过微信 → QClaw

#### 7. Windows 服务化

用 `nssm` 或 Windows 计划任务设置 FastAPI 服务器开机自启：
```bash
nssm install KnowledgeBaseAPI "python" "D:\...\server.py"
nssm set KnowledgeBaseAPI AppParameters "D:\...\server.py"
nssm set KnowledgeBaseAPI AppDirectory "D:\...\10-System\scripts"
nssm start KnowledgeBaseAPI
```

### 本阶段验证

```
1. 每日 cron 触发，微信收到复习推送
2. SM-2 算法根据测验结果调整复习间隔
3. knowledge_graph.py 输出有意义的图谱报告
4. iPhone Obsidian App 通过 git pull 显示最新笔记
5. Windows 重启后 FastAPI 自动启动
6. 通过微信完成完整的 创建→学习→测验→复习 循环
```

### 时间分配（6 周内）

| 任务 | 预计时间 |
|------|----------|
| spaced_repetition.py + SM-2 | 4-5h |
| knowledge_graph.py + 图谱分析 | 4-5h |
| kb-review skill + 复习端点 | 3-4h |
| QClaw cron 设置 + 每日推送测试 | 3-4h |
| Obsidian iOS + Git 同步 | 3-4h |
| Windows 服务化 + 端到端可靠性测试 | 3-4h |
| 持续创建笔记（每周 2-3 条） | 3-4h |

---

## 最终文件结构

### 知识库新增文件

```
10-System/
├── scripts/
│   ├── requirements.txt              (已有，需更新)
│   ├── indexer.py                    (Phase 1 新增)
│   ├── server.py                     (Phase 1 新增)
│   ├── kb_tool.py                    (Phase 1 新增)
│   ├── generator.py                  (Phase 2 新增)
│   ├── spaced_repetition.py          (Phase 3 新增)
│   ├── knowledge_graph.py            (Phase 3 新增)
│   └── chroma_data/                  (Phase 1 自动生成，.gitignore 已忽略)
└── config/
    └── review_schedule.json          (Phase 3 新增)
```

### QClaw 新增文件

```
C:\Users\yzb\.qclaw\
├── skills/
│   ├── kb-qa\SKILL.md               (Phase 1)
│   ├── kb-add\SKILL.md              (Phase 2)
│   ├── kb-quiz\SKILL.md             (Phase 2)
│   └── kb-review\SKILL.md           (Phase 3)
├── workspace\projects\
│   └── personal-knowledge-base\     (Phase 1)
│       ├── README.md
│       ├── AUTONOMOUS_CONFIG.json
│       └── agent_templates/
└── cron\jobs.json                    (Phase 3 修改)
```

---

## 关键技术决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 移动端 AI 界面 | 微信 → QClaw | 已运行，零额外配置，远程自动可用 |
| 移动端阅读 | Obsidian iOS | 原生 vault 支持、图谱视图 |
| 向量存储 | ChromaDB | 嵌入式、纯 Python、免费 |
| 嵌入模型 | paraphrase-multilingual-MiniLM-L12-v2 | 中英文支持、本地免费、120MB |
| 笔记生成 LLM | Claude API | 高质量结构化输出 |
| 快速问答 LLM | QClaw 内置模型 | 零额外成本 |
| 同步方案 | Git → GitHub/Gitee | 版本控制、免费、跨平台 |
| 后端框架 | FastAPI + uvicorn | 已安装、异步、自动文档 |
| QClaw↔FastAPI 桥接 | CLI 工具 (kb_tool.py) | 简单、可调试、QClaw exec 可调用 |
| 间隔重复 | SM-2 算法 | 经典、易实现 |
| 知识图谱 | NetworkX | 已安装、轻量 |
| 服务持久化 | nssm Windows 服务 | 开机自启、自动重启 |
| 笔记文件名 | 描述性标题（无时间戳前缀） | 图谱视图干净、链接可读 |

---

## 风险与应对

| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| ChromaDB 索引损坏 | 低 | 中 | `/index/rebuild` 从 Markdown 重建 |
| 微信连接断开 | 中 | 高 | 飞书已配置为备用通道 |
| Claude API 费用增长 | 中 | 低 | 简单问答用 QClaw 内置模型，Claude 仅用于笔记生成 |
| Windows 重启中断服务 | 中 | 中 | nssm/计划任务自动启动 |
| 笔记生成质量低 | 中 | 中 | 校验步骤 + 人工审核收件箱 |
| 用户未坚持每日复习 | 高 | 低 | cron 推送提供被动提醒，不强制 |

---

## 知识库当前状态（2026-04-27）

### 已有笔记（8 条）
| 笔记 | 领域 | 掌握度 |
|------|------|--------|
| Row Storage vs Column Storage | SQL | 1-introduced |
| OLTP vs OLAP | SQL | 1-introduced |
| Database Partitioning | SQL | 1-introduced |
| Time-Series Database | SQL | 1-introduced |
| MongoDB vs MySQL vs ClickHouse | SQL | 1-introduced |
| L2 Market Data Storage Strategy | Quant | 1-introduced |
| Parquet File Format | Python | 1-introduced |
| Processing Parquet with Python | Python | 1-introduced |

### 知识缺口
| 领域 | 已有笔记 | MOC 占位符 | 空缺率 |
|------|----------|-----------|--------|
| SQL | 6 | 6 | 50% |
| Python | 2 | 9 | 82% |
| Quantitative Strategy | 2 | 15 | 88% |
| Mathematics | 0 | 34 | 100% |
| Learning Methods | 0 | 9 | 100% |
| **合计** | **8 (实)** | **64 (虚)** | **82%** |

### 优先学习方向
1. **数学基础**：概率 → 统计 → 线性代数（量化研究的根基）
2. **Python 核心库**：NumPy → Pandas（数据处理的日常工具）
3. **量化入门**：因子模型 → 回测（从 MOC 框架填充内容）

---

## 验证总表

### Phase 0 验证
- [ ] 8 条笔记重命名（去掉时间戳前缀）
- [ ] 所有 MOC 链接更新
- [ ] CLAUDE.md 命名规则更新
- [ ] Git 提交并推送到 GitHub

### Phase 1 验证
- [ ] `python indexer.py build` 成功索引 8 条笔记
- [ ] `curl -X POST localhost:28790/search` 返回相关结果
- [ ] 通过微信向 QClaw 提问获得基于笔记的回答
- [ ] Git push 到远程仓库正常

### Phase 2 验证
- [ ] 通过微信创建新笔记，格式正确（frontmatter、Connections、MOC 更新）
- [ ] 重复主题被检测到，提示复习
- [ ] kb-quiz 从笔记出题并评估答案

### Phase 3 验证
- [ ] 每日 cron 推送复习项目到微信
- [ ] SM-2 根据测验结果调整间隔
- [ ] knowledge_graph.py 输出有意义的图谱报告
- [ ] iPhone Obsidian 通过 git pull 显示最新笔记
- [ ] Windows 重启后 FastAPI 自动启动
