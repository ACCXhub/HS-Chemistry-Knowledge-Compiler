# 声明式反应规则 DSL

[English](RULE_DSL.md)

> 中文版对应英文文档；历史章节保留其当时范围与版本。后续契约变更须同步维护两种语言。

状态：**M19 有界动态 Relation 目标与实体源产物**

## 1. 责任与版本

每条源 Rule 拥有稳定 rule_* ID、语义版本、证据和显式消解关系。DSL 版本独立于源 schema、编译计划和外部产物版本。

M19 将 DSL 升至 1.4.0，支持有类型动态关系目标和源派生产物。RulePlan 独立升至 1.4.0，加入 EntitySourcePlan、PredicatePlan.target_source、ProductPlan.entity_source。Reaction 条件和关系家族基数仍属于源数据契约，不是 DSL 字段。

## 2. 参与者模式

反应物模式绑定一个规范参与者，可约束：

```yaml
- bind: chloride_salt
  entity_kind: substance
  species_kind: ion        # only when relevant
  target_id: ent_...       # optional exact identity
  phase: liquid            # optional input participant phase
  required_facets: []
  forbidden_facets: []
```

target_id、phase 可选；身份/类型/物态约束建立可能绑定，Facet 按开放世界三值语义计算，缺失不转为 false。

## 3. 有类型谓词

当前只公开以下源算子：

| 算子 | 主体 | 输入类型 | 期望参数 | UNKNOWN 行为 |
| --- | --- | --- | --- | --- |
| `equals` | context, facet, property, ionic_exchange, relation | 字符串/布尔/整数 | 单一标量 | 非已知事实 → UNKNOWN |
| `not_equals` | context, facet, property, ionic_exchange | 字符串/布尔/整数 | 单一标量 | 非已知事实 → UNKNOWN |
| `is_known` | context, facet, property, ionic_exchange | 任意事实状态 | 无 | 仅 known 返回 TRUE，其余 FALSE |
| `in_set` | context, facet, property | 字符串/布尔/整数 | 同类型非空标量列表 | 非已知事实 → UNKNOWN |

示例：

```yaml
predicates:
  - operator: equals
    subject: context
    key: medium
    expected: aqueous
```

旧 F2 context: {key: value} 编写方式编译为相同有类型 equals/context 语义。M6 刻意不引入任意表达式或析取语言。

Relation 比一般 equals 更严格。精确目标仍有效，M19 还允许一个有类型目标源：

```yaml
- operator: equals
  subject: relation
  binding: metal
  key: metal.displaces_cation
  target_source:
    kind: speciation_ion
    binding: salt
    charge_sign: positive
  expected: true
```

要求恰好一个有效源绑定、受控关系键、target_id 或 target_source 二选一，以及字面值 expected: true。有证据的匹配断言为 TRUE；无断言或动态目标不可用/歧义为 UNKNOWN。拒绝其他算子、反向查找、递归 Relation 源和任意图表达式。

## 4. 知识状态

适用性保留：

```text
known(value, including false)
explicit unknown
not_applicable
absent/open-world
```

即已知值（含 false）、显式未知、不适用、缺失/开放世界，并追踪 intrinsic/contextual/derived 来源。除 is_known 等认知状态算子外，非已知状态传播为 UNKNOWN，不是 false。

## 5. 阻断条件

阻断条件使用相同有类型谓词语义。TRUE 阻断该路径，UNKNOWN 使路径不确定。阻断条件不是整数优先级捷径。

## 6. 产物构造器

DSL 支持有界规范构造：

```yaml
products:
  - phase: solid
    target_id: ent_substance_agcl
```

或：

```yaml
products:
  - phase: solid
    construct:
      kind: semantic_key
      scheme: formula.unit
      value: AgCl
```

构造器必须解析到恰好一个已有规范 Entity，不虚构身份，也不负责配平系数。

ionic_pair 从独立有类型来源解析规范阳/阴离子，对精确组成做电荷平衡，再选择已有中性 Substance。M10 语法为：

```yaml
construct:
  kind: ionic_pair
  cation_source:
    kind: relation_target
    binding: metal
    relation_key: metal.product_cation
  anion_source:
    kind: speciation
    binding: acid
```

speciation 从绑定 Entity 的上下文匹配水溶液配置选唯一电荷符号适合的离子。relation_target 执行一次受控、考虑上下文的关系查找，要求唯一目标，不是任意图遍历。旧 cation_from/anion_from 仍有效并编译为两个 speciation 来源。

M11 加入通用精确离子形式：

```yaml
anion_source:
  kind: exact_entity
  target_id: ent_species_oh_minus
```

exact_entity 要求唯一规范离子 Species，电荷符号符合阳/阴离子位置；不携带参与者绑定，也不暗示反应物解离出该离子。

exchange_product 复用有界交换解析，选择唯一沉淀或可溶对产物。零/多个产物、离子或关系匹配均显式失败。

M19 增加 entity_source 构造器：

```yaml
construct:
  kind: entity_source
  source:
    kind: relation_target
    relation_key: ion.elemental_substance
    source:
      kind: speciation_ion
      binding: salt
      charge_sign: positive
```

共享实体源形式为 exact_entity、binding、speciation_ion、relation_target。关系目标必须包裹非 Relation 源，保证最多一跳语义关系。必须选到一个已有规范 Entity，并保留全部使用的物种组成与关系证据。

离子对解析分别返回物种组成来源和关系断言来源，包括实际使用的证据。成功的 Relation 谓词把匹配断言贡献到相同确定性候选来源，在谓词证明事件中保留目标/上下文/证据。失败或未选中的绑定不污染候选来源。该元数据不是新化学事实主体或化学式解析器。

## 7. 规则消解关系

Rule 可声明 overrides、specializes、fallback_for、equivalent_to、mutually_exclusive_with。未知引用、自环、矛盾等价声明和优先环都是编译错误。文件顺序、定义顺序和任意整数优先级不用于语义决胜。

## 8. 静态重叠分析

在 decision_domain 内分析参与者数量/类型/物态、精确身份、必需/禁止 Facet 和简单上下文相等约束。无法证明不相交时，保守输出 potential_overlap。

非等价重叠结果需要显式关系，否则严格编译失败，并给出两条规则 ID 和确定性原因/签名。

## 9. 校验边界

Rule 在精确配平前确定规范产物身份。随后校验器检查守恒/后置条件。规范反应查找属于下游比较，不能成为替代推断的答案来源。
