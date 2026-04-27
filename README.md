# 个人成长型量化知识库

基于 Zettelkasten 笔记法 + LLM + Obsidian 构建的个人成长型量化策略研究知识库。

## 项目结构

| 目录 | 用途 | 笔记类型标签 |
|------|------|-------------|
| `00-Inbox/` | 临时收集箱 | `#type/fleeting` |
| `01-Atlas/` | 知识地图/MOC | `#type/structure` |
| `02-Source/` | 文献笔记 | `#type/source` |
| `03-Zettel/` | 永久笔记 | `#type/zettel` |
| `04-Project/` | 研究项目 | `#type/project` |
| `05-Daily/` | 每日笔记 | `#type/daily` |
| `06-Archive/` | 归档 | `#status/archive` |
| `09-Templates/` | 模板 | - |
| `10-System/` | 脚本/配置 | - |

## 笔记工作流

```
想法 → Fleeting Note (00-Inbox) → Literature Note (02-Source) → Permanent Note (03-Zettel) → Structure Note (01-Atlas)
```

1. **捕获**: 想法快速记入 `00-Inbox/`（48小时内处理）
2. **阅读**: 学习资料时做文献笔记 `02-Source/`
3. **提炼**: 提取原子概念为永久笔记 `03-Zettel/`（用自己的话、至少一个链接）
4. **组织**: 在 MOC 中策展链接 `01-Atlas/`

## 命名规则

- 永久笔记: `YYYYMMDDHHmm - 描述性标题.md`
- 来源笔记: `YYYY-MM-DD - 作者 - 标题.md`
- 每日笔记: `YYYY-MM-DD.md`

## 标签体系

- `#type/` — 笔记类型（每笔记一个）
- `#domain/` — 知识领域（永久笔记一个）
- `#mastery/0-5` — 掌握程度（永久笔记专属）
- `#status/` — 工作流状态（可选）

## 插件

- **Templater**: 动态模板（时间戳、变量填充）
- **Calendar**: 每日笔记日历导航
- **Dataview**: 查询笔记、生成仪表盘

## 同步

Git 为主，Obsidian Sync 可选。每次会话开始 `git pull`，结束 `git add . && git commit && git push`。

## 复习节奏

- **每日**（2-3分钟）: 处理收件箱
- **每周**（20-30分钟）: 审查新笔记、更新掌握等级
- **每月**（45-60分钟）: 审查 MOC、清理孤立笔记、评估进度
