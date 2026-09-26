# 路线图

[English](ROADMAP.md)

> 中文版对应英文文档；历史章节保留其当时范围与版本。后续契约变更须同步维护两种语言。

## 当前状态

main 已完成截至 M25 的有界工作，尚未启动下一里程碑。历史 F1/F2 与 F3A/F3B 工作流建立了本体、可执行编译契约和有界水溶液试点；其来源与分支名保留为历史事实。

## M4 — 化学模型收敛

M4 在历史 workstream/f3-convergence 分支整合上述工作流，验证以下流程：

```text
规范 YAML 源数据
→ schema、引用和证据校验
→ 有类型参与者/属性/上下文谓词
→ 确定性 RulePlan 匹配与消解
→ 有界规范产物构造
→ 精确配平与原子/电荷校验
→ 规范 Reaction 比较
→ ReactionCandidate + 证明轨迹
→ TeachingView/物种组成/推导 ReactionForm 产物
```

验收要求：上下文限定属性与稳定分类 Facet 分离；TeachingView 可执行源数据通过验证但不参与推断；明确 MaterialSystem 到计量参与者的投影边界；水溶液物种组成带精确系数和证据；中和/沉淀可复用且无精确案例引擎分支；不虚构规范实体或负面 Reaction；完全/净离子投影确定且从属所属 Reaction；语义产物字节稳定，编译器/CLI 测试全部通过。

NaCl + KNO3 无净反应对照，在沉淀规则中记录已知 driving_force = none。其他结构上可能的家族若依赖缺失知识，整体仍为 indeterminate；不输出候选或规范负面反应。

## M5 — 有界碳酸氢盐放气

家族为“水溶液强酸 + 可溶且完全强解离的碳酸氢盐 → 规范盐 + CO2 + H2O”。HCl/NaHCO3、HNO3/NaHCO3 共用 Rule；酸/电解质强度、溶解性和规范物种组成限定适用性，ionic_pair 解析盐，不解析化学式、不虚构实体。精确配平产生分子系数，既有投影得到 H+ + HCO3- → CO2 + H2O，并保留配置/证据来源。放气 Rule 显式 specializes 中和，以消解保守重叠。

## M6 — 强酸与碳酸盐放气

使用同一执行架构建立独立兄弟家族：“水溶液强酸 + 可溶且完全强解离的碳酸盐 → 规范盐 + CO2 + H2O”。CO3^2-、Na2CO3、K2CO3 验证二价物种组成和精确系数；HCl/Na2CO3、HNO3/Na2CO3、HCl/K2CO3 共用 Rule，配平器导出 2:1:2:1:1，投影均为 2 H+ + CO3^2- → CO2 + H2O。

采用兄弟规则避免 OR 语法和虚构总括 Facet。相对酸强度、弱酸适用性、pKa/平衡及更广泛物种组成能力延期到证据驱动工作。

## M7 — 铵盐与强碱及 Reaction 条件

家族为“水溶液可溶铵盐 + 水溶液强碱 + warmed → 旁观盐 + NH3(g) + H2O”。NH4Cl/NaOH、(NH4)2SO4/NaOH 共用 Rule 和 ionic_pair；精确配平处理多个铵根，投影均为 NH4+ + OH- → NH3(g) + H2O。

嵌入 Reaction 条件开始可执行：参与者签名先检索，必需条件再筛选，并在比较/投影中保留证据。NH3 气态仅限有证据的 warmed 案例，通用溶解氨平衡延期。

## M8 — 强酸与亚硫酸盐放气

家族为“水溶液强酸 + 可溶且完全强解离的亚硫酸盐 → 规范盐 + SO2(g) + H2O”。SO3^2-、SO2、Na2SO3、K2SO3 支持酸和阳离子替换；HCl/Na2SO3、HNO3/Na2SO3、HCl/K2SO3 共用 Rule 和 ionic_pair。系数为 2:1:2:1:1，净离子式为 2 H+ + SO3^2- → SO2(g) + H2O。

