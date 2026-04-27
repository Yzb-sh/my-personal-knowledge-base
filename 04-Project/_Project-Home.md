---
id: "project-home"
title: "Project Home"
created: "2026-04-27"
tags:
  - type/structure
---
# Project Home

活跃研究项目仪表盘。

## Active Projects
<!-- 用 Dataview 查询活跃项目 -->
```dataview
TABLE status, created
FROM "04-Project"
WHERE file.name != "_Project-Home" AND status != "completed"
SORT created DESC
```

## Completed Projects
```dataview
TABLE created
FROM "04-Project"
WHERE status = "completed"
SORT created DESC
```
