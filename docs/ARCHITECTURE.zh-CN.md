# 架构

[English](ARCHITECTURE.md)

> 中文版对应英文文档；历史章节保留其当时范围与版本。后续契约变更须同步维护两种语言。

状态：**F1 设计基线，包含截至 M25 已实现的边界**

## 1. 目的

本项目生成高中化学方程式，并执行有界、确定性的反应推断。源数据到产物的模型服务于此目标：保留稳定化学身份、显式语义、上下文、证据和确定性推导，不让课程组织或运行时布局成为领域模型。

本仓库替代 `chem-knowledge-data`；旧数据可以通过适配器迁移，但不约束规范模型。

## 2. 分层边界

```text
具有身份的记录
+ 断言 / 分类维度 / 关系
+ 规范反应
+ 教学视图
+ 证据
+ 声明式规则
        │
        ▼
规范源数据契约
        │
        ▼
编译器
解析 → schema 校验 → 语义校验 → 解析引用 → 规范化
→ 规则分析 → 推断 → 构造产物 → 解析身份
→ 配平 → 原子/电荷校验 → 规范反应比较 → 证明轨迹
        │
        ▼
确定性的外部产物 + 内部运行计划
```

外部生成产物的 schema 由数据契约负责。内部 `RulePlan`、索引、缓存、算子降级编译和运行时布局由编译器负责。

## 3. 身份模型

### 3.1 具有化学身份的记录

`Entity` 是稳定化学/材料身份的封装。规范 `entity_kind` 值为：

```text
element
species
substance
material_system
```

`Species` 使用浅层 `species_kind`，如 `atom`、`ion`、`molecule`，或课程确有需要的其他微观种类。因此 `Ion` 不与 `Species` 并列为身份类型。

`Substance` 表示宏观纯物质身份，可承载宏观性质、制备、用途和带物态限定的观察。

`MaterialSystem` 表示组成或实验状态有意义的复合样品/体系。`Solution` 和 `Mixture` 是 `material_system_kind` 的值。浓度变化不产生新 Species，通常也不产生新身份；只有把体系本身整理为可复用指称对象时例外。

### 3.2 其他具有身份的记录

F1 也允许独立生命周期需要持久引用的对象具有稳定 ID，包括：

- `Structure`；
- `Reaction`；
- 整理为可复用步骤/设计的 `Experiment`；
- `TeachingView`；
- `Rule`；
- `Source` 和 `Evidence`；
- 因溯源或修订生命周期需要而独立整理的断言/关系。

不能仅因某个值可以单独规范化成表，就要求它具有持久 ID。

## 4. 结构边界

`Structure` 是稳定结构模型的规范主体，不等同于 SMILES 字符串、Lewis 图、图片或文件资源。

结构可包含节点/组成单元、嵌入的键组件、连接与几何事实、结构基元/官能团链接，以及 SMILES、InChI、Lewis、晶体描述或资源引用等表示。

`Bond` 默认是嵌入组件，使用结构内局部键。F1 不因图规范化而创建顶层键 UUID。只有键自身的证据、修订或外部持久引用确需独立生命周期时，后续才可引入顶层身份。

官能团是与结构/Species 关联的可复用基元或 Facet 词汇概念，不是 Substance。

## 5. 源数据规范化原则

规范源数据应便于人工审核、差异比较、schema 校验和实际编辑。

以下对象默认作为**嵌入值对象**：

| 对象 | F1 源数据角色 |
| --- | --- |
| Composition | 在所属 Species/Substance/Structure 上嵌入精确组成 |
| Context | 在断言/反应/形式上嵌入结构化限定集合；维度使用受控词汇 |
| ReactionParticipant | `Reaction` / `ReactionForm` 内的参与者值对象 |
| Condition | 反应/规则范围内的条件值对象 |
| TeachingViewPath | `TeachingView` 内的节点/路径；路径键只在视图内定位 |
| Bond | 使用结构局部键的嵌入组件 |

`FacetAssertion` 只有在经编写和证据支持、且需独立溯源/修订生命周期时，才成为规范断言。编译器推导的 Facet 成员关系属于生成产物，不是源记录。

该原则避免源数据充斥 UUID，同时保留有依据的持久引用。

## 6. 事实语义

断言区分 `intrinsic`（内禀）、`contextual`（上下文限定）和 `derived`（推导）。值状态区分：没有断言、显式 `unknown`、`not_applicable`、已知值（包括已知布尔 `false`）。

缺失数据不能转为 false；依赖上下文的断言不能压平成无条件属性。

## 7. 反应模型

### 7.1 规范 Reaction