不改编译器、DSL、schema、产物或依赖；普通酸化足够，未加 warmed。硫酸盐保持反向对照。亚硫酸氢盐、弱酸置换、亚硫酸平衡、亚硫酸盐氧化还原和更广硫化学延期。

## M9 — 硫代硫酸盐酸分解

家族为“水溶液非氧化性强酸 + 可溶且完全强解离的硫代硫酸盐 → 规范盐 + SO2(g) + 硫单质(s) + H2O(l)”。S2O3^2-、Na2S2O3、K2S2O3、硫单质支持两个 HCl 阳离子替换案例，共用 Rule。ionic_pair 解析 NaCl/KCl，系数为 2:1:2:1:1:1，投影保留气/固/液产物，归一化为 2 H+ + S2O3^2- → SO2(g) + S(s) + H2O(l)。

增加上下文 acid.redox_character = non_oxidizing，支持有证据的水溶液 HCl；HNO3 缺兼容事实，保持 UNKNOWN。不改编译器/schema/DSL/产物/条件契约/依赖，不增加通用氧化还原引擎。

## M10 — 金属与非氧化性酸放氢

家族为“足够活泼的单质金属 + 水溶液非氧化性强酸 → 规范金属盐 + H2(g)”。Mg/Zn/Cu 元素与单质分离；Mg/Zn 相对氢为 above、Cu 为 below，固体金属无水溶液解离。嵌入且带证据的 metal.product_cation 连接 Mg/Zn 与二价离子。扩展有类型离子源，让 ionic_pair 组合关系阳离子与酸解离阴离子，不解析化学式或猜价态。

Zn/HCl、Mg/HCl 共用 Rule，系数 1:2:1:1，净离子式为 Zn + 2 H+ → Zn2+ + H2 和 Mg + 2 H+ → Mg2+ + H2。Cu 不满足已知活动性；Zn/HNO3 因强酸不代表非氧化性，保持 UNKNOWN。

版本独立升为源 schema 3.2.0、DSL 1.1.0、RulePlan 1.1.0、产物 1.2.0。产物升级来自输出的有类型离子源形状，保留历史格式和旧离子对语法读取。

## M11 — 有界碱金属与液态水放氢

家族为“常温能与水反应的固体金属 + H2O(l) → 规范水溶液金属氢氧化物 + H2(g)”。Na/K 单质与元素分离，无虚构解离；metal.water_reactivity = reacts 独立于 M10 相对氢事实。metal.product_cation 给出 Na+/K+，新通用 exact_entity 离子源给出 OH-；已有 ionic_pair 选择 NaOH/KOH，不创建身份。

一条有物态限制的 Rule 处理两种金属，系数 2:2:2:1。产物解离得到完全与净离子式 2 M(s) + 2 H2O(l) → 2 M+(aq) + 2 OH-(aq) + H2(g)，因无旁观离子，两形式相同。Cu/Zn/Mg 缺常温液态水反应事实时为 UNKNOWN，M10 不变。

源 schema 3.3.0、DSL/RulePlan 1.2.0、产物 1.3.0，分别反映精确离子编写/引用、物态编写/编译、ambient 条件和输出计划字段；保留读取 1.0.0–1.2.0。

## M12 — 单质金属与水溶液 CuSO4 置换

限定 Cu2+ 家族：“有证据的兼容金属 + CuSO4(aq) → 加入金属的规范硫酸盐 + Cu(s)”。Zn/Mg 拥有水溶液 metal.displaces_cation → Cu2+；不给 Cu/Na/K 虚构正负事实。metal.product_cation 每上下文单目标，metal.displaces_cation 可多不同目标。精确目标单跳谓词限定一条 Rule；金属关系给出 Zn2+/Mg2+，CuSO4 解离给出硫酸根，ionic_pair 选 ZnSO4/MgSO4，Cu 为精确规范产物。

