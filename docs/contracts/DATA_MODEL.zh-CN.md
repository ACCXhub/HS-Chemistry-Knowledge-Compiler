# 规范数据模型

[English](DATA_MODEL.md)

> 中文版对应英文文档；历史章节保留其当时范围与版本。后续契约变更须同步维护两种语言。

状态：**截至 M25 的可执行源数据契约**

本文定义规范源记录语义。M4 收敛可执行的 Rule/事实/物种组成/TeachingView/ReactionForm/产物子集，不缩减更广泛的模型。

## 1. 顶层具有身份的记录

规范记录包括 Entity（`element | species | substance | material_system`）、Structure、Reaction、TeachingView、Rule、Source、Evidence；需要持久断言身份时，还包括独立整理且有证据的 FacetAssertion、PropertyFact、Relation，以及可选的可复用 Experiment。

只有独立生命周期或持久引用确有需要时，记录才获得持久 ID。

## 2. Entity

概念形状：

```yaml
id: ent_...
record_type: entity
entity_kind: species
semantic_keys: []
terms:
  preferred: ...
  aliases: []
payload:
  species_kind: ion
  composition: {}
  formal_charge: -1
  structure_ids: []
relation_assertions:
  - relation_key: metal.product_cation
    target_id: ent_species_...
    context: {medium: aqueous}
    evidence_ids: [ev_...]
```

`species_kind` 可为 atom/ion/molecule 等。Substance 表示宏观纯物质身份，MaterialSystem 表示溶液/混合物/体系组成。化学式字符串和语义键是查找/表示坐标，不拥有持久身份。

## 3. 嵌入组成

Composition 默认是所属对象上的精确嵌入值，不是顶层身份记录。

```yaml
composition:
  components:
    - element_id: ent_element_h
      count: 2
    - element_id: ent_element_o
      count: 1
  net_charge: 0
```

精确组成/电荷为确定性配平提供守恒数据。源校验拒绝重复元素组分、形式电荷与净电荷不一致、重复 Facet 键，以及规范 Reaction、ReactionForm、物种组成配置的原子/电荷不守恒。非化学计量混合物/材料体系应使用适当定量组分，不能伪造整数化学式计数。

## 4. Structure

Structure 是独立于任何表示的稳定领域对象。

```yaml
id: str_...
record_type: structure
structure_kind: molecular_connectivity
subject_ids: [ent_...]
components: []
bonds:
  - key: b1
    from: a1
    to: a2
    order: 1
motifs: []
representations:
  - kind: smiles
    value: CCO
```

表示不能替代结构身份。键默认嵌入结构，除非后续独立生命周期确需顶层身份。

## 5. 断言与事实语义

源断言区分语义来源：

```text
intrinsic | contextual | derived
```

知识状态区分：

```text
known(value, including boolean false)
explicit unknown
not_applicable
absent/open-world
```

即已知值（包括 false）、显式未知、不适用、缺失/开放世界。absent 是编译器在没有匹配断言时观察到的状态，不能序列化成虚构源断言。

可执行上下文属性示例：

```yaml
property_key: electrolyte.strength
fact_kind: contextual
value_state: known
value: strong
context: {medium: aqueous}
evidence_ids: [ev_...]
```

酸、碱、盐、氯化物、硫酸盐、碳酸氢盐等稳定分类仍是 Facet。规则不能静默地把缺失、显式未知或不适用转成已知 false。独立身份事实/断言在生命周期需要时，可另有持久溯源/修订元数据。

M10 最小可执行 Relation 嵌入源 Entity：

```yaml
relation_assertions:
  - relation_key: metal.product_cation
    target_id: ent_species_zn_2plus
    truth: true  # optional; defaults to true
    context: {medium: aqueous}
    evidence_ids: [ev_...]
```

关系键受控，在引用解析后语义校验定义域/值域。metal.product_cation、metal.displaces_cation 的源必须是 classification.metal 已知为真的单质 Substance，目标为正电离子 Species。ion.elemental_substance 的源是正电离子 Species，目标是已知为金属的单质 Substance。普通嵌入断言没有持久关系 UUID；确定性查找/来源保留源 ID、关系键、目标 ID、解析真值、规范上下文和证据 ID。

各关系家族声明正向目标基数。metal.product_cation 和 ion.elemental_substance 每源/上下文允许一个正目标；metal.displaces_cation 允许多个不同正目标。truth: false 记录已知否定，不占正向基数。拒绝完全重复和同一元组正负矛盾。解析选取最具体的匹配断言；相同具体程度且真值一致时合并证据，真值混合则显式语义错误。产物目标解析只暴露正断言。缺失仍是开放世界状态，不是 false。

## 6. 嵌入 Context

Context 是结构化限定集合，默认不是顶层记录：

```yaml
context:
  phase: aqueous
  solvent_id: ent_water
  temperature: {number: 298.15, unit: K}
  pressure: {number: 100, unit: kPa}
  concentration_regime: dilute
```

上下文维度键和枚举使用受控词汇。M4 可执行请求案例刻意只使用少量标量子集，不因此缩减规范模型。

## 7. Reaction

规范 Reaction 拥有一次经过整理的化学转化：

```yaml
id: rxn_...
record_type: reaction
participants:
  - target_id: ent_...
    target_kind: substance
    role: reactant
    coefficient: {numerator: 1, denominator: 1}
    phase: aqueous
conditions: []
forms: []
facet_assertions: []
evidence_ids: [ev_...]
```

参与者和条件为嵌入值。Reaction 身份不依赖方程文本、参与者顺序、系数倍乘或教学位置。

M7 可执行条件子集是顺序无关、带证据的受控值列表：

