# HS-Chemistry-Knowledge-Compiler

[简体中文](README.zh-CN.md)

Generate high-school chemistry equations and infer reactions deterministically from curated canonical data and bounded declarative Rules. Ontology, Entity/Relation facts, evidence, migration, and TeachingView support this equation-generation pipeline.

## Current executable scope

The F1/F2/F3 foundations, M4–M25 and follow-up corrections are recorded in the [roadmap](docs/ROADMAP.md). The corpus has 66 canonical Reactions, 15 active Rules, 119 fixtures and 38 aqueous profiles, including newly executable solid CaCO3/HCl. Mainland compulsory and selective-compulsory curriculum coverage remains incomplete; see the [coverage checklist](docs/CURRICULUM_COVERAGE.md).

Supported families include bounded neutralization, precipitation, acid-driven gas evolution, ammonium/base, metal/acid and metal/water hydrogen evolution, aqueous metal-salt displacement, and exact thermal/steam pilots. Missing knowledge remains UNKNOWN; explicit FALSE rejects a particular pathway without asserting a global negative Reaction.

```text
canonical YAML → schema/reference/chemistry validation → RulePlan matching
→ canonical product resolution → exact balancing → atom/charge validation
→ canonical Reaction comparison → ReactionCandidate + proof trace
```

## Run

Python 3.11+ is required. Install with `python -m pip install -e .`; install `pytest` separately for development checks.

```powershell
python -m compiler.cli validate
python -m compiler.cli compile --output build/compile --source-revision WORKTREE
python -m compiler.cli audit --output build/audit --source-revision WORKTREE
python -m compiler.cli export --output build/application-bundle --source-revision WORKTREE
python -m pytest -q
```

`audit` runs the checked-in fixtures; Applications load a fixed bundle through `compiler.application.InferenceSession`; see the [API contract](docs/contracts/APPLICATION_API.md). `infer_case` is the internal execution layer. Build outputs are generated artifacts, never editable chemistry truth. Use an exact Git SHA instead of WORKTREE when recording a verified build.

## Canonical ownership

| Concern | Owner |
| --- | --- |
| Chemical identities, composition, contextual facts, one-hop Relations | `knowledge/domain/`, `compiler/source.py` |
| Curated transformations and subordinate ReactionForms | Reaction records in `knowledge/domain/`, `compiler/reaction_forms.py` |
| Applicability and canonical product construction | `knowledge/rules/`, `compiler/rules.py`, `compiler/products.py` |
| Exact balancing and conservation | `compiler/balance.py` |
| Runtime inference and proof traces | `compiler/engine.py` |
| Source and artifact contracts | `schemas/`, `docs/contracts/` |
| Teaching projections | `knowledge/teaching/`; excluded from inference |
| Offline legacy reconciliation | `migration/`; excluded from runtime |

The compiler never guesses formulas or valences, fabricates product identities, or promotes inferred candidates into canonical Reactions. Formula/name values are lookup signals, not identity owners. Broader equilibrium, redox, activity-series reasoning, UI, and automatic bulk migration remain outside the implemented scope.

Compatibility coordinates remain source schema `3.7.0`, Rule DSL `1.4.0`, RulePlan `1.4.0`, and artifact format `1.5.0`; compiler versions are independent. Historical artifacts `1.0.0`–`1.5.0` remain admitted by the format gate.

See [Architecture](docs/ARCHITECTURE.md), [Inference](docs/inference/INFERENCE.md), [Coverage audit](docs/COVERAGE_AUDIT.md), and [Roadmap](docs/ROADMAP.md).
