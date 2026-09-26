# 知识编译器架构

[English](COMPILER.md)

> 中文版对应英文文档；历史章节保留其当时范围与版本。后续契约变更须同步维护两种语言。

状态：**M19 通用有界 entity-source 执行**

## 责任

编译器把经过验证的规范源数据和声明式规则转换为确定性的内部计划、诊断、候选、证明轨迹和外部产物。生成输出可重现，不能成为可编辑的化学事实。

## 编译责任的执行顺序

```text
安全解析 YAML
→ JSON Schema 校验
→ 持久 ID/引用解析
→ 受控关系目标校验
→ 语义索引
→ Rule 解析/类型检查
→ 编译为有类型的 PredicatePlan / ParticipantPatternPlan / IonSourcePlan / EntitySourcePlan / ProductPlan
→ 规则关系图校验
→ 静态重叠分析
→ 确定性运行计划
→ 推断/审计
→ 带版本的产物输出
```

先验证，后推导。

## 算子注册表

编译器实现源级有类型算子注册表。源语义使用稳定算子名和有类型参数，而不是 Python 函数名。注册表保持小规模，编译时拒绝格式错误参数。`equals expected: true` 的 Relation 谓词接受一个绑定，以及恰好一个精确目标或有类型目标源。动态目标缺失/歧义保持 UNKNOWN，不增加图遍历或查询语言。

## 重叠分析

严格编译只比较同一决策域内的 Rule。目前可分析参与者数量、精确 ID、Entity/Species 类型、参与者物态、必需/禁止 Facet 和简单上下文相等约束。不能证明互斥时保守记为 `potential_overlap`。

非等价的潜在重叠若没有显式消解关系，产生 `rule_overlap_compile_error`。

## 消解图

编译器校验关系引用，并按以下规则建立优先关系：

```text
overrides: 声明规则 > 被引用规则
specializes: 声明规则 > 被引用规则
fallback_for: 被引用规则 > 声明的后备规则
```

拒绝优先关系环。运行时使用传递可达性消解，与文件顺序无关。

## 产物解析

`exact_entity`、`semantic_key`、`ionic_pair`、`exchange_product`、`entity_source` 都是有界构造器，根据规范索引及组成/物种组成/关系记录解析。`EntitySourcePlan` 解析精确实体、绑定、唯一指定电荷符号的解离离子，或源自身非 Relation 时的一跳关系目标。离子对来源仍由物种组成、关系或精确离子支持；两离子解析后，既有中性组成/电荷解析器选择规范 Substance。零个或多个匹配都显式报告；不解析显示化学式、不猜化合价、不创建规范身份。

## ReactionForm 投影

投影 API 显式使用整理审核的/基准形式与规范物种组成配置。所需假设决定是否可用；推导的完全/净离子形式保留所属规范 Reaction 身份、精确系数、验证和推导来源。

## 条件执行

规则上下文要求与规范 Reaction 条件使用既有通用标量相等路径。M16 在词汇中加入 `heated`，不增加 heated/CaCO3 专用编译器分支：缺失为 UNKNOWN，已知不等为 FALSE；匹配条件的证据保留在比较结果和来源中。

## 产物/版本边界

版本轴彼此独立：

```text
source schema     3.7.0
Rule DSL          1.4.0
RulePlan          1.4.0
artifact format   1.5.0
```

外部产物包含 `artifact_format_version`；manifest 包含全部四项。产物 `1.5.0` 对应新增嵌套 `PredicatePlan.target_source` 和 `ProductPlan.entity_source`。读取器也接受历史 `1.0.0`–`1.4.0`；消费者应拒绝未知版本。

M20 只改变源 Relation 数据：适用的显式 `truth: false` 产生已知 FALSE 谓词结果，缺失仍为 UNKNOWN。Rule DSL、RulePlan 和产物格式不变。

## 性能原则

Python 实现仍是参考实现。M19 不引入外部依赖、RETE、数据库、原生扩展、通用图引擎、活动性排序引擎或插件运行时。优先使用小型有类型索引和编译计划；优化需要测量证据。
