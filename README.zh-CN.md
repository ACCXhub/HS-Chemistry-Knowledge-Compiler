# 高中化学知识编译器

[English](README.md)

> 中文版对应英文文档；历史章节保留其当时范围与版本。后续契约变更须同步维护两种语言。

基于经过整理审核的规范数据和有界声明式 Rule，生成高中化学方程式并进行确定性反应推断。本体、Entity/Relation 事实、证据、迁移和 TeachingView 均服务于这一方程生成流程。

## 当前可执行范围

F1/F2/F3 基础与已完成的 M4–M25 工作见[路线图](docs/ROADMAP.zh-CN.md)。当前包含 68 条规范 Reaction、14 条有效 Rule、117 个推断测试案例和 38 个水溶液物种组成配置。规范反应覆盖与可执行推断覆盖不同：固体 CaCO3 + HCl 已有规范 Reaction，但可溶性碳酸盐 Rule 不生成该反应。

支持有界的中和、沉淀、酸驱动放气、铵盐/碱、金属/酸和金属/水放氢、水溶液金属盐置换，以及限定身份的热分解/水蒸气试点。缺失知识保持 UNKNOWN；显式 FALSE 只否定具体路径，不声明全局负面 Reaction。

```text
规范 YAML → schema/引用/化学校验 → RulePlan 匹配
→ 规范产物解析 → 精确配平 → 原子/电荷校验
→ 规范 Reaction 比较 → ReactionCandidate + 证明轨迹
```

## 运行

需要 Python 3.11+。执行 `python -m pip install -e .` 安装；开发验证需另外安装 `pytest`。

```powershell
python -m compiler.cli validate
python -m compiler.cli compile --output build/compile --source-revision WORKTREE
python -m compiler.cli audit --output build/audit --source-revision WORKTREE
python -m pytest -q
```

`audit` 运行仓库内的测试案例；`compiler.engine.infer_case` 是有界 Python 推断入口。构建输出是生成产物，不可作为可编辑的化学事实。记录已验证构建时，用精确 Git SHA 替代 WORKTREE。

## 规范责任边界

| 事项 | 负责位置 |
| --- | --- |
| 化学身份、组成、上下文事实、单跳 Relation | `knowledge/domain/`、`compiler/source.py` |
| 整理审核的化学转化及从属 ReactionForm | `knowledge/domain/` 中的 Reaction、`compiler/reaction_forms.py` |
| 适用性与规范产物构造 | `knowledge/rules/`、`compiler/rules.py`、`compiler/products.py` |
| 精确配平与守恒 | `compiler/balance.py` |
| 运行时推断与证明轨迹 | `compiler/engine.py` |
| 源数据与产物契约 | `schemas/`、`docs/contracts/` |
| 教学投影 | `knowledge/teaching/`，不参与推断 |
| 离线旧数据对照 | `migration/`，不进入运行时 |

编译器不猜测化学式或化合价，不虚构产物身份，也不把推断候选提升为规范 Reaction。化学式/名称仅用于查找，不拥有身份。更广泛的平衡、氧化还原、活动性顺序推理、UI 和自动批量迁移均不在已实现范围内。

兼容坐标保持为：源 schema `3.7.0`、Rule DSL `1.4.0`、RulePlan `1.4.0`、产物格式 `1.5.0`；编译器补丁版本独立。格式检查仍接受历史产物 `1.0.0`–`1.5.0`。

参见[架构](docs/ARCHITECTURE.zh-CN.md)、[推断语义](docs/inference/INFERENCE.zh-CN.md)、[覆盖审计](docs/COVERAGE_AUDIT.zh-CN.md)、[路线图](docs/ROADMAP.zh-CN.md)和[chem-wiki 接入建议](docs/contracts/CHEM_WIKI_INTEGRATION.md)。

## 中文文档导航

| 文档 | 内容 |
| --- | --- |
| [架构](docs/ARCHITECTURE.zh-CN.md) | docs/ARCHITECTURE.md |
| [覆盖与迁移审计 — M25 之后](docs/COVERAGE_AUDIT.zh-CN.md) | docs/COVERAGE_AUDIT.md |
| [架构决策记录](docs/DECISIONS.zh-CN.md) | docs/DECISIONS.md |
| [路线图](docs/ROADMAP.zh-CN.md) | docs/ROADMAP.md |
| [F3B 水溶液化学试点审计](docs/audits/F3B_AQUEOUS_PILOT.zh-CN.md) | docs/audits/F3B_AQUEOUS_PILOT.md |
| [规范数据模型](docs/contracts/DATA_MODEL.zh-CN.md) | docs/contracts/DATA_MODEL.md |
| [身份与溯源](docs/contracts/IDENTITY_AND_PROVENANCE.zh-CN.md) | docs/contracts/IDENTITY_AND_PROVENANCE.md |
| [Schema 策略](docs/contracts/SCHEMA_STRATEGY.zh-CN.md) | docs/contracts/SCHEMA_STRATEGY.md |
| [规范领域本体](docs/domain/ONTOLOGY.zh-CN.md) | docs/domain/ONTOLOGY.md |
| [知识编译器架构](docs/inference/COMPILER.zh-CN.md) | docs/inference/COMPILER.md |
| [确定性反应推断语义](docs/inference/INFERENCE.zh-CN.md) | docs/inference/INFERENCE.md |
| [声明式反应规则 DSL](docs/inference/RULE_DSL.zh-CN.md) | docs/inference/RULE_DSL.md |
| [规范教学视图模型](docs/pedagogy/PEDAGOGY.zh-CN.md) | docs/pedagogy/PEDAGOGY.md |
| [chem-wiki 接入建议](docs/contracts/CHEM_WIKI_INTEGRATION.md) | 原文已为中文 |
