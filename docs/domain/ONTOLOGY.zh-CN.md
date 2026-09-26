# 规范领域本体

[English](ONTOLOGY.md)

> 中文版对应英文文档；历史章节保留其当时范围与版本。后续契约变更须同步维护两种语言。

状态：**M12 规范本体，包含有界金属/铜盐置换**

## 1. 建模原则

采用浅层身份类型、独立 Facet 分类维度、有类型关系、结构化上下文和推导投影。不要把教材章节树编码为类继承。

## 2. 化学身份类型

```text
Entity
├─ Element（元素）
├─ Species（微观物种）
│  ├─ Atom（原子）
│  ├─ Ion（离子）
│  ├─ Molecule（分子）
│  └─ 课程确有需要的其他微观物种
├─ Substance（纯物质）
└─ MaterialSystem（材料体系）
   ├─ Mixture（混合物）
   └─ Solution（溶液）
```

`Ion` 是 `Species` 的子类型标记，不是与其并列的 `entity_kind`。

`Substance` 是宏观纯物质身份。单质 Substance 不同于抽象 Element；用于配平的最小元素组成并不自动声明分子结构或同素异形体。`MaterialSystem` 是复合样品/体系身份：溶液、混合物、胶体、平衡体系和实验专用组成在确需持久引用体系本身时使用它。

## 3. 结构

`Structure` 是独立于任何表示的稳定领域对象，可描述分子连接/几何、离子晶格、金属结构、共价网络或课程相关的其他结构语义。

SMILES/InChI 类编码、Lewis 结构、结构式、晶体描述和图片/资源均为表示，不拥有结构身份。化学键默认嵌入结构；官能团是关联结构/Species 的可复用结构基元或 Facet 概念。

## 4. Facet 分类维度

Facet 表达相互独立的分类维度，包括元素特征、化合物/材料家族、酸/碱/盐/氧化物类别、氧化物行为、有机类别、官能团、电解质行为、酸碱角色、氧化还原角色和反应类别。

依赖上下文的角色必须是上下文断言，不能成为永久标签。

## 5. 事实

事实可为内禀、上下文限定或推导事实。若条件变化而身份不变，就需要上下文。

常见维度包括物态、溶剂/介质、浓度、温度、压力、pH 范围、气氛、试剂可用性、催化剂、光/热/电刺激和实验装置。

上下文化学属性也可限定反应家族适用性。例如酸强度和酸氧化还原特性是独立事实；已知强酸不等于非氧化性路径适用。

金属相对氢的活动性同样是上下文化学知识，不是反应结果 Facet。M10 只使用证据支持的 `above`、`below`，不推导数值活动性顺序或电极电势。

M11 将常温液态水反应性与相对氢的活动性分开。`metal.water_reactivity = reacts` 是由 `temperature_regime = ambient` 限定的 PropertyFact，不是分类 Facet 或反应名称。缺失保持 UNKNOWN；不从 `classification.metal` 或 M10 活动性知识推导该事实。

## 6. 关系

Relation 是有类型的语义断言，不是通用图边。关系家族可涉及组成、结构、酸碱共轭、转化、推导、证据、教学和反应组合。

M10 的可执行子集包含单跳受控关系 `metal.product_cation`：定义域为 `classification.metal` 已知为真的单质 Substance，值域为正电荷离子 Species。金属 Substance 内嵌带上下文和证据的断言；除非后续确需独立生命周期，否则不另设身份。这是化学产物身份知识，不是固体金属的虚构水溶液解离。

M12 增加相同类型边界的上下文单跳关系 `metal.displaces_cation`。置换能力连接两个规范身份，属于 Relation，不是分类 Facet 或某反应的布尔字段。水溶液适用性用 `context: {medium: aqueous}` 表达，不能编码进关系键。M20 允许同一断言携带有证据的 `truth: false`；缺失仍为 UNKNOWN，不能据此认定不可置换。

基数约束由各受控关系家族规定，约束正向目标。`metal.product_cation` 为 `one_target_per_context`，`metal.displaces_cation` 为 `many_targets_per_context`，允许一种金属在相同上下文置换不同阳离子。显式否定不占正向基数；完全重复和同一元组真值矛盾均无效。此契约不引入通用图、反向遍历、多跳查询或数值活动性排序。

## 7. 反应

`Reaction` 是一次转化的稳定知识对象。分类有多个维度：氧化还原、酸碱、沉淀、放气、燃烧、取代、加成、酯化等可重叠。

反应形式是表示/投影；化学上不同的半反应仍各自是 Reaction。

## 8. 实验与观察

规范步骤/设计需要持久引用时，可复用 `Experiment` 可以具有身份。个别观察通常是附着于 Reaction/MaterialSystem/Experiment 的上下文事实。

## 9. 必须保持的示例

- Fe 元素概念不等于 Fe(s) 物质。
- S 元素概念不等于硫单质 Substance；`S: 1` 的配平基准不表示宏观硫由单原子构成。
- NaCl 晶体是具有离子结构、Na+/Cl- 组成物种的物质，无需 NaCl 分子。
- H2SO4 分子 Species、硫酸 Substance 和硫酸溶液/MaterialSystem 不同。
- SO2 氧化/还原行为由上下文或反应限定。
- 乙醇关联分子结构和羟基基元；醇是 Facet/分类。
