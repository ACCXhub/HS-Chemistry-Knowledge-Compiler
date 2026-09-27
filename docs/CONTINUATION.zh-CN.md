# 持续补齐任务的续作点

[English](CONTINUATION.md)

## 长期目标（未完成）

覆盖大陆高中必修＋选择性必修的元素、物质、方程、通用规则和特例；支持共享身份的三类独立数据包，后续加入有证据的案例迁移与预测解释。预测不冒充规范事实，UNKNOWN 不等于不可能。安全提交推送 main 已授权；不启动子代理，不重复 M0–M25 审计，不 reset/stash/rebase。

## 最新完成批次：铁的固体氧化物/氢氧化物与酸

已发布基线 `3ab77d93b6f93b8744e10a7b22eb62fa015fa0ff`（铁氯化物价态互转）。当前新增 FeO、Fe2O3、Fe(NO3)3 三个身份、八条 Reaction、四条声明式 Rule、八个正例和两个 UNKNOWN 案例。FeO/Fe(OH)2 的普通溶酸路径必须有非氧化性酸证据；与 HNO3 不冒充普通 Fe(II) 盐中和。Fe(III) 氧化物/氢氧化物支持 HCl/HNO3；硝酸铁与 NaOH/KOH 复用 M15。未改运行时、schema、版本坐标或迁移机制。

当前297记录、117 Entity、102 Reaction、27 Rule、159案例、43解离配置；103 inferred、43 indeterminate、12 no_match、1 blocked。全部102规范反应均有正例；去掉全部 Reaction 后仍能独立生成103个正例。compiler 0.5.0。模块主记录/依赖：elements 18/6、substances 99/62、equations 129/162。

## 验证与保存

- validate 和35项针对性测试通过，覆盖价态、净离子式、原子/电荷、物态、上下文、正面非氧化性证据、输入/规则顺序和无存储 Reaction 的生成。
- 完整508项测试全部通过（443.48秒），日志 `build/iron-solid-acid-pytest.txt`；session `69693` 已结束，无需重跑。InferenceSession 数据包 API 的八个正例和两个 UNKNOWN 边界均通过。
- compile/audit/bundle/modules 在 PYTHONHASHSEED 3/941 下逐字节相同，证据 `build/iron-solid-acid-verification/`。M25两次复现相同：21映射、122不支持、9拒绝。历史报告不改写。
- 本批安全提交推送 main，正式 `build/application-bundle`、`build/data-modules` 按最终 SHA 重导出。以两份 manifest.source_revision 对照当前 HEAD 核验发布身份。

上一批完整482项通过，日志 `build/iron-interconversion-pytest.txt`；该结果不能代替当前批次验证。更早铜氧化物批次已在 `c751cf4` 保存。已完成审计和测试不需重跑。

## 精确下一步

1. `git status --short --branch`、`git diff --stat`、`git rev-parse HEAD`；读本文件，查询真实额度，保留已有改动。
2. 下一批优先[逐式队列](CURRICULUM_COVERAGE.zh-CN.md)中的 Fe3O4/HCl 混合价特例、Fe(OH)2/O2/H2O 独立氧化步骤；避免猜单一价态或把后续氧化混进沉淀方程。
3. 继续冻结有限教材逐式目录并补 Al、非金属、有机、电化学等缺口。主题矩阵及当前102方程不证明教材全覆盖。浓度、过量、催化、可逆和电极条件需先有最小必要语义。
4. 自动案例推广/模型预测尚未实现。已有规则可推知识充分但未存储的方程；标签与守恒不能单独证明反应能发生。

## 网站交付和自动续作

完整 bundle 为 InferenceSession 输入；三个独立模块用于导入数据库，不能当运行时插件。见[模块契约](contracts/DATA_PACKAGES.zh-CN.md)、[Python API](contracts/APPLICATION_API.zh-CN.md)、[chem-wiki接入](contracts/CHEM_WIKI_INTEGRATION.md)。实际 HTTP 适配器、数据库导入尚未实施。README 不再重复计数，当前覆盖数统一维护于课程表。

heartbeat `automation` 保持 ACTIVE，中文乱码已修复；每5小时10分钟触发，为五小时额度窗口留出10分钟恢复余量，逐次查询真实额度和重置时间。额度使用约80%开始收尾，不等耗尽才保存；未恢复则安静等待，不暂停/删除任务，不把长期目标标记完成。收尾时五小时额度已使用73%，本批之后不开新规则工作流；窗口重置时间为北京时间2026-09-27 14:51:13。
