# Schema 策略

[English](SCHEMA_STRATEGY.md)

> 中文版对应英文文档；历史章节保留其当时范围与版本。后续契约变更须同步维护两种语言。

状态：**当前源数据/产物契约与 M22–M25 离线迁移边界**

## 1. 编写边界

规范化学数据保持为可人工审核的 YAML。结构校验使用 JSON Schema Draft 2020-12，随后执行编译器负责的语义校验。运行布局、索引和 RulePlan 是生成的实现细节，不是源数据编写契约。

M4 保持文件布局不承载身份的原则：稳定 ID 和语义内容决定含义，源遍历顺序不决定含义。

## 2. 当前源 schema

```text
schemas/knowledge-record.schema.json
source schema version: 3.7.0
```

覆盖 M4 可执行子集中的 Entity、嵌入式有类型 Entity Relation 断言、Reaction/ReactionForm、TeachingView、Rule、Source、Evidence。Relation 定义域/值域及家族基数由编译器语义校验。

`schemas/f2-record.schema.json` 是历史 F2 材料，不是 M4 加载器的当前契约。`schemas/f2-case.schema.json` 仍是确定性审计/示例请求 schema，因为 M4 未扩展请求范围。

## 3. 校验顺序

1. 安全解析 YAML，拒绝重复键；
2. JSON Schema 校验；
3. 稳定 ID 唯一性与引用校验；
4. 实体/参与者/关系定义域和值域、组成/Facet 键唯一性、电荷一致性，以及源 Reaction/ReactionForm/物种组成守恒；
5. 有类型谓词/算子和离子源校验；
6. 将 Rule 编译为编译器内部 RulePlan/IonSourcePlan/EntitySourcePlan；
7. 规则关系图校验；
8. 保守的重叠/冲突分析；
9. 推断时产物解析；
10. 精确配平和原子/电荷校验；
11. 按参与者签名查找规范 Reaction；
12. 必需条件兼容性筛选。

格式错误或语义歧义源数据应被拒绝，不用隐藏默认值修复。

## 4. 事实与 Facet 状态

Facet 断言的 `fact_kind` 可为：

```text
intrinsic | contextual | derived
```

知识状态区分：

```text
known
unknown
not_applicable
absent
```

`absent` 是编译器观察到没有匹配断言，不应序列化成虚构源断言。已知布尔 false 与所有非已知状态不同。

## 5. Rule 源契约

参与者模式可通过精确规范 `target_id`、`entity_kind`、`species_kind`、参与者 `phase`、必需 Facet、禁止 Facet 约束绑定；只有确需身份专用行为时使用精确 ID。

谓词使用带版本的 DSL 算子名，不使用 Python 函数名。注册表仅含 `equals`、`not_equals`、`is_known`、`in_set`。Relation 适用性采用 `equals expected: true`，需一个源绑定、一个受控关系键，以及恰好一个精确 `target_id` 或有类型 `target_source`；缺失或动态解析失败为 UNKNOWN。

规则关系是显式源语义：`overrides`、`specializes`、`fallback_for`、`equivalent_to`、`mutually_exclusive_with`。

产物模板可用精确规范 ID 或有界的语义键、离子对、交换产物、实体源解析器。EntitySourcePlan 允许精确实体、绑定、唯一指定电荷符号的解离离子，或非 Relation 源的一次关系目标；拒绝递归关系跳转。离子对的两种离子可来自规范物种组成、受控单跳关系或精确规范离子 Species。构造使用规范身份/物种组成/关系，绝不创建新规范 Entity。历史 `cation_from`/`anion_from` 仍接受并编译为解离离子源。

## 6. ReactionForm 投影契约

ReactionForm 从属于规范 Reaction，投影声明：

```yaml
projection:
  method: aqueous_strong_electrolyte_v1
  required_assumptions: []
  notes: []
```

只有所需假设及上下文匹配的规范物种组成可用时，消费者/编译器才可提供该形式。投影不创建第二个 Reaction 身份。

## 7. 版本轴

M4 分离四项兼容坐标：

| 坐标 | 当前值 | 责任 |
| --- | --- | --- |
| 源 schema | `3.7.0` | 源数据契约 |
| Rule DSL | `1.4.0` | 规则源契约 |
| 编译器 RulePlan | `1.4.0` | 编译器内部契约 |
| 外部产物格式 | `1.5.0` | 外部生成契约 |

各轴独立。源 schema 修改不自动要求外部格式变更，内部 RulePlan 修订也不天然等于 DSL 修订。

M16 仅升级源 schema，因为 `temperature_regime` 新增区别于 `warmed` 的 `heated`。既有通用标量上下文/条件路径已支持其校验、编译、比较与保留，其他版本不变。

M19 升级四轴：源 schema 接受动态关系目标、源派生产物及 `ion.elemental_substance`；DSL/RulePlan 增加有类型实体源语义；输出编译计划携带嵌套字段。

M20 仅升级源 schema：Relation 断言可选布尔 `truth`，为兼容历史数据默认正向。谓词、编译计划和产物容器不变，其他三轴固定。

M4 不承诺超出显式坐标的长期后向兼容。

`1.5.0` 读取器接受历史格式 `1.0.0`–`1.4.0`。既有 Reaction 可省略 `conditions`，Entity 可省略 `relation_assertions`，参与者模式可省略 `phase`，旧离子对 Rule 可保留 `cation_from`/`anion_from`。此次产物升级因 `compiled-rule-plans.json` 输出了 `1.4.0` 消费者无法安全理解的嵌套实体源。

## 8. 生成产物

M4 在调用者指定目录生成确定性 JSON。manifest 携带四项版本；外部 payload 携带 `artifact_format_version`，编译计划另带 `rule_plan_version`。

消费者必须拒绝不支持的产物版本；参考编译器提供此兼容检查。生成产物始终可重现，不能成为可编辑化学事实。

M22 迁移报告是编译器运行时与产物契约之外的确定性溯源输出，用于对照有界外部旧输入与规范源数据。验证、编译、审计和推断均不加载报告或旧包，因此四项兼容坐标不变。

## 9. 确定性序列化

继续使用 F2 规范 JSON 规则：UTF-8；字符串和映射键做 NFC 规范化；映射键按字典序排序；紧凑分隔符；语义数值域只用整数；语义身份中不含时间戳、本地路径、进程 ID 或遍历顺序元数据。

相同规范化过程继续保护语义摘要和确定性候选键。