```yaml
conditions:
  - key: medium
    value: aqueous
    evidence_ids: [ev_...]
  - key: temperature_regime
    value: warmed
    evidence_ids: [ev_...]
```

同一 Reaction 内条件键唯一。它们是规范比较的要求，不要求请求上下文与条件对象完全相同；允许额外请求维度。

当前 temperature_regime 为 ambient | warmed | heated。heated 是独立受控值，不是 warmed 的别名，也不隐含温度排序推理。M16 复用通用标量上下文/条件比较，不隐含温度专用运行语义。

## 8. ReactionForm

底层转化相同时，ReactionForm 是所属 Reaction 的表示/投影。

```yaml
forms:
  - form_key: net_ionic
    form_kind: net_ionic
    participants: []
    projection:
      method: aqueous_strong_electrolyte_v1
      required_assumptions:
        - aqueous_medium
        - strong_electrolyte_dissociation
      notes: []
```

只有在声明的假设下，形式才可从宏观物质转到离子物种指称层次。M4 只从唯一上下文匹配的规范物种组成推导水溶液形式；缺失假设/配置显式报告，不猜测解离。

同一转化可并存分子、完全离子、净离子和热化学形式。半反应因化学转化不同，仍是独立 Reaction。

## 9. ReactionCandidate

生成候选：

```yaml
record_type: reaction_candidate
candidate_key: cand_sha256_...
proposed_participants: []
proposed_conditions: []
provenance:
  rule_id: rule_...
  rule_version: 1.0.0
  input_ids: []
  validation_results: []
  canonical_match: {}
  proof_trace: []
  relation_assertions: []
```

纯编译不创建基于时间的审核 UUID。精确规范匹配不把候选提升或修改为规范知识。单独持久化的人工审核对象可有 rcand_* ID，但保留不可变确定性 candidate_key。

## 10. Rule

Rule 拥有 rule_* 身份、语义版本、决策域、证据、匹配约束、谓词/阻断条件、产物构造、校验器和显式消解关系。不另设规范 RuleReference。

M4 参与者模式可组合身份专用 target_id、entity_kind、species_kind、参与者 phase、必需和禁止 Facet。

有类型谓词注册表支持在声明主体上使用 equals、not_equals、is_known、in_set。Relation 谓词接受 equals expected: true，一个有效源绑定、受控关系键，以及恰好一个精确 target_id 或有类型 target_source。目标源可从绑定参与者的规范物种组成中解析指定电荷符号的唯一离子。这是有界执行词汇，不是任意表达式或图查询语言。

规则关系为：

```text
overrides
specializes
fallback_for
equivalent_to
mutually_exclusive_with
```

未知引用、无效优先环、矛盾声明和未消解的非等价潜在重叠均在编译时失败。规则/文件顺序不表示语义优先级。

### 产物构造

可用精确规范 ID：

```yaml
- target_id: ent_substance_h2o
  phase: liquid
```

也可用有界语义键/离子对/交换产物解析器：

```yaml
- construct:
    kind: semantic_key
    scheme: formula.unit
    value: AgCl
  phase: solid
```

必须恰好返回一个已有规范 Entity。零匹配/多匹配显式失败。编译器不虚构身份，不猜可变价或其他化学歧义身份。

M10 为 ionic_pair 增加有类型离子源：

```yaml
- phase: aqueous
  construct:
    kind: ionic_pair
    cation_source:
      {kind: relation_target, binding: metal, relation_key: metal.product_cation}
    anion_source:
      {kind: speciation, binding: acid}
```

两种规范离子 Species 解析后，既有中性离子对解析器仍唯一负责精确电荷/组成匹配。历史 cation_from/anion_from 仍有效，编译为等价 speciation 离子源。

M11 增加精确规范离子源：

```yaml
anion_source:
  kind: exact_entity
  target_id: ent_species_oh_minus
```

目标必须为规范离子 Species，电荷符号符合阳/阴离子位置。此来源无反应物绑定，不为水或其他 Entity 创建解离断言。

M19 增加共享 EntitySourcePlan 的四种封闭形式：精确实体、参与者绑定、来自绑定参与者上下文匹配配置的唯一指定电荷符号离子，以及源属于上述非 Relation 形式的一次关系目标。Relation 套 Relation 无效。entity_source 产物解析到一个已有规范 Entity，携带所用配置/断言证据，不解析化学式、不创建身份。

## 11. TeachingView

```yaml
id: view_...
record_type: teaching_view
view_key: hs-cn-framework-11
nodes:
  - path_key: D08/substances/inorganic/acids
    parent_path_key: D08/substances/inorganic
    members: []
```

教学路径/节点嵌入且仅在视图内有效。路径变化不改变化学身份。视图投影规范知识，不拥有或重定义化学身份。

## 12. Source 与 Evidence

Source 标识出版物/数据库/标准/手册。Evidence 定位并解释来源中的断言，可支持、限定或反驳整理的断言、关系、反应、教学主张或规则。生成结果依赖证据时，证据/来源必须可沿编译输出追溯。

## 13. 外部生成产物

外部产物由契约负责且可重现。四项兼容坐标独立：

| 坐标 | 当前值 |
| --- | --- |
| 源 schema | `3.7.0` |
| Rule DSL | `1.4.0` |
| 内部 RulePlan | `1.4.0` |
| 外部产物格式 | `1.5.0` |

manifest 携带四项坐标，外部 payload 携带 artifact_format_version。消费者必须拒绝不支持的格式，不能仅由编译器包版本猜测兼容性。

产物 1.5.0 必需，因为输出计划的 PredicatePlan.target_source、ProductPlan.entity_source 包含嵌套 EntitySourcePlan。参考读取器仍接受 1.0.0–1.4.0。

编译器内部计划、索引、缓存和紧凑运行 ID 仍是实现细节，不是规范源契约。