系数 1:1:1:1，只拆分可溶硫酸盐，净离子式为 Zn + Cu2+ → Zn2+ + Cu 和 Mg + Cu2+ → Mg2+ + Cu。缺关系为 UNKNOWN，Cu/Na/K + CuSO4 无虚假候选；Cu + ZnSO4 不匹配精确 CuSO4。

源 schema 3.4.0、DSL/RulePlan 1.3.0、产物 1.4.0，反映关系家族基数、精确目标谓词和 PredicatePlan.target_id；保留读取 1.0.0–1.3.0。

## 覆盖与迁移工作 — 硝酸银复用验证（工作标签 M13）

复用 Ag、Ag+、AgNO3，并用 OpenStax Chemistry 2e 加固事实和物种组成；增加 Ag 单质、Zn(NO3)2、Mg(NO3)2。Zn/Mg 同时具有水溶液 Cu2+ 和 Ag+ 置换目标，真实数据验证已有多目标契约。

AgNO3 限定 Rule 复用精确关系谓词与 ionic_pair；Zn2+/Mg2+ 来自关系，硝酸根来自盐解离，Ag 为精确产物。系数 1:2:1:2，消去硝酸根后为 Zn/Mg + 2 Ag+ → Zn2+/Mg2+ + 2 Ag。Ag/Na/K/Cu 缺 Ag+ 置换断言，保持 UNKNOWN。

这是覆盖复用证明，不是新正式路线图阶段；版本仍为 3.4.0 / 1.3.0 / 1.3.0 / 1.4.0，无编译器/schema 扩展。

## M15 — 有界氢氧化物沉淀

家族为“水溶液可溶强电解质盐 + 水溶液强碱 → 难溶氢氧化物 + 可溶旁观盐”。CuSO4/NaOH、MgCl2/NaOH、FeCl3/NaOH 共用 Rule；规范解离给出 Cu2+/Mg2+/精确 Fe3+/OH- 和旁观离子，ionic_exchange.driving_force、exchange_product 选择一难溶和一可溶产物。系数分别 1:2:1:1、1:2:1:2、1:3:1:3，净离子式 M^n+ + n OH- → M(OH)n(s)。

审计否决新增 classification.metal_salt，因为会引起广泛重分类并重复实际解离/溶解性门槛。继续用已有盐/碱 Facet、aqueous 物态、强电解质/溶解性事实和唯一交换产物。缺氢氧化物身份/溶解性为 UNKNOWN；Zn/Al 两性、过量 OH-、弱碱、可变价推断和平衡不在 M15 内。

编译器与各契约不变，版本保持 3.4.0 / 1.3.0 / 1.3.0 / 1.4.0。

## M16 — heated 条件与 CaCO3 热分解试点

新增与 warmed 不同的受控 temperature_regime = heated，以 CaCO3(s) → CaO(s) + CO2(g) 验证既有通用标量条件路径。

只新增缺失 CaO、一个 Reaction、一条精确 Rule；要求固体 CaCO3 和 heated。缺温度为 UNKNOWN；ambient/warmed、错误物态、MgCO3 不匹配。系数 1:1:1，强制原子/电荷守恒，无离子形式。

既有运行时传递上下文、规范比较、轨迹和条件证据，无 heated/CaCO3 专用 Python 分支。只因词汇值将源 schema 升至 3.5.0，DSL/RulePlan 1.3.0、产物 1.4.0 不变。

这不是通用碳酸盐分解；基质派生氧化物、MgCO3/ZnCO3、通用碳酸氢盐/硝酸盐、数值温度、催化剂、水蒸气、动力学、平衡、氧化还原须另有明确语义责任。

## M17 — heated 复用与精确 NaHCO3 分解

