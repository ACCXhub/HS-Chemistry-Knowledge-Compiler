# 架构决策记录

[English](DECISIONS.md)

> 中文版对应英文文档；历史章节保留其当时范围与版本。后续契约变更须同步维护两种语言。

状态：**截至 M25 的已实现决策；早期章节保留历史上下文**

当前纠正：以下 ADR 保留作出决策时的范围。M8 硝酸适用性、M21 HBr 非氧化性知识及 M25 固体 CaCO3 推断限制，已由 [2026-09-26 审计](COVERAGE_AUDIT.zh-CN.md)更新；[应用数据包](contracts/APPLICATION_API.zh-CN.md)共用原有化学验证与推断责任。

## ADR-F1-001 — Entity 类型对齐

规范 entity_kind 为 element | species | substance | material_system。Ion 使用 species_kind: ion；溶液/混合物使用 material_system_kind。

## ADR-F1-002 — Structure 责任

需要持久结构引用时，Structure 具有稳定身份。表示从属于结构；Bond 默认以结构局部键嵌入。

## ADR-F1-003 — 源数据规范化

Composition、Context、ReactionParticipant、Condition、TeachingViewPath 和默认 Bond 是嵌入值，除非独立生命周期/溯源需要持久身份。

## ADR-F1-004 — ReactionCandidate 生命周期

纯编译生成内容派生的确定性 candidate_key，不创建 UUID。持久审核状态可另有 rcand_*，但保留不可变候选键。

## ADR-F1-005 — Rule 身份责任

声明式 Rule 是 rule_* 身份、语义版本、证据、来源和规则消解关系的唯一规范主体。

## ADR-F1-006 — Reaction 身份与表示

采用 Reaction + ReactionForm。分子、完全离子、净离子、符号和热化学形式可投影同一转化；化学上不同的半反应仍是关联的独立 Reaction。

## ADR-F1-007 — 宏观/微观反应指称

参与者可引用 Species、Substance、MaterialSystem。跨层投影必须声明物种组成/解离假设。

## ADR-F1-008 — 规范专业文档位置

