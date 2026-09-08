# Roadmap

## Current state

F1 architecture convergence is complete at `eeff560b176b4d4b0cb45aec663413325ac39232`.

F2 implements the first executable contract-to-candidate proof on `workstream/f2-contract-to-candidate`:

```text
canonical YAML source
→ JSON Schema validation
→ reference / facet / context resolution
→ source Rule compilation to internal RulePlan
→ deterministic inference
→ canonical product resolution
→ exact rational balancing
→ atom + charge validation
→ canonical Reaction comparison
→ ReactionCandidate + structured proof trace
→ deterministic JSON artifacts
```

The slice contains only two positive chemistry families—AgCl precipitation and strong acid/base neutralization—plus explicit UNKNOWN and blocker cases.

## F2 acceptance boundary

F2 is considered complete when the repository test/CLI workflow proves:

- malformed source is rejected;
- references resolve before inference;
- absent open-world context remains `UNKNOWN` rather than false;
- declared blockers produce an explicit blocked result;
- precipitation and neutralization infer canonical products;
- balancing uses fixed products and exact arithmetic;
- atom and charge conservation are explicit validations;
- canonical comparison happens after candidate validation;
- generated candidates use deterministic `candidate_key` and no time-based review UUID;
- molecular and net-ionic forms remain projections of the curated Reaction where appropriate;
- repeated audit builds are byte-stable;
- source file traversal order does not change semantic output.

## F3 — Contract hardening and small migration pilot

The next phase should broaden only where F2 evidence justifies it:

1. harden reusable typed/faceted rule patterns and compile-time overlap diagnostics;
2. generalize the context/fact assertion operators needed by a small real chemistry sample;
3. make `ReactionForm` projection/speciation rules explicit beyond the two F2 fixtures;
4. freeze external artifact compatibility/versioning beyond `f2.0`;
5. migrate a small evidence-backed subset of real high-school chemistry data through the new contracts;
6. measure before considering alternative runtimes or native acceleration.

Still out of scope: full corpus migration, D01-D11 population, database services, UI integration, RETE, Rust/C++ optimization, and speculative plugin frameworks.