复用不变的 heated：2 NaHCO3(s) → Na2CO3(s) + H2O(g) + CO2(g)。复用全部物质/元素，增加有证据 Reaction 和精确 Rule。缺温度 UNKNOWN；ambient/warmed、错误物态、KHCO3 不匹配。系数 2:1:1:1，校验守恒，无离子形式。H2O(g) 依据 Triton College 实验手册，其明确水和 CO2 气体释放、碳酸钠保持固体。

不新增条件词汇，不改任何编译器/schema/DSL/RulePlan/产物行为。这是精确复用验证，不能推导通用阳离子到碳酸盐或 KHCO3 分解。

## M18 — 镁与水蒸气的物态/路径试点

Mg(s) + H2O(g) —heated→ MgO(s) + H2(g)，验证既有物态与条件，无需新蒸汽 Entity 或条件。蒸汽是规范 H2O 的 gas 物态；精确 Rule 只绑定 Mg(s)、H2O(g)，选 MgO(s)、H2(g)，既有配平/校验给出 1:1:1:1。H2O(l)、ambient/warmed 不满足，缺温度 UNKNOWN。

MgO 是唯一新 Entity，无离子形式，不消耗 Mg 水溶液阳离子关系，不添加 Mg 的 water_reactivity。热液态水、通用金属/蒸汽、Fe/Zn/Ca、动态氧化物、相变、数值温度、通用氧化还原仍不支持；版本与编译器/schema 不变。

## M19 — 通用水溶液金属盐置换架构

停用精确盐 M12/M13 Rule，以 rule_m19_generic_aqueous_metal_salt_displacement 替代。绑定盐从规范完全解离配置提供唯一正/负离子；适用性只检查到解析阳离子的显式 metal.displaces_cation 成对断言，缺失 UNKNOWN，不推导活动性排序或传递关系。

共享 EntitySourcePlan 支持精确实体、绑定、指定电荷符号离子和最多一跳受控关系。新盐仍由 metal.product_cation + ionic_pair 构造；被置换产物由 ion.elemental_substance 提供，当前仅 Cu2+ → Cu、Ag+ → Ag。不解析化学式、不创建身份。

同一 Rule 重现 Zn/Mg + CuSO4、AgNO3，并增加 CuCl2 第三盐验证。旧 Reaction ID/案例保留，只迁移有效 Rule 责任。版本为 3.6.0 / 1.4.0 / 1.4.0 / 1.5.0，读取器保留 1.0.0–1.4.0。

## M20 — 显式否定 Relation 知识

Entity 关系断言新增可选 truth（默认 true）：适用正断言 TRUE，truth: false 为 FALSE，无断言 UNKNOWN。确定性拒绝完全重复及同元组正负矛盾，单目标基数仅约束正向目标。

新增有证据水溶液 Cu → Zn2+ 否定。Cu + ZnSO4 的 M19 谓词为已知 FALSE，Cu + MgSO4 保持 UNKNOWN，六个 Zn/Mg 正例仍共用 M19。否定不创建 Reaction 或全局不反应事实，不增加排序、传递、电势或氧化还原引擎。

仅源 schema 升为 3.7.0；DSL/RulePlan 1.4.0、产物 1.5.0。

## M21 — 覆盖复用批次 B

新增有证据 HBr Entity 和八个水溶液 Reaction。HBr/Br- 配置在 Na/K 两种对离子、四个既有家族中复用：中和、碳酸氢盐、碳酸盐、亚硫酸盐放气。配平、规范匹配、完全/净离子投影、溴离子消去、教学投影全部复用。

不编写 HBr 酸氧化还原特性，故 HBr/硫代硫酸盐 UNKNOWN；缺 aqueous 也 UNKNOWN。Rule、Relation、构造器、编译原语、schema、版本均不变，保持 3.7.0 / 1.4.0 / 1.4.0 / 1.5.0。

## M22 — 旧数据迁移试点 A