专业规范文档位于 docs/domain/**、docs/pedagogy/**、docs/contracts/**、docs/inference/**，不在根目录另建重复责任文档。

## ADR-F1-009 — 编译契约责任

数据契约负责外部产物/源数据；编译器负责内部计划、索引、缓存、算子编译和运行布局。

## ADR-F1-010 — 身份独立于显示

名称、化学式、别名、路径、文件顺序和运行时紧凑 ID 不定义持久化学身份。

## ADR-F1-011 — 开放世界事实语义

缺失、显式 unknown、not_applicable、已知值（含 false）保持不同；缺失不得静默转成 false。

## ADR-F1-012 — 规范 Reaction 不等于 ReactionCandidate

规范比较不会提升生成候选。提升仍是有证据的源数据整理操作。

## ADR-F1-013 — 语言与优化

源契约和 DSL 保持语言中立。Python 是参考实现；性能修改需证据和稳定语义边界。

## ADR-F2-001 — 确定性规范 JSON

语义哈希/产物采用 UTF-8、字符串/键 NFC 规范化、映射字典序、紧凑分隔符、整数语义数值、语义列表顺序；不含时间戳、本地路径、进程 ID、遍历顺序元数据。candidate_key 为 cand_sha256_ 加规范候选语义内容的 SHA-256。

## ADR-F2-002 — 可执行 YAML 与 JSON Schema 边界

人工编写化学/规则使用 YAML。结构校验先于稳定 ID/引用、规则编译、配平与守恒。物态属于参与者/模板上下文，不属于身份。

## ADR-F2-003 — 源 Rule 与内部 RulePlan

源 Rule 编译为有类型的内部 RulePlan。配平接受固定规范反应物/产物，规范比较发生在产物解析与守恒验证之后。文件顺序和整数优先级不是消解语义。

## ADR-F3A-001 — 可复用参与者模式

模式可约束精确身份、entity_kind、species_kind、必需/禁止 Facet。Facet 用正常三值谓词计算，不能隐藏闭世界匹配。

普通家族扩展通常增加规范数据和声明式 Rule，不增加引擎分支。AgCl 沉淀以类型/Facet 替换 NaCl/AgNO3 精确绑定，规范候选结果不变，验证此架构。

## ADR-F3A-002 — 小型有类型谓词注册表

源语义采用 equals、not_equals、is_known、in_set，不使用宿主函数名或任意表达式。各算子声明允许主体、输入类型、期望参数形状和 UNKNOWN 行为。该阶段支持 context、facet；关系和数值算子待可执行源数据证明必要后再加。

## ADR-F3A-003 — 事实状态与来源

区分 known、显式 unknown、not_applicable、编译器观察到的 absent；false 仍是已知值。来源为 intrinsic | contextual | derived，请求上下文记为 contextual。缺失不编写成假事实记录。

## ADR-F3A-004 — 保守静态重叠分析

在一个 decision_domain 内分析参与者数量/类型、精确身份、必需/禁止 Facet 和简单上下文相等。不能证明不相交时，可保守记录 potential_overlap。潜在重叠且结果非等价必须有显式语义关系；严格编译拒绝未消解重叠并报告双方 ID、原因/签名。

## ADR-F3A-005 — 显式规则消解图

支持 overrides、specializes、fallback_for、equivalent_to、mutually_exclusive_with。未知引用、自关系、矛盾等价声明和优先环是编译错误。overrides/specializes 由声明方优先；fallback_for 在两者适用时由被引用方优先。运行时优先关系传递且确定。

## ADR-F3A-006 — 有界规范产物构造

F3A 限于 exact_entity、规范 semantic_key。必须返回唯一已有 Entity；零匹配或歧义为 product_unresolved，不能虚构身份。可变价等化学歧义在源数据/上下文未确定唯一目标前保持未解析。

## ADR-F3A-007 — 假设限定 ReactionForm 投影

ReactionForm 从属于所属 Reaction，不产生第二身份。投影声明 aqueous medium、strong-electrolyte dissociation、precipitate integrity、weak-electrolyte molecular retention 等稳定 required_assumptions；全部提供后才可用。F3A 不实现通用水溶液求解器；半反应独立。

## ADR-F3A-008 — 兼容版本轴分离

该阶段独立坐标为源 schema 3.1.0、DSL 1.0.0、RulePlan 1.0.0、外部产物 1.1.0。产物带格式版本，manifest 带全部坐标；消费者拒绝不支持版本。不作更广长期后向兼容承诺。

## ADR-F3A-009 — 结构化诊断代码

失败使用确定性的 code、stage、message 和可选排序 details。区分 schema 无效、未解析引用、未知适用性、阻断、无匹配、规则歧义、编译重叠、产物解析、配平、原子/电荷校验、规范无匹配/冲突。

## F3A 当时尚未实现的内容

关系谓词、数值化学谓词、任意表达式、通用物种求解、广泛家族填充、氧化还原/有机推断、数据库/运行服务、RETE、原生加速均延期。

## ADR-M4-001 — 上下文限定属性

电解质强度、溶解性等行为是带结构化上下文的类型属性；稳定分类仍为 Facet。Facet/Property 保持 TRUE/FALSE/UNKNOWN，缺失不转成 false。

## ADR-M4-002 — 有证据的水溶液投影

规范物种组成配置拥有精确 Species ID、有理系数、上下文、模型和证据。有界离子构造组合规范组成/电荷，解析唯一已有中性 Substance，不解析显示化学式、不创建 Entity。

MaterialSystem 没有显式计量/物种投影就不能配平。完全/净离子形式是所属 Reaction 的确定性推导，保留来源/证据，不成为独立 Reaction。

## ADR-M4-003 — 教学与生成事实边界

TeachingView 是经 schema/引用校验的可执行规范源，但不参与推断。生成候选和派生形式保持为编译输出，不能隐式进入规范反应源。

## ADR-M5-001 — 强酸与碳酸氢盐边界

要求水溶液分类酸具有 acid.strength = strong、electrolyte.strength = strong；另一方同时为盐和碳酸氢盐，具 strong electrolyte、soluble。缺事实 UNKNOWN，无候选。

复用规范解离和 ionic_pair 造盐，CO2/H2O 解析已有实体，候选保留精确配置/证据。禁止化学式解析、HCl/NaHCO3 精确引擎分支和运行时外部事实。Rule specializes 中和，显式消解重叠，不用顺序或整数优先级。

## ADR-M6-001 — 强酸碳酸盐兄弟规则

CO3^2- 为二价规范 Species，Na/K 碳酸盐带精确组成、完整解离与证据。每 CO3^2- 对应 2 Na+/K+ 是源数据，不是运行时由化学式猜得。

碳酸盐 Rule 与 M5 并列，不用析取、总括 Facet 或隐藏计量分支。两者复用 ionic_pair、配平、投影；双酸计量由配平器推得，Rule 不含特定系数或反应物 ID。

Rule specializes 中和，与碳酸氢盐 mutually_exclusive_with；两分类应标识不同反应物，同时适用是模型/数据矛盾，报告歧义。

## M6 当时尚未实现的内容

相对酸强度、弱酸碳酸盐、pKa、平衡方向、浓度置换、CO3/CO2/H2CO3 平衡、缓冲和通用物种组成延期；只支持水溶液强酸与可溶强解离碳酸盐。

## ADR-M7-001 — 可执行嵌入 Reaction 条件

条件为嵌入且有证据的受控 key/value；M7 只执行 medium = aqueous、temperature_regime = warmed。重复键和未解析证据为源错误；条件不另有普通持久 ID，自由文字不作语义事实。

先按规范参与者签名索引，再按各 Reaction 必需条件筛选。允许额外请求上下文；缺失/冲突不兼容；多个兼容仍冲突；既有无条件 Reaction 仍兼容。候选身份继续包含请求上下文，M4–M6 键不变。

源/产物形状分别升至 3.1.0、1.1.0，读取保留 1.0.0；DSL/RulePlan 1.0.0 不变，因为规则语法/计划未改。

## ADR-M7-002 — 带条件铵盐/强碱放气

增加 NH4+、NH3、NH4Cl、(NH4)2SO4；classification.ammonium 是含铵盐/Species 稳定 Facet。Rule 要求可溶强解离铵盐、强碱/强解离、水溶液、warmed；复用解离/ionic_pair，不解析化学式、不创建 NH4OH。

规范反应明确表达加热检验的 NH3(g)。OpenStax 支持铵盐/强碱制氨，Cambridge IGCSE 定性分析要求提供 warming。一般 NH4+ + OH- → NH3(aq) + H2O 和氨平衡不在气体 Rule 内。

配平器生成两条分子式；投影器在旁观消去后约去共同有理比例，使硫酸铵的两份当量归一化为 NH4+ + OH- → NH3(g) + H2O，保留条件/证据。

与中和及两种强酸碳酸盐在同域保守重叠，声明互斥，因为有界强碱不能同时是它们要求的强酸。跨域沉淀不进入该重叠图，不用优先级/顺序。

## M7 当时尚未实现的内容

无条件溶解氨投影、氨平衡常数、弱酸碱通用推理、缓冲、更广氮化学和亚硫酸盐/SO2 放气延期。

## ADR-M8-001 — 在既有流程上添加强酸亚硫酸盐兄弟规则

SO3^2-、SO2、Na2SO3、K2SO3 具有规范组成、电荷和有证据水溶液配置。Rule 与 M5/M6 并列，保留强酸门槛，增加独立 classification.sulfite，不引入放气阴离子总括 Facet、化学式解析、OR 或精确反应物分支。

ionic_pair 造旁观盐，配平器导出 2:1:2:1:1，净式为 2 H+ + SO3^2- → SO2(g) + H2O。只需 aqueous，普通酸化足够，不写 warmed/D05 实验映射，M7 条件比较不变。

specializes 中和，与碳酸氢盐、碳酸盐、铵盐/强碱互斥，依据独立分类及酸碱方向。硫酸盐不能因化学式相似而匹配。契约和依赖不变，版本 3.1.0 / 1.0.0 / 1.0.0 / 1.1.0。

## M8 当时尚未实现的内容

亚硫酸氢盐、弱酸、相对酸强度、亚硫酸和 SO2/H2SO3 平衡、亚硫酸盐氧化、SO2 还原/漂白、硫氧化态、H2S、硫代硫酸盐及更广硫化学延期。

## ADR-M9-001 — 上下文限定硫代硫酸盐分解与混合物态产物

S2O3^2-、Na/K 硫代硫酸盐、硫单质为规范身份；classification.thiosulfate 区别于亚硫酸盐/硫酸盐。硫 Substance 不等于 Element；S:1 只是精确配平基准，不声明单原子或同素异形结构。

强酸还可能为氧化性酸，故另需 acid.redox_character = non_oxidizing。HCl 有证据，HNO3 不虚构兼容/不兼容事实，保持 UNKNOWN。

Rule 用酸/盐/硫代硫酸盐分类及强度、电解质、溶解性、氧化还原上下文，复用构造/配平/投影；同时保留 aqueous 盐、SO2(g)、S(s)、H2O(l)，Na/K 均归一化为 2 H+ + S2O3^2- → SO2(g) + S(s) + H2O(l)。

不引入 warmed、精确引擎分支、化学式解析、通用氧化还原、新依赖、契约变化或 D05 映射；版本仍 3.1.0 / 1.0.0 / 1.0.0 / 1.1.0。

## M9 当时尚未实现的内容

硝酸/硫代硫酸盐产物、通用酸氧化还原分类、氧化数/电势、碘氯与硫代硫酸盐、H2S/多硫化物、硫同素异形结构、弱酸泛化及更广氧化还原延期。

## ADR-M10-001 — 嵌入有类型产物阳离子关系与离子源

使一类 Relation 可执行，不引入通用图。已知为金属的单质 Substance 可拥有带证据/上下文的 metal.product_cation，目标必须是正电规范离子 Species。源/目标在语义引用阶段验证，不等产物构造再检查。断言无普通 UUID，来源由源、受控键、目标、上下文、证据元组确定。查找仅一跳，复用上下文具体程度；零目标显式，同等具体的多个目标保留供唯一性解析器报告歧义。

ionic_pair 接受独立 cation_source/anion_source，组合金属 relation_target 与酸 speciation，再委托既有中性离子对电荷/组成匹配。旧 cation_from/anion_from 编译为解离 IonSourcePlan，仍有效；不解析化学式、猜价态、造实体。

源 schema 3.2.0、DSL/RulePlan 1.1.0。外部计划从平面字段转成嵌套离子源，产物独立升 1.2.0；读取接受 1.0.0/1.1.0/1.2.0。仅实际消费关系的候选输出关系来源，M4–M9 原键不变。

## ADR-M10-002 — 有界金属/非氧化性酸放氢

Mg/Zn/Cu 元素与固体单质分离，无假水溶液解离。relative_to_hydrogen 的有证据事实为 Mg/Zn above、Cu below；Mg/Zn 另有 Mg2+/Zn2+ 产物关系。酸强度与酸氧化还原特性独立。

Rule 要求单质金属分类且 above、aqueous 强酸/强电解质且 non_oxidizing，解析规范氯化物和 H2(g)。系数 1:2:1:1；投影保留固体，只拆 HCl 和可溶盐，消氯后为 Zn/Mg + 2 H+ → Zn2+/Mg2+ + H2。

Cu 在 M10 上已知失败、不输出放氢；其他可能路径缺知识时整体仍可不确定。Zn/HNO3 不虚构非氧化性，UNKNOWN。数值电势、氧化态、电子/半反应配平、可变价、钝化、浓度、通用氧化还原延期。

## ADR-M11-001 — 精确离子源与参与者物态限制

exact_entity 成为第三种 IonSourcePlan，要求已有离子且电荷符号符合位置。运行时对修改过的内存知识重复有限检查，纳入目标证据，再委托 ionic_pair；不造实体、解析式或加 OH 专用构造器。

模式可限制 phase，在谓词前检查，也用于同域保守重叠。M11 要求固体金属/液态水，H2O(g) 不进入液态水 Rule。Reaction 条件加入 ambient。

源 schema 3.3.0；新语法使 DSL 1.2.0；IonSourcePlan.target_id、ParticipantPatternPlan.phase 使 RulePlan 1.2.0；外部序列化使产物 1.3.0。保留读取 1.0.0–1.2.0。

## ADR-M11-002 — 有界碱金属/液态水放氢

Na/K 为不同于 Element 的固体 Substance，具有 ambient 限定 water_reactivity = reacts 和到 Na+/K+ 的单跳关系。阳离子身份关系不加介质限定，因为不是解离断言；Mg/Zn 原 aqueous 关系不变。金属和 H2O 均不添解离配置。

Rule 匹配固体金属、精确 H2O(l)，检查常温反应性，用关系阳离子 + 精确 OH- + 中性解析器构造氢氧化物，H2 为另一个已有精确产物。两种金属均导出 2:2:2:1，无 Na/K 引擎分支或虚构产物。

规范 Reaction 要求 ambient；产物解离产生 2 M(s) + 2 H2O(l) → 2 M+(aq) + 2 OH-(aq) + H2(g)，完全/净式相同。Cu/Zn/Mg 缺水反应事实为 UNKNOWN，不从 M10 推升。独立 metal_liquid_water_hydrogen 域与酸置换不同，不加虚构关系/优先级。

蒸汽/热水、Ca、钝化、活动排序、可变价、氧化态、半反应、电子配平、通用金属水/氧化还原延期。

## ADR-M12-001 — 家族级关系基数与精确目标适用性

metal.product_cation 为 one_target_per_context；同源/上下文不能不同阳离子。metal.displaces_cation 为 many_targets_per_context，允许不同正离子目标，但重复源/键/目标/上下文无效。都保留单质金属 Substance → 正离子 Species 类型边界，水溶液真值在结构化 context，不编码入关系名。

只增加 equals expected: true 的精确目标单跳谓词，需有效绑定、受控键和值域正确规范目标。匹配已知真，无匹配 ABSENT/UNKNOWN。同目标同等具体断言合并证据；事件保留源/键/目标/上下文/证据，只有最终适用绑定进入候选来源。

源 schema 3.4.0、DSL 1.3.0、RulePlan 1.3.0（target_id）、产物 1.4.0；读取保留 1.0.0–1.3.0。

## ADR-M12-002 — CuSO4 限定的可复用置换

Cu2+、CuSO4、ZnSO4、MgSO4 有精确组成、电荷、盐/硫酸盐分类和有证据完全解离。Zn/Mg 有到 Cu2+ 的 aqueous 正置换断言；Cu/Na/K 无推导或编写的关系，含未建模水竞争在内的缺成对知识均 UNKNOWN。

Rule 匹配通用固体金属 + 精确 CuSO4(aq)，由关系限定；金属产物阳离子和 CuSO4 的 SO4^2- 经 ionic_pair 造盐，Cu 为精确第二产物。系数 1:1:1:1，只解离可溶硫酸盐，消去后 Zn/Mg + Cu2+ → Zn2+/Mg2+ + Cu。

独立 aqueous_copper_salt_displacement 域不与既有家族静态重叠，不加关系/优先级。无化学式解析、价态猜测、产物虚构、反向/链式关系、数值活动性、电势、氧化数、通用氧化还原或任意金属盐解析。

## M12 当时尚未实现的内容

一般金属 A + 金属 B 盐仍需有证据阳离子发现、离子到元素映射、成对/有序活动性、被置换金属构造、水竞争、可变价、钝化、浓度/温度；不作为隐藏 M12 行为。

## 覆盖决策 — M13 硝酸银复用验证

Zn/Mg 各有 Cu2+、Ag+ 水溶液置换目标，阳离子产物仍单目标，完全重复无效。保留 Ag/Ag+/AgNO3 ID、历史测试证据，新增 OpenStax 支持银身份、硝酸盐可溶/强电解质、AgNO3 解离和有界 Zn/Mg 置换。

精确 AgNO3 Rule 完全复用关系谓词、关系阳离子、解离阴离子、中性解析器，选 Zn(NO3)2/Mg(NO3)2 和 Ag，系数 1:2:1:2，离子式消硝酸根，无 Ag 编译器特例或虚构身份。

Ag/Na/K/Cu 不添合成 Ag+ 断言，保持 UNKNOWN，保留水竞争/可变价压力。版本 3.4.0 / 1.3.0 / 1.3.0 / 1.4.0。

## ADR-M15-001 — 无新增金属盐 Facet 的盐/强碱交换

在 aqueous_exchange 域增加 Rule，要求 aqueous 盐且 soluble/strong electrolyte，aqueous 碱且 strong base/strong electrolyte。既有 driving_force 用双方配置，要求恰好一已知难溶和一已知可溶产物，再由 exchange_product 返回已有身份。与两盐沉淀模式互斥；未来数据使二者同时适用时报告歧义，不按顺序选取。

全库审计发现 metal_salt 会覆盖几乎所有非铵盐，引起历史重分类却不增加实际所需知识，故不加。金属离子来自盐的有证据解离；FeCl3 指定精确 Fe3+，无铁元素推导、化学式价态猜测或图遍历。

Cu(OH)2、Mg(OH)2、Fe(OH)3 为难溶 Substance，无假解离。缺产物/溶解性/aqueous、错误物态和不支持盐为 UNKNOWN 或不匹配。投影只消规范旁观离子。不隐含两性溶解、过量 OH-、配离子、Ksp、弱碱、平衡或氧化还原。版本不变。

## ADR-M16-001 — heated 受控值与精确 CaCO3 试点

heated 区别于 warmed，不表示排序、数值温度或相互蕴含。通用标量路径已支持缺失 UNKNOWN、已知不同 FALSE、匹配保留条件证据，不加专用运行分支。

精确 Rule 仅匹配 CaCO3(s)+heated，选择 CaO(s)、CO2(g)，系数 1:1:1，守恒器不变，无离子形式。只新增 CaO，复用 CaCO3、CO2、Ca、C、O。

不分类或动态映射碳酸盐为氧化物；MgCO3 heated 不支持。通用碳酸盐、碳酸氢盐、硝酸盐、催化剂、蒸汽、动力学、平衡、氧化还原因无基质派生产物语义而延期。

源 schema 3.4.0 → 3.5.0；语法/计划/产物形状不变，DSL/RulePlan 1.3.0、产物 1.4.0。source.py 只改源版本坐标，运行行为不变。

## ADR-M18-001 — 蒸汽是 gas H2O 加 heated 上下文

蒸汽使用既有 H2O 身份、气态参与者和 heated；不新建 Substance 或 steam 条件，不等同于加热液态水。通用物态匹配拒绝 H2O(l)，上下文对 ambient/warmed 为 FALSE，缺温度 UNKNOWN。

精确 Rule 绑定 Mg(s)、H2O(g)，选 MgO(s)、H2(g)。MgO 唯一新增；不用 Mg 水溶液产物关系、不加或滥用 water_reactivity、不动态造氧化物。系数 1:1:1:1；守恒是结构校验，不是通用氧化还原推理，无离子形式。

任何编译器/schema/DSL/计划/产物契约不变。热液态水、相变、通用金属蒸汽、其他金属路径、氧化物选择、氧化还原预测不在 M18。

## ADR-M19-001 — 有界实体源负责通用置换间接解析

共享 EntitySourcePlan 服务动态关系谓词和源派生产物，仅精确实体、绑定、唯一正/负解离离子及非 Relation 源的一跳目标。拒绝关系嵌套，不是递归遍历/查询语言。

唯一有效金属盐 Rule 绑定通用固体金属与 aqueous 盐。盐配置动态给出阳离子，金属必须拥有到它的有证据成对置换断言。缺失/歧义配置或缺关系均 UNKNOWN。metal.product_cation + ionic_pair 选新盐，不猜式/价态。

ion.elemental_substance 从正离子映射唯一单质金属，one_target_per_context；只编写所需 Cu2+ → Cu、Ag+ → Ag。被置换产物恰好走一跳，保留配置/证据，不反向推断。

旧精确 M12/M13 Rule 停用，因为没有弃用/别名机制，保留会重复语义；实体/Reaction ID、证据、案例、教学和历史 ADR 保留。一条 Rule 覆盖授权 Zn/Mg 与 CuSO4/AgNO3/CuCl2。活动排序、传递、显式否定、水竞争、可变价、钝化、浓度、通用氧化还原该阶段仍延期。

版本升为 3.6.0 / 1.4.0 / 1.4.0 / 1.5.0，保留历史 1.0.0–1.4.0 读取。

## ADR-M20-001 — 上下文 Relation 的显式真值

正负成对知识共存于 Entity 的 relation_assertions；可选布尔 truth 默认 true。false 是精确源/键/目标/规范上下文的有证据否定；无适用断言为 ABSENT/UNKNOWN。最具体集合决定结果，同等具体混合真值是确定性语义错误，不按顺序选择。

拒绝完全重复和同元组正负矛盾。基数只计正向目标：product_cation、elemental_substance 每上下文一正目标，可记录任意不同有证据拒绝目标。产物目标解析只暴露正断言。

仅新增 aqueous Cu(s) displaces Zn2+ = false，由 OpenStax 支持，使 Cu/ZnSO4 的 M19 谓词 FALSE；Cu/Mg2+ UNKNOWN，六个 Zn/Mg 正例 TRUE。这是编写的成对知识，不是排序、传递、电势运行或通用氧化还原。

否定只说明一个谓词/路径不适用，不创建负面 Reaction、规范无反应记录或全局不反应事实。其他家族可使整体不确定。轨迹保留目标、真值、上下文、证据；正候选来源形状不变，否定诊断增加 truth: false。

源 schema 3.7.0；DSL/RulePlan 1.4.0、产物 1.5.0 不变，历史读取兼容。

## ADR-M21-001 — 既有家族复用 HBr 对离子覆盖

因已有 Br-/NaBr/KBr，选择紧凑 HBr 扩展。一个 OpenStax 支持 Entity 拥有组成、aqueous 强酸/强电解质和完全解离；八条 Reaction 覆盖 Na/K 中和、碳酸氢盐、碳酸盐、亚硫酸盐。

全部产物用既有 ionic_pair/精确路径、既有配平；投影拆 HBr 和可溶溴盐，消 Br- 得既有家族净式。HBr/硫代硫酸盐缺 redox_character，刻意 UNKNOWN，不泛化酸置换/氧化还原。

仅数据/证据/案例/教学修改，不新增 Rule/关系家族/构造器/Python 化学分支；版本 3.7.0 / 1.4.0 / 1.4.0 / 1.5.0。

## ADR-M22-001 — 迁移映射是操作来源，不是化学事实

旧无机包是显式离线输入。固定 20 ID 清单，每输入一个排序处置，五种封闭状态。旧 ID、包修订、输入摘要、对照依据、创建证据、跳过/错误代码属于报告，不是 Entity 别名、规则事实或编译产物。

公式/名称不能单独定身份。元素需类型/符号/原子序数；单原子离子需 Species/ion、精确组成、电荷；简单化合物需 Substance/pure-compound、精确组成和中性。多个验证候选为 ambiguous，无效形状 rejected_invalid，不按顺序决胜。

只有单独编写的规范记录通过正常校验，且迁移证据门槛确认非测试权威证据后，才承认创建。仅接纳 ent_element_li 与 ev_m22_lithium_identity。旧审核状态和验证目标不满足门槛。工具只写确定性报告，重跑不复制 Entity，编译器不依赖旧仓库。推断/版本不变。

## ADR-M23-001 — 唯一身份迁移实现与严格 Substance 范围

引擎归于 migration/legacy_identity.py，旧 M22 模块只委托；清单/报告显式不可变。新样本恰好 100 条：48 元素、32 单原子离子、20 物质，不扫描导入全库。

元素/离子契约不变。简单中性物质显式选择严格范围：类型/pure-compound、中性电荷、组成是最终事实，精确规范化学式键佐证，已整理指称形状排除网络/同素异形/配合或物种组成案例。公式不单独创建/选择 Entity，多候选仍歧义。

45 映射，55 因权威身份依据或安全指称形状未整理而跳过。无 Entity/Evidence 新增，不改源，不迁 Reaction；M22 经兼容入口可重现，运行时不导入迁移，版本不变。

## ADR-M24-001 — 旧 Reaction 只对照既有规范事实

migration/legacy_reaction.py 负责离线编排，legacy_identity.py 唯一负责参与者。固定旧修订 a6311150436038ca06fa7b9d05de39da9e1de815 的 18 案例涵盖中和、沉淀、碳酸盐/碳酸氢盐/亚硫酸盐放气、铵盐碱、Zn/CuSO4、CaCO3/NaHCO3 热分解。16 唯一映射；CaCO3/HCl 无规范对照，催化氨氧化缺催化剂语义，故跳过。禁止创建，created_canonical = 0。

所有参与者经批准身份语义，再验角色、正整数系数、重复合并、公因数约化、原子电荷守恒、显式物态和受控条件。复用规范签名/条件比较，不倒转方向、不推测 aqueous；缺条件/冲突、未知字符串、未解析身份、无效形状、守恒失败、多匹配均保守拒绝。有限单质身份范围允许规范元素化学式键辅助单一 Zn/Cu 对照，不改 M22/M23 默认。

旧分子/离子式只作审核证据。净式诊断 compatible/unavailable/unsupported_inconsistent 不得选择、创建或重写 ReactionForm；规范形式仍由 Reaction 和配置负责。报告是操作来源，不改源、不成为编译依赖。缺反应、催化剂/光/条件、多原子身份为独立未来压力；版本不变。

## ADR-M25-001 — 全量审计结束迁移机制工作，不做批量导入

扩展既有 legacy_reaction.py 审计固定 manifest 全部 152 条，不另建引擎。保留 M24 处置，未映射逐条加确定性后续行动分类。最终 20 映射、123 不支持、9 可逆拒绝、0 歧义、0 自动创建；缺口为 88 身份、25 上下文、10 普通整理、9 化学架构、0 旧数据无效。可逆因当前不负责平衡方向而属架构缺口，处置仍保守拒绝。

Layer A 严格只读；Layer B 仅接纳 rxn_m25_hcl_caco3_gas_evolution，权威性来自已有碳酸盐/酸和身份依据，不是旧来源。精确固/水溶液/气/液参与者守恒，既有配置推导完全/净式。不添证据、Rule、schema、编译分支或条件；可溶碳酸盐 Rule 仍需 aqueous、soluble、complete dissociation，不能推断固体 CaCO3。规范覆盖不等于 Rule 覆盖。

余项已分类，需证据整理或另设计身份、受控上下文、可逆/平衡、氧化还原、竞争路径。分子对照成功时，多原子旧离子仍仅为诊断阻塞。报告确定，运行时独立于 migration/**。满足迁移 M6 退出：M6_EXIT_READY = true，无需 M26；版本保持 3.7.0 / 1.4.0 / 1.4.0 / 1.5.0。
