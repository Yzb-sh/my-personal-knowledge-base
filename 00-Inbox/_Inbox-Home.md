---
id: "inbox-home"
title: "Inbox Home"
created: "2026-04-27"
tags:
  - type/structure
---
# Inbox Home

收件箱仪表盘。所有临时笔记的入口。

## Rules
1. 所有快速捕获的想法放入 `00-Inbox/`
2. 48小时内必须处理每条临时笔记
3. 处理选项：
   - **转为永久笔记**: 提取概念到 `03-Zettel/`，使用 T-Zettel 模板
   - **转为来源笔记**: 如果来自书籍/论文/课程，放到 `02-Source/`
   - **合并到现有笔记**: 如果是对已有概念的补充
   - **删除**: 如果不再需要

## Unprocessed Notes
<!-- 用 Dataview 查询收件箱中的笔记 -->
```dataview
LIST
FROM "00-Inbox"
WHERE file.name != "_Inbox-Home"
SORT created DESC
```
