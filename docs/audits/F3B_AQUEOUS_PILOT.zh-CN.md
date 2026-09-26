# F3B 水溶液化学试点审计

[English](F3B_AQUEOUS_PILOT.md)

> 中文版对应英文文档；历史章节保留其当时范围与版本。后续契约变更须同步维护两种语言。

起始规范 main：`8d92d19b8ebbbcb0f8a9fdaceb7eb895da381447`

分支：`workstream/f3b-aqueous-chemistry-pilot`

## 整理范围

F3B 围绕三种转化增加小规模真实水溶液无机化学数据：

1. `BaCl2(aq) + Na2SO4(aq) -> BaSO4(s) + 2 NaCl(aq)`：沉淀。
2. `HNO3(aq) + KOH(aq) -> KNO3(aq) + H2O(l)`：强酸/强碱中和。
3. `HCl(aq) + NaHCO3(aq) -> NaCl(aq) + CO2(g) + H2O(l)`：碳酸氢盐与酸放气。

每个反应是一个规范 Reaction，含编写的分子、完全离子和净离子 ReactionForm。生成推断候选只作为审计输出。

试点增加这些形式所需的最小离子/化合物集合，并检验 HCl 身份区分：HCl 分子 Species、已有氯化氢 Substance、盐酸水溶液 MaterialSystem。

## 证据

规范 Source 为 OpenStax《Chemistry 2e》。Evidence 范围为：

