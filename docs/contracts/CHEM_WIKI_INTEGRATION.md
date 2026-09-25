# chem-wiki 联立建议

状态：2026-09-25 基于两仓库源码的接入建议，尚未实现适配器、API 或数据库迁移；未核查运行中数据库的数据量。

## 当前可复用的边界

- chem-wiki 当前 HEAD 为 `7776bc6c2b9f70ebd2c350085e05175287d85da4`，有未提交的前端改动，本轮未修改。
- `backend/src/chem_wiki/modules/knowledge_catalog/release.py` 锁定旧仓库的 `consolidated-1.1.0` 与 `a631115...`，校验固定 JSONL 文件、计数和哈希；不能只改目录指向本编译器。
- `knowledge_catalog` 已有 PostgreSQL / SQLAlchemy 导入、stable application UUID、来源 crosswalk、Reaction catalog、物态和热化学表。`reaction_core` 负责应用 Reaction 聚合和配平；`reaction_builder` 当前按物质 UUID 查找、排序已知 Reaction，尚不执行本编译器规则。
- 编译器当前有 68 条 canonical Reaction、14 条 Rule；旧应用 release 声明 183 条 Reaction、309 条 species。两个数字的口径与覆盖不同，不能整库替换，也不能丢弃旧库的结构和热化学内容。

## 推荐接法：先接推断，再扩展数据发布

```text
EquationDraft（application UUID + 显式物态/条件）
  → reaction_builder 的推断适配器
  → 已审核 identity crosswalk → compiler canonical ID
  → 固定版本 compiler + 固定只读知识快照
  → ReactionCandidate / UNKNOWN / diagnostics + proof trace
  → 映回 application UUID，返回应用 DTO
```

保持当前已知 Reaction 查询接口；另设计显式的推断请求，例如拟议的 `POST /v1/reaction-builder/infer`。现有 `/candidates` 只接受两侧 UUID 列表，无法表达相态或 warmed/heated 条件，不应暗中把它当完整推断输入。

第一步可把编译器作为 Python 依赖接入，在应用启动时对固定 source SHA 的只读快照执行一次 `load_knowledge` / `compile_rules`，随后复用 `infer_case`。固定代码版本、source digest 与版本坐标；不要逐请求读 YAML、拉 Git 或查库拼装规则。chem-wiki 要求 Python 3.13，实际接入时需在其锁定环境验证依赖和全部公共调用。

当前 `compile` 没有导出完整 Entity、canonical Reaction、Evidence/Source 清单，也没有完整的产物加载器；`audit` 的 fixture 候选不是反应数据库。后续正式发布只需补齐一个有 manifest、文件哈希、引用闭包的应用数据包，再为 `knowledge_catalog` 增加专用 release adapter；无需另建通用知识平台。

## 数据字典必须明确的内容

| 数据 | 最小契约 |
|---|---|
| Release | provider、不可变 release ID、source SHA/digest、compiler 版本、四项兼容坐标、文件哈希 |
| Entity | canonical ID、kind、名称/别名、元素组成、净电荷；公式只作检索信号 |
| 身份映射 | provider + canonical ID → 现有 application UUID，附映射依据与审核状态；支持反向查询 |
| Reaction | canonical ID、方向、参与者 ID/role/phase、有理数系数、条件及 evidence refs |
| 推断知识 | 带上下文的 properties、Relation truth、speciation 与完整 Rule；保留 unknown/absent，不补成 false |
| ReactionForm / Candidate | Form 从属于 Reaction；Candidate 保留 rule ID/version、candidate key、完整 trace 和来源版本，不自动 published |

Species(ion) 可映射到既有 IonId，Substance 到 SubstanceId；Element 复用 element_data。分子 Species、原子 Species 和 MaterialSystem 不能强制塞进只接收 ion/substance 的 Catalog。现有迁移报告只能提供映射线索，不能代替完整、已审核的应用 identity crosswalk；复用已有 UUID，不按新 external ID 给旧物质再造 UUID。

相态须有显式映射，尤其 `aqueous` 与离子 `dissolved`；unknown 保持缺失语义，不默认 aqueous。系数保留 numerator/denominator，物化时先对整条方程作精确整数归一化，再检查 `Numeric(20,8)` 容量，不能经 float 舍入。M05 当前同侧同 identity 的唯一约束不含 phase；出现同一物质同侧多物态时先保留 catalog-only，不合并物态。当前 schema 也不能用一个 molecular Reaction 的物化流程把不同 ReactionForm 变成新的化学变换身份。

## PostgreSQL 如何建

优先沿用 chem-wiki `compose.yaml` 中的 PostgreSQL 17 与已有 Alembic 链，维护应用读模型；Git 中的审核数据仍是编译器化学事实来源。

| 责任 | 现有表 / 建议增量 |
|---|---|
| 发布校验 | 复用 `catalog_release`、`catalog_release_artifact`，为多 provider 定义无碰撞的 release key |
| 物质与检索 | 复用 `catalog_species`、教学、物态及来源投影，不复制一套 substance 表 |
| 已审核身份映射 | 在 Catalog owner 下增加窄 crosswalk，主键 `(provider, canonical_id)`，映射到既有 typed application UUID，并索引反向映射 |
| 已知反应 | 复用 `catalog_reaction`、`catalog_reaction_participant`；满足 M05 约束和审核状态后才物化到 `reaction*` 表 |
| 规则执行 | 首期从固定快照加载到内存，不把 RulePlan 拆成大量 SQL 表或在 SQL 中推断 |
| 推断结果 | 首期按请求返回；有实际缓存需求时再增加 derived 结果缓存，键含 source digest、compiler 版本和规范化输入 |

常查字段用普通列、外键及 B-tree 索引；变化较大的条件、原始 payload、证据及 proof trace 可用 JSONB。只为实际查询添加 JSONB 索引。未知事实优先用缺行/明确状态表达，FALSE 是已审核的否定事实，二者不能同值。

现有 Catalog 保留 release 历史，但 species 等行并不是完整的按 release 分版本快照：物质导入主要是 insert-if-missing。因此多版本切换/回滚不能仅增加一个 active_release 字段。先明确哪个 provider 拥有哪些字段，并对一次窄接入设计事务内的变更集和回滚；确需多快照并存时再引入按 release 的投影关联，避免一次导入混合两个版本。

## 最小落地顺序

1. 保持现有数据库，用少量已有物质建立经审核的双向 ID 映射。
2. 接入推断适配器，验证中和、沉淀、Zn/HCl 三条正例，以及未知事实、错误物态、Cu/Zn 否定与缺少加热条件；前端只展示 DTO。
3. 验证同一 release 重复导入不改 UUID、不增重复记录，所有参与者解析成功，错误哈希/版本拒绝，Candidate 不变成 published Reaction。
4. 再按需求补齐正式数据发布和 Catalog 导入。更新 chem-wiki 当前冻结的 upstream/owner 契约之后，才逐步迁移受支持的数据；本轮尚未执行这些步骤。