处理同级旧无机包修订 a6311150436038ca06fa7b9d05de39da9e1de815 的固定 20 条记录。元素、单原子离子、简单物质按指称类型、组成、电荷、符号、原子序数对照；化学式/名称只定位候选。复用 16 个身份，仅创建 OpenStax 支持的 Li Element；Cu(I)、碳酸、氯在不支持/证据边界显式跳过。

仅显式 --legacy-root 调用时读取旧包，生成字节稳定报告。不改规范源、不在运行时加载旧数据、不滥用别名、不进入 DSL/产物。合成歧义/无效案例保守拒绝，重复/乱序幂等。版本不变。

## M23 — 旧身份迁移批次 B

以 migration/legacy_identity.py 为唯一身份迁移实现，M22 入口仅薄委托。固定 100 条包括旧 48 元素、32 单原子离子和 20 代表性中性物质。映射 45 个现有身份、记录 55 个证据/指称形状跳过，不自动或人工新增 M23 规范身份。

简单物质在类型、中性电荷、组成验证后，还需已整理指称形状门槛和规范化学式语义键佐证。网络、同素异形、配合/物种组成、弱平衡及未整理证据仍跳过。M22 可重现，推断不导入迁移代码，不迁移 Reaction，版本不变。

## M24 — 旧反应迁移试点 A

一个离线实现处理 18 条旧 Reaction，复用身份对照；先验证角色、正系数、公因数缩放、物态、受控条件、原子电荷守恒、方向，再调用既有规范比较。16 条映射现有中和/沉淀/放气/铵盐碱/置换/热分解；CaCO3/HCl 和催化氨氧化显式跳过。不创建 Reaction/Rule。

旧离子式只作与规范派生形式比较的非权威诊断。反向、物态不兼容、缺失/冲突必需条件、未解析参与者、歧义、错误系数和守恒失败均保守拒绝。报告确定，不改规范源或进入运行依赖。催化剂/光、丰富条件、多原子身份、缺规范 Reaction、全量迁移留作 M25 或之后压力；版本保持 3.7.0 / 1.4.0 / 1.4.0 / 1.5.0。

## M25 — 已完成反应迁移审计

同一实现只读审计全部 152 条：最终 20 映射、123 不支持跳过、9 条可逆记录保守拒绝、0 歧义、0 自动创建。132 条未映射分为 88 身份缺口、25 上下文缺口、10 普通整理缺口、9 化学架构缺口、0 旧结构无效。旧离子投影仍仅诊断。

独立于旧数据权威补齐一项高价值整理：CaCO3(s) + 2 HCl(aq) → CaCl2(aq) + CO2(g) + H2O(l)，复用已有身份、物态、物种组成和权威证据。不增加 Evidence/Rule；可溶碳酸盐 Rule 不变，不能推断固体 CaCO3。规范覆盖与推断覆盖不同。

审计后不存在被迁移机制阻塞的高价值、当前 schema 兼容案例。余项需要证据整理，或另行授权身份/上下文/平衡/路径架构。历史 M6_EXIT_READY = true 表示迁移退出，不是 M6 碳酸盐全部推断完成；无需额外迁移里程碑。版本不变。

## 仍在已实现范围之外

- 全部高中数据填充，或超出 M22–M25 审计边界的自动迁移；
- 过渡金属氧化还原、浓酸/钝化、有机家族；
- 可变价产物选择、超出有证据成对水溶液盐的置换、更广金属水反应、通用活动性/电极电势；
- 通用碳酸盐到氧化物、碳酸氢盐到碳酸盐映射，或超出精确 M16/M17 的热分解；
- 超出精确 M18 的通用金属/水蒸气或热液态水；
- 通用平衡/物种组成求解；
- 硝酸/硫代硫酸盐预测、氧化数/电极电势推断和更广氧化还原；
- UI 接入、数据库服务、Neo4j、RETE；
- 无性能证据的 Rust/C++ 或原生加速；
- 推测性插件基础设施。