- [4.2 Classifying Chemical Reactions](https://openstax.org/books/chemistry-2e/pages/4-2-classifying-chemical-reactions)：沉淀、常见水溶液溶解性规则、AgCl/BaSO4 示例、分子/净离子表示。
- [14.3 Relative Strengths of Acids and Bases](https://openstax.org/books/chemistry-2e/pages/14-3-relative-strengths-of-acids-and-bases)：HNO3 为水中常见强酸，KOH 为常见强碱。
- [18.6 Occurrence, Preparation, and Properties of Carbonates](https://openstax.org/books/chemistry-2e/pages/18-6-occurrence-preparation-and-properties-of-carbonates)：碳酸氢盐/碳酸盐与酸生成 CO2 和水。

该教材是权威教学化学参考。证据按断言范围组织，不在每个原子计数字段上重复。

## 新增规范内容

### Entity

20 个 Entity：元素 C、S、K、Ba；Species 为 HCl 分子、Na+、K+、Ba2+、NO3-、SO4^2-、HCO3-；一个盐酸水溶液 MaterialSystem；Substance 为 BaCl2、Na2SO4、BaSO4、HNO3、KOH、KNO3、NaHCO3、CO2。

25 条 Facet 断言覆盖试点分类/行为，包括酸/碱/盐、水中强电解质、水中可溶/难溶和碳酸氢盐分类。

### Reaction

- rxn_f3b_baso4_precipitation
- rxn_f3b_hno3_koh_neutralization
- rxn_f3b_hcl_nahco3_gas_evolution

各含 molecular、complete_ionic、net_ionic 形式及显式投影假设。

### 教学视图

view_f3b_hs_aqueous_core 在 D02 电解质溶液、D03 反应类型、D06 记法/离子方程式、D08 物质分类、D10 元素与化合物中复用规范实体/反应，不按教学路径复制化学身份。

## 无净反应对照

审计案例为水溶液 NaCl + KNO3。在有界常见溶解性教学模型下，交换组合仍可溶，不编写规范转化。它是对照/审计案例，不是普遍 false 反应事实。该阶段 F2 引擎返回 no_match，不能提升为规范负面知识。

## F2 推断覆盖

该阶段 F2 规则是精确身份演示规则，不是可复用家族规则。

| 案例 | F2 结果 | 规范覆盖 |
| --- | --- | --- |
| NaCl + AgNO3 | inferred | 精确 rxn_agcl_precipitation |
| HCl + NaOH | inferred | 精确 rxn_hcl_naoh_neutralization |
| BaCl2 + Na2SO4 | no_match | 已有整理的 F3B Reaction |
| HNO3 + KOH | no_match | 已有整理的 F3B Reaction |
| HCl + NaHCO3 | no_match | 已有整理的 F3B Reaction |
| NaCl + KNO3 对照 | no_match | 有意不创建规范 Reaction |

三条 F3B 反应暴露的是可复用匹配/算子能力缺口，而非化学错误。

## 旧数据迁移比较

新记录设计后才检查相关旧材料。

- 可直接复用的化学内容：旧 barium-chloride、barium-sulfate、carbon-dioxide 的组成/名称；bacl2-na2so4 的计量和净离子化学；AgNO3 + NaCl 沉淀记录可作交叉检查。
- 需身份对照：substance:barium-chloride、ion:barium 等旧 ID 不保留为规范 ID；面向方程式的 species_id 不决定新指称层次。
- 需拆分重建：旧 Substance 同行混合 category、ambient_phase、aqueous_behavior 和离子列表；新模型分离稳定物质身份、微观离子、上下文/Facet 断言与教学投影。
- 转为 Facet/TeachingView 的分类路径：旧 category: salt/base/acid 和教学优先组织只作迁移材料，不是继承或身份。
- 被压平的上下文：aqueous_behavior: strong_electrolyte|insoluble 有化学价值，但丢失溶剂/条件；F3B 暂用 ..._in_water Facet 键，是因 F2 断言无结构化 context，以下记录该契约压力。
- 旧 Reaction reaction:bacl2-na2so4、reaction:agno3-nacl 可交叉检查；不批量导入，不保留旧 ID/形状。

## 架构压力点

### 1. F2 Facet 断言缺结构化上下文

例：BaSO4 难溶和 HNO3/KOH 强电解质行为都限于水。F1 描述 Context，但 F2 schema 的嵌入 Facet 只有 facet_key、value_state、value、evidence_ids。

暂用 solubility.insoluble_in_water、electrolyte.strong_in_water。最小建议是允许 Facet/Property 断言带结构化 context，不把维度编码进键字符串。责任在 F3A/F3 收敛契约。

### 2. TeachingView 在 F1 已规范，但不在 F2 可执行契约内

同一沉淀应出现在 D03、D06 而不复制身份。F2 只遍历 knowledge/domain 和 knowledge/rules，f2-record.schema.json 不接受 teaching_view。

F3B 在规范位置编写 knowledge/teaching/f3b_aqueous_views.yaml，并用试点测试验证成员，不改 F3A 负责的编译器/schema。最小建议为补 TeachingView schema、加载器、索引和引用验证；责任由 F3A/F3C 最终分工决定。

### 3. MaterialSystem 组成/物种组成不足以充当反应参与者

盐酸水溶液是 MaterialSystem，但配平需要 HCl 计量单位。F2 payload 能标识溶液，不能表达溶质/溶剂/物种组成，而配平器要求每个参与者有精确元素组成。

F3B 区分 HCl Species、已有 Substance 和水溶液 MaterialSystem，当前分子反应仍用 Substance 层 HCl。最小建议为定义体系参与者如何投影到配平/离子形式需要的计量/物种参与者。责任为 F3C，协调 F3A 的 ReactionForm 算子。

### 4. Rule 匹配依赖精确 ID，尚不可复用 Facet

F2 可推断 HCl + NaOH，但不能推断等类 HNO3 + KOH；可处理 AgCl 测试沉淀，不能处理 BaSO4。每条 F2 Rule 在 Facet 谓词前绑定精确 target_id。

最小建议是支持可复用有类型/Facet 模式和产物构造/解析，保持确定性证明轨迹。责任为 F3A。

### 5. 完全离子形式靠编写，尚非编译推导

BaCl2 + Na2SO4 需要旁观离子展开与消去。F2 保存 ReactionForm，但没有通用物种组成/解离投影算子。

最小建议为显式投影/物种组成算子，规定假设、证据和上下文要求；由 F3A/F3C 收敛。

## 验证

试点测试应证明：持久 ID/引用经 F2 加载器解析；离子形式电荷等于组成净电荷；关键组成精确；三条规范反应可配平；每个编写的分子/完全离子/净离子形式原子电荷守恒；语义键不冲突；证据及 Facet 证据引用可解析；视图成员解析到规范实体/反应；F2 覆盖审计可执行；候选键确定且生成候选不变为 rxn_* 源记录。

任何候选都不自动提升为规范知识。

## 收敛状态

READY_FOR_F3_CONVERGENCE

数据集刻意保持小规模，价值在于压力测试证据：真实水溶液化学适合身份/反应模型，而结构化上下文断言、TeachingView 执行支持、MaterialSystem 反应投影、可复用 Facet 规则和推导离子形式仍需收敛。
