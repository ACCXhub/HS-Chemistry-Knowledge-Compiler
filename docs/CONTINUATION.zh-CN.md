# 持续补齐任务的续作点

[English](CONTINUATION.md)

## 长期目标（未完成）

覆盖大陆高中必修＋选择性必修的元素、物质、方程、通用规则与特例；独立发布共享身份的数据模块，后续支持有证据的案例迁移和预测解释。预测不冒充规范事实，UNKNOWN 不等于不可能。安全提交推送 main 已授权；不启动子代理，不重复 M0–M25 审计，不 reset/stash/rebase。

## 最新完成批次：M16–M18 介质边界

基线 `e7f8a71d07e82bf61b835fe8b22f1d64332c0d14`。三条规则升级 1.1.0，同时要求 `medium: non_aqueous` 和 `temperature_regime: heated`；规范 Reaction 条件、fixtures、相关测试及中英文接口/路线图已同步。缺 medium 为 indeterminate/UNKNOWN，明确 aqueous 为 no_match，均不生成候选。编译器与 schema 版本不变，没有新增运行分支。

验证：28 项热反应针对性测试、21 项 application bundle/M25 测试全部通过；validate 通过。按本轮仅针对实际改动验证的要求，未重跑全套。种子3/941下 compile/audit/bundle/modules 字节一致，108条规范反应仍均有正例；统计保持109 inferred、45 indeterminate、12 no_match、1 blocked。日志与证据在 `build/thermal-medium-*`。

M25 两次复现相同：19 mapped /124 skipped /9 rejected。相比上一批，只有 `reaction:caco3-thermal` 和 `reaction:nahco3-thermal` 因旧数据缺明确介质转为 context_gap；未放宽迁移或重写历史报告。后续若恢复这两条映射，须补有来源的介质声明，不从固体相态猜环境。

## 上一批：混合价铁氧化物、氧化及热反应

基线 `89cb84993b7072eabe1d837f4a72beab11541fe8`。新增 Fe3O4、O2 身份及六条精确规则/方程：Fe3O4/HCl、Fe(OH)2/O2/H2O、Fe/蒸汽、Fe/O2、Fe/Cl2、Fe(OH)3 热分解。Fe3O4 保留 Fe(II):Fe(III)=1:2，不能选单一价态。氢氧化物氧化必须显式输入氧气和水，不改写之前的沉淀反应。

初次测试暴露缺介质的阻断项仍为 UNKNOWN，不能当非水相。最小修正为 source schema 3.8.0 / compiler 0.6.0，增加 `medium: non_aqueous`，新增四条热反应同时要求该介质与 heated。non_aqueous 表示不是水溶液，不排除水蒸气；省略介质不推定默认值。Rule DSL/plan、artifact、bundle/module 格式不变。版本坐标测试同步；公共 API 文档纠正原错误的“仅1–2输入”说法，已有匹配器支持三输入。

当前317记录、119 Entity、108 Reaction、33 Rule、167案例、43解离配置；109 inferred、45 indeterminate、12 no_match、1 blocked。全部108规范反应均有正例；移除 Reaction 后仍生成109正例。模块主记录/依赖：elements 18/6、substances 101/65、equations 141/170。

## 验证与保存状态

- validate 与41项针对性通过，包括混合价净离子式、精确系数/物态、缺热/缺介质/水溶液边界、液态水不能套蒸汽、未显式输入氧气不擅自氧化、三输入公共 API。
- 全套540项全部通过（463.78秒），日志 `build/iron-thermal-pytest.txt`；session `34417` 已结束，无需重跑。
- compile/audit/bundle/modules 在哈希种子3/941下字节相同；M25两次复现为21映射、122不支持、9拒绝。证据目录 `build/iron-thermal-verification/`。
- 0.6.0 wheel 标准隔离构建和安装验证通过（session `46005` 已结束）；日志 `build/iron-thermal-wheel.txt`。隔离Python仅通过安装包+bundle验证非水相铁/蒸汽可推导，缺介质为UNKNOWN。未修改全局环境。
- 正式产物为 `build/application-bundle`、`build/data-modules`，以 manifest.source_revision 与最终 HEAD 一致为发布验收。旧0.5.0包不能直接用于新严格加载器，须重新导出，不能改 manifest 哈希伪装升级。

来源：OpenStax 19.1 的铁/氯气、Fe3O4及氧化物/氢氧化物；Chemguide 铁章节的 Fe(OH)2 被空气氧化；NCERT 3.2.2（PDF第7页）明确铁/蒸汽方程，仅用作事实来源，不更改大陆课程范围。原始材料保存在忽略的 `build/curriculum-review/`。

## 精确下一步

1. `git status --short --branch`、`git diff --stat`、`git rev-parse HEAD`，读本文并检查真实额度；保留未提交工作，当前批次无遗留测试进程。
2. M16–M18 介质修正已完成，不重复审计；直接从下一项逐式队列继续。
3. 然后补 Fe2O3/CO、铝热反应等[逐式队列](CURRICULUM_COVERAGE.zh-CN.md)，以及 Al、非金属、有机、电化学。当前数量不是教材全覆盖证明；仍需有限教材逐式目录。
4. 浓度、过量、催化、可逆、电极条件须有必要语义。案例/模型自动推广还未实现，不凭标签或守恒猜反应。

## 网站与自动续作

[模块契约](contracts/DATA_PACKAGES.zh-CN.md)、[Python API](contracts/APPLICATION_API.zh-CN.md)、[chem-wiki接入](contracts/CHEM_WIKI_INTEGRATION.md)已同步。完整bundle用于 InferenceSession，独立模块用于数据库导入；HTTP适配和实际数据库导入未实施。

自动任务 `automation` 保持 ACTIVE，每5小时10分钟触发；每次先查真实额度，约80%起只收尾。额度未恢复则安静等待，不暂停/删除自动任务，不将长期目标标记完成。本轮开始额度已恢复，五小时用量5%；重置时间为北京时间2026-09-28 01:20:55，每次以实时查询为准。
