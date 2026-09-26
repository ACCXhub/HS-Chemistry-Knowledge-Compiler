# 元素、物质与方程三个数据包

[English](DATA_PACKAGES.md)

compiler 0.5.0 已实现 `export-modules`。三个模块使用同一套源记录格式、规范ID、证据和精确系数，不创建平行知识库。

```powershell
python -m compiler.cli export-modules --output build/data-modules --source-revision WORKTREE
```

正式发布应使用干净且已验证 checkout 的完整提交SHA。生成 `manifest.json`、`knowledge-record.schema.json` 和三个JSON文件；完整推断部署继续使用 `export` 的 bundle 与 `InferenceSession`。模块数据包是数据库导入/查询字典，不是可以替代完整知识快照的运行时插件。

## 模块与格式

| 文件 | 主记录（root_ids） | 自动带齐的依赖 |
| --- | --- | --- |
| elements.json | Entity.kind=element：符号、原子序数及已审定元素属性 | 必需的Evidence/Source |
| substances.json | 所有非Element的Entity：Substance、Species（包括离子）、MaterialSystem | 元素、被引用的物种/物质、Evidence/Source |
| equations.json | 全部Reaction与Rule；ReactionForms保留在所属Reaction内 | 参与者、规则产物/关系目标、元素、Evidence/Source |

“物质包”包括离子等相关实体；MaterialSystem仍不能当作可直接配平的纯物质。每包都含完整引用闭包，因此可单独分发；共享依赖保留相同ID与相同内容，不产生新身份。TeachingView不属于这三个主模块，完整bundle仍保留它。

每个包的固定顶层字段：

| 字段 | 含义 |
| --- | --- |
| module_format_version | 当前1.0.0，与源schema/DSL及完整bundle版本独立 |
| module_id | elements、substances或equations |
| source_schema_version | 当前3.7.0，records使用随包的规范记录schema |
| source_semantic_digest | 完整审核知识快照的摘要；三个包必须相同才属于同一快照 |
| record_digest | 本包全部records的规范JSON摘要 |
| root_ids | 本模块直接负责的主记录ID，排序、无重复 |
| dependency_ids | 引用依赖ID，排序，与root_ids不相交 |
| records | 主记录与依赖的并集，按record_type/id排序；不丢属性、Relation或证据 |

manifest包含源码提交、compiler版本、四项兼容坐标、文件SHA-256、每包主记录/依赖/总数和release_id。`hschem_modules_`后接除release_id字段以外manifest的规范JSON SHA-256。记录摘要不含换行，文件哈希包括末尾LF。导出前对每包复用源schema、唯一性、引用与化学守恒校验，并验证其Rule可编译。

## 网站导入顺序与数据库责任

1. 固定可信release，先检查manifest文件哈希和版本，再验证record_digest与引用闭包。不要把来自不同source_semantic_digest的包混成一个快照。
2. 按规范ID合并records。共享依赖必须内容一致；内容冲突终止导入。root_ids用于决定模块归属，不能把依赖重复计入覆盖数。
3. 在一个事务中导入release、规范记录和已审核的应用ID映射；同一release重复导入不增加实体或反应。未知/缺失属性保持原值状态，不补FALSE。
4. 组成、净电荷和参与者ID用于身份审核；名称、中文别名、公式可建立检索索引，但不能凭公式合并不同结构或物态身份。保留Source/Evidence供前端展开解释。
5. 有理系数以分子/分母整数保存；物化为现有反应表前做整条方程的精确整数归一化。Rule保留声明式JSON/固定内存计划，不拆成SQL推理系统。

接入chem-wiki时沿用 `knowledge_catalog` 的release、crosswalk和读模型；`reaction_core`拥有已物化应用Reaction。已有schema尚不支持的记录先保留catalog-only，不创建伪UUID或丢弃数据。详见[数据库接入说明](CHEM_WIKI_INTEGRATION.md)。

从零建站时，最小导入存储可采用release表、以`(release_id, canonical_id)`为键的规范record表（kind普通列，payload JSONB），以及规范ID到应用UUID的审核映射表。元素/物质/方程分别通过kind和root_ids投影查询；热点字段后续按实际查询建立普通列/索引。预测候选另存状态、依据release、模型/Rule版本和解释，绝不覆盖审核记录。

## 后续模型的数据边界

Reaction样本、Rule适用条件、实体属性/关系和显式否定构成可复用输入。未来类比/模型输出应保留候选身份、支持样例、反例、缺失条件、守恒检查及审核状态；样本少或知识缺失返回未知。元素/物质基础数据缺失时先补规范身份和组成，不能让模型凭名称虚构可配平实体。当前模块导出不等于已经实现自动学习或全课程覆盖。
