# 持续补齐任务的续作点

[English](CONTINUATION.md)

## 长期目标（未完成）

覆盖中国大陆高中必修＋选择性必修的元素、物质、方程式、规则与特例；元素、物质、方程数据分别发布并保持共享身份。后续支持有证据的案例迁移和预测解释；预测不得冒充规范事实，UNKNOWN 不等于不可能。已授权安全提交推送 main；不启动子代理，不重复 M0–M25 审计，不 reset/stash/rebase。

## 当前成果：2026-09-27 铜氧化物与硝酸盐批次

- 在 `0db354e2aae013f0b8ca36e6be0028057b8f01b9` 亚铁批次上，新增 CuO、Ca(NO3)2、Cu(NO3)2 三个身份，八条 Reaction、一条 CuO/强酸 Rule、八个正例。其余七条路径复用原有规则；硝酸盐作旁观离子不赋予硝酸非氧化性。
- 272记录、113 Entity、91 Reaction、20 Rule、146案例、42解离配置。92 inferred 覆盖全部91规范方程和1条未存储方程；41 indeterminate、12 no_match、1 blocked。
- compiler 0.5.0；完整 application-bundle 是 InferenceSession 输入。独立模块：elements 18主记录/6依赖，substances 95/59，equations 111/155。接入见[数据模块契约](contracts/DATA_PACKAGES.zh-CN.md)、[Python API](contracts/APPLICATION_API.zh-CN.md)、[chem-wiki数据库说明](contracts/CHEM_WIKI_INTEGRATION.md)。HTTP适配器和实际数据库导入尚未实现。
- 无运行时/schema改动。修正 M12/M13 测试对全部置换关系的过度冻结，只检查各自负责的目标及证据。同步中英文数量、路线图和历史审计定位。

## 验证与保存

validate、18项铜批次/独立生成测试通过；移除全部 Reaction 后仍可生成全部92正例。完整466项已执行：464通过，两处旧关系列表断言失败，随后已修正；随后受影响的 M12/M13 两文件27项全部通过；此后未修改运行时或规则。完整日志 `build/current-final-pytest.txt`，不需要重跑全套。

PYTHONHASHSEED 3/941 下 compile、audit、bundle、modules 字节一致，证据在 `build/copper-verification/`。M25两次复现相同：21映射、122不支持、9拒绝；历史报告保留，迁移范围未变。提交后从最终 SHA 重新导出 `build/application-bundle` 和 `build/data-modules`；通过 manifest.source_revision 检查发布身份。

## 精确下一步

1. 先执行 `git status --short --branch`、`git diff --stat`、`git rev-parse HEAD`，查询真实额度；保留任何未提交内容。本批无需重复广泛调查。
2. 冻结大陆高中教材的有限逐式目录。现有[课程覆盖表](CURRICULUM_COVERAGE.zh-CN.md)只是主题矩阵，不能证明教材全覆盖。优先 Fe 价态互转、Al 和非金属的高价值小批次，证据、条件、正例和边界一起补。
3. 浓度、过量、催化、可逆、电极式需要先确定必要语义。案例自动推广尚未实现；已有规则可以推导知识充分但未存储的方程，不能仅凭标签或守恒猜产物。

## 额度与自动续作

本次5小时额度已达93%，停止新工作流，仅收尾保存。重置时间为北京时间2026-09-27 08:43:54。heartbeat `automation` 保持 ACTIVE，每5小时在50分触发，为本次刷新留余量；后续按真实重置时间检查。额度未恢复则安静等待，不暂停/删除任务，不将长期目标标记完成。旧测试进程14838已结束；不要重新启动该全套。