`Reaction` 是在声明的语义边界下经过整理审核的一次化学转化，拥有稳定反应身份、规范参与者、条件/约束、分类、证据和相关形式。

反应身份不依赖方程式文本、参与者顺序、系数倍乘或教学位置。

### 7.2 ReactionForm / ReactionRepresentation

`ReactionForm` 是同一反应转化的嵌入或子级表示/投影，可表达分子方程式、完全离子方程式、净离子方程式、热化学方程式，以及保持同一底层转化的其他记法。

形式可以采用与规范反应不同的指称层次；计算得出的形式必须带有推导/投影依据。

方程式倍乘不产生新反应。反应焓等量应相对于选定的化学计量反应进度/形式倍数解释。

### 7.3 相互关联但不同的反应

化学上不同的转化仍是不同 `Reaction`，即使方程式相关。电化学的氧化、还原半反应分别建模为 Reaction，通过 `component_of` / `composes` 等有类型的组合关系关联总电池反应。

## 8. 反应指称层次

参与者可以引用微观离子/分子转化的 `Species`、宏观纯物质的 `Substance`，或组成/实验体系身份有意义时的 `MaterialSystem`。参与者应显式声明指称层次，或由目标类型消除歧义。

分子/离子形式可依据已声明的物种组成/解离假设跨层投影。不能为方便书写方程式而把 `NaCl(s)` 建模为虚构 NaCl 分子。

## 9. ReactionCandidate 生命周期

纯编译不得创建基于时间的 ID。

生成候选的确定性 `candidate_key` 来自规范化语义内容、相关规则身份/版本和声明的推断输入。相同输入重复编译必须得到相同键。

候选进入持久人工审核流程时，可为审核对象创建 `rcand_*` ID，但需保留不可变的 `candidate_key`。提升到规范知识必须创建或修改 `rxn_*` 记录，不能把生成候选本身改成规范反应。

## 10. Rule 身份

声明式 `Rule` 定义是稳定 `rule_*` 身份、语义版本、证据和消解关系的唯一规范主体。

不另设规范 `RuleReference` 记录；其他记录使用 `rule_id` 及可选所需版本约束等标量/引用值。

## 11. 教学视图

教学视图投影规范化学知识，可按 D01–D11 或后续课程分组、排序、注释、简化和交叉链接对象。

`TeachingView` 有稳定身份，路径节点嵌入且只在视图内有效。路径变化不改变化学身份。

## 12. 源数据与生成物边界

可编辑规范源数据位于：

```text
knowledge/domain/**
knowledge/teaching/**
knowledge/rules/**
schemas/**
```

生成产物可比源数据更规范化或更非规范化。运行时紧凑 ID、数据库行、图边、索引、缓存和编译规则计划都是可丢弃、可重建的表示。

## 13. 规范责任映射

| 事项 | 负责文档 |
| --- | --- |
| 跨工作流架构 | `docs/ARCHITECTURE.md`、`docs/DECISIONS.md` |
| 本体含义 | `docs/domain/ONTOLOGY.md` |
| 教学模型 | `docs/pedagogy/PEDAGOGY.md` |
| 源数据/外部产物契约 | `docs/contracts/**` |
| 推断语义/运行计划 | `docs/inference/**` |

## 14. 代表性一致性案例

### Fe 元素与 Fe(s)

`Element(Fe, Z=26)` 是元素概念，宏观铁是 `Substance`。铁原子、离子和宏观铁不能只因共用 Fe 符号就共用身份。

### NaCl 晶体

氯化钠晶体是关联离子 `Structure` 的 `Substance`，结构包含 Na+、Cl- 组成单元。`NaCl` 是化学式单位表示，无需 NaCl 分子 Entity。

### H2SO4

`H2SO4` 分子 Species、硫酸 Substance 和硫酸溶液 MaterialSystem 不同。强酸/电解质行为受水溶液上下文限定。

### SO2

SO2 身份稳定；氧化剂/还原剂行为由反应/上下文限定的角色断言表达。

### 乙醇

乙醇 Species/Substance 关联稳定的分子 Structure；羟基是结构基元/Facet，醇分类可由断言或确定性推导得到。

### NaCl + AgNO3

宏观水溶液沉淀 Reaction 可有分子、完全离子和净离子 ReactionForm。在投影假设明确时，Ag+ + Cl- → AgCl(s) 是同一沉淀转化的微观投影。

### HCl + NaOH

水溶液中和 Reaction 可提供分子与离子形式；H+ + OH- → H2O 是声明的强电解质水溶液模型下的净离子形式。

### 铜锌原电池

电池总转化是一个 Reaction。Zn 氧化和 Cu2+ 还原分别是半反应 Reaction，关联总反应及电极/材料体系上下文。
