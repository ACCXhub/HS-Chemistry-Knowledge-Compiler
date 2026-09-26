# 应用数据包与推断接口

[English](APPLICATION_API.md)

状态：compiler 0.4.0 已实现离线导出和 Python 接口；HTTP 路由、chem-wiki 适配器和数据库迁移尚未实现。

## 发布、安装和加载

```powershell
python -m pip install .
python -m compiler.cli export --output build/application-bundle --source-revision WORKTREE
```

正式发布时在已验证的干净 checkout 中，把 WORKTREE 替换为 `git rev-parse HEAD` 的完整 SHA。命令不会自动确认传入 SHA 与 checkout 相符。发布编译器 wheel 和整个数据包目录，并固定二者版本。wheel 不包含知识数据；部署端加载数据包无需原仓库、YAML、迁移包或数据库。

| 文件 | 契约 |
| --- | --- |
| manifest.json | bundle_format_version=1.0.0、compiler 精确版本、四项兼容坐标、源 SHA/语义摘要、各类计数、文件 SHA-256、release_id |
| knowledge.json | `records`：完整 Entity、Reaction（含 forms）、Rule、Evidence、Source、TeachingView，保留全部属性/关系/物种配置和引用 |
| knowledge-record.schema.json | 规范记录的 JSON Schema；与源校验共用引用、唯一性、原子/电荷验证 |
| inference-request.schema.json | 可供后端及前端校验的请求 JSON Schema；从现有 fixture 输入契约生成，并收窄为已支持的公共输入 |

所有 JSON 为规范化 UTF-8；文件哈希包括末尾 LF。release_id 是除自身字段外 manifest 的规范 JSON SHA-256，前缀 `hschem_`。同代码版本、源版本及内容产生相同数据包。加载器拒绝错误哈希、版本、计数、语义摘要和断开的规范引用，并重新编译 Rule。哈希提供完整性校验；发布来源由部署方固定，不能把未知来源的 manifest 当签名。

```python
from pathlib import Path
from compiler.application import InferenceSession
from compiler.source import SourceError

session = InferenceSession(Path("build/application-bundle"))
response = session.infer({
    "id": "wiki_request_001",
    "reactants": [
        {"target_id": "ent_substance_hbr", "phase": "aqueous"},
        {"target_id": "ent_substance_na2s2o3", "phase": "aqueous"},
    ],
    "context": {"medium": "aqueous", "temperature_regime": "ambient"},
})
assert response["result"]["status"] == "inferred"
assert response["result"]["canonical_match"]["state"] == "none"
```

在每个后端 worker 启动时加载一次，复用验证后的知识和 RulePlan；逐请求不读文件、不访问网络。不修改 session 内部对象；返回的 manifest 是副本。`infer_case` 是内部执行层，不代替公共输入校验。

## 请求

- `id` 是调用方关联标识，匹配 `^[a-z][a-z0-9_:-]+$`；不参与候选化学身份。
- `reactants` 当前为 1–2 个规范 Entity ID，物态必须显式提供：solid/liquid/gas/aqueous/dissolved/unknown。同一 ID 重复输入（即使物态不同）拒绝，不能静默丢物态。
- `context` 必须提供对象，可为空；仅允许 `medium: aqueous` 与 `temperature_regime: ambient|warmed|heated|frozen`。缺条件保留 UNKNOWN，不自动补常温或水溶液。heated 与 warmed 不等价；frozen 用于已有阻断边界。
- 不接受自由文本化学式、产物、投料量/比例、浓度、催化剂、电解、光照、压强等额外字段。配平系数表示当前规则的反应路径，不是实际混合物的限量、过量或平衡计算。扩展这些条件须先有对应语义，不能忽略后返回成功。
- 输入形状错误抛 `SourceError(code="request_invalid", stage="request_validation")`。未知 ID 则返回化学结果 `invalid/reference_unresolved`。

## 响应

外层固定为 `release_id`、`compiler_version`、`source_semantic_digest`、`result`。result 包含 `case_id`、`status`、`proof_trace`；成功时另有 `rule_id`/`rule_version`、`candidate_key`、`participants`、`validation`、`canonical_match`、`provenance`。参与者使用 role/target_id/target_kind/phase 和精确 `{numerator, denominator}` 系数，禁止转浮点保存。

| status | 应用含义 |
| --- | --- |
| inferred | 有适用规则、产物已解析、配平且原子/电荷守恒；canonical_match 可为 none，候选不自动入规范库 |
| indeterminate | 必需知识或条件缺失，尚不能判断 |
| no_match | 当前规则范围没有匹配路径，不代表化学上绝不反应 |
| blocked | 当前考虑路径被条件阻断，不是全局 FALSE |
| ambiguous | 多条规则无法唯一消解；保留诊断，不选第一条 |
| invalid | 身份/产物/物态证据或守恒等失败；不显示为“不反应” |

例如 aqueous 离子对产物无溶解性事实为 `product_phase_unverified`，已知不溶却请求 aqueous 为 `product_phase_conflict`，均不输出候选。proof trace 的 TRUE/FALSE/UNKNOWN 属于具体谓词；缺事实不是 FALSE。`canonical_match.state = conflict` 同样应显示审查提示。

## chem-wiki HTTP 适配建议（尚未部署）

建议 `POST /v1/reaction-builder/infer` 由现有 reaction_builder 持有适配器。请求中的 application UUID 经 knowledge_catalog 的已审核 crosswalk 映射为 compiler ID，返回 DTO 再反向映射。来源 Source、Evidence 和规范 Reaction 查询归 knowledge_catalog；应用 Reaction 物化归 reaction_core，前端 EquationDraft 不保存事实。

HTTP 建议：合法请求的六类化学结果均为 200；请求校验或未映射 UUID 为 422；固定数据包无法加载则 worker 启动失败/503；不向前端泄露本地路径。保留详细 trace 供展开调试。数据字典及 PostgreSQL 表复用、导入幂等和回滚约束见 [chem-wiki 接入说明](CHEM_WIKI_INTEGRATION.md)。
