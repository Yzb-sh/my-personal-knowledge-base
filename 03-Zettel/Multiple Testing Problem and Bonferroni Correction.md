---
id: "202605061810"
title: "Multiple Testing Problem and Bonferroni Correction"
created: "2026-05-06T18:10:00"
updated: "2026-05-06T18:10:00"
tags:
  - type/zettel
  - domain/math
  - mastery/2-familiar
aliases: []
---
# Multiple Testing Problem and Bonferroni Correction

## Core Definition
当同时进行多个假设检验时，整体假阳性率会随检验次数增加而膨胀。Bonferroni 校正通过收紧每个检验的显著性阈值来控制整体错误率。

## My Understanding
如果按照 5% 假阳性的概率，50 个因子里面大概有 2.5 个假阳，而现在算出来 50 个里有 3 个有效，正好是假阳因子的期望个数，所以这个结果是不靠谱的。测试 50 个因子时，至少出现一个假阳性的概率是 1 - 0.95^50 ≈ 92.3%。多重比较问题跟怎么组织分析无关，跟给了自己多少次"碰巧成功"的机会有关——50 次单独分析和一次性做 50 个检验，数学上完全等价。Confirmatory test（有明确假设，只验证一个因子）不需要校正，exploratory search（从多个候选中筛选）必须校正。

## Why It Matters
因子研究几乎都是探索性的——研究者会测试大量候选因子，筛选出显著的报告。如果不做多重比较校正，发表的研究成果中假阳性比例会非常高。这是量化研究中"因子动物园"问题的统计根源。

## Technical Details

**假阳性膨胀**
- 单次检验：P(假阳性) = α
- m 次检验：P(至少一个假阳性) = 1 - (1-α)^m
- 例：α = 0.05，m = 50 → P = 1 - 0.95^50 ≈ 92.3%
- 期望假阳性个数 = m × α = 50 × 0.05 = 2.5

**Bonferroni 校正**
- α_new = α_total / m
- 例：α_total = 0.05，m = 50 → α_new = 0.001
- 每个因子的 p-value 需 < 0.001 才算通过校正

**Confirmatory vs Exploratory**
- Confirmatory：有先验理论预期，检验特定假设 → 单次检验，α = 0.05
- Exploratory：搜索多个候选，挑选显著结果 → 必须多重比较校正
- 关键区别在于研究流程是否包含"从多个候选中筛选"的过程

**其他校正方法**
- FDR（False Discovery Rate）：控制假阳性比例而非绝对数量，因子研究中更常用
- 比 Bonferroni 更宽松，但原理类似

## Application Example
测了 50 个因子，3 个 p < 0.05。期望假阳性 = 50 × 0.05 = 2.5，3 个显著完全可以用运气解释。Bonferroni 校正后阈值 = 0.001，如果 3 个因子的 p 都在 0.01-0.05 之间，则全部不能算显著。

## Common Misconceptions
- 认为分次单独测试就不需要校正：50 次单独分析的假阳性率与一次性做 50 个检验完全相同
- 只报告显著结果隐瞒测试次数：与研究流程无关，只要测试了多个候选就存在多重比较问题

## Connections
- [[MOC-Mathematics]] -- 属于统计学部分（假设检验的扩展）
- [[Hypothesis Testing Fundamentals]] -- 多重比较建立在单次假设检验之上
- [[Pearson vs Spearman Correlation]] -- 因子 IC 的假设检验是多重比较的典型应用场景
- [[Cross-Sectional vs Time-Series Data]] -- 截面因子筛选时的多重比较问题
