# Work Plan

This file is the canonical execution plan for Searillion. It is expected to evolve as evidence changes the research direction. Checkmarks describe implemented/tested capability, **not** universal scalability or final SEAR-semantic certification. See `RESEARCH.md` for measured boundaries.

## Current priority (after R11)

1. [x] Reconcile completed Phase 0/1 work and close superseded PR #4 without merging the pre-workspace prototype.
2. [x] Test source-row grafting with *incremental* elimination of completed R rows; preserve correlations through shared S. Compare against exact extensional oracles.
3. [x] Complete same-runner, bounded n=4–10 benchmarks of graft vs row-elimination; retain row checkpoints and resource-limit outcomes in CI artifacts (R13).
4. [x] Promote row-wise elimination as the default public composer after exactness and CI replication (R13); retain both legacy constructors as research controls.
5. [ ] Measure intermediate DD node counts using a defensible backend-specific method, report instrumentation overhead, and identify the next growth knee.
6. [ ] Compare total functions against bijections, sparse/partial, correlated, and adversarial relation families before generalizing the improvement. R14 adds bijection, single-edge, and unrestricted local controls; CI replication and partial/correlated performance cases remain.
7. [ ] Only if fused elimination still fails badly, specify the missing backend primitive and assess lower-level DD engines.

## Phase 0 — substrate and measurement

- [x] Record supported Python and Graphillion versions (Phase 0 CI matrix).
- [x] Add CI matrix covering current Graphillion plus selected historical baselines.
- [x] Establish deterministic experiment scripts and machine-readable JSONL results (central orchestration remains future work).
- [ ] Capture wall time, CPU time, peak RSS, ZDD size/node count where available, variable order, package versions, seed, and failure classification. Timings/RSS/version/order/classification work; generalized DD-node measurement is still incomplete.
- [x] Add explicit brute-force/combinatorial baselines and correctness oracles (for implemented operations).
- [x] Establish artifact retention for benchmark results (Actions uploads; bounded timeouts are classified).

## Phase 1 — finite SEAR kernel

- [x] Define finite carriers and stable tagged atom indexing within a compiled workspace.
- [x] Represent finite relation subsets and families of them (not yet every SEAR set construction).
- [x] Represent binary relations as subsets of Cartesian-product universes.
- [x] Implement family union/intersection/difference.
- [x] Implement projection / existential elimination.
- [x] Implement exact relational composition (several constructors, bounded frontier).
- [x] Implement exact counting without member enumeration where supported.
- [x] Validate implemented operations against explicit ground truth on small universes.

## Phase 2 — compression frontier

- [x] Full power-set baseline.
- [x] Cardinality-constrained families.
- [ ] Implication/exclusion constrained families.
- [x] Structured relation families (total functions and bijections).
- [ ] Equivalence relations / partitions.
- [x] Measure variable-order sensitivity (R2/R10; not exhaustive).
- [ ] Construct adversarial families intended to destroy sharing.
- [ ] Identify the first practical failure knee for each operation, not merely construction.

## Phase 3 — logical-family experiments

- [ ] Define logical encoding independently of any claim that one encoding is optimal.
- [ ] 2-SAT family experiments.
- [ ] Horn-SAT family experiments.
- [ ] XOR/affine family experiments.
- [ ] Bounded-treewidth and small-backdoor experiments.
- [ ] Logical canonicalization / equivalence-family experiments.
- [ ] #SAT/counting comparisons.
- [ ] Random/adversarial 3-SAT near hard regimes.
- [ ] Separate decision, counting, equivalence, minimization, and rewrite-closure claims.

## Phase 4 — application probes

Promote only after the core measurements justify them.

- [ ] Software execution-path families.
- [ ] Sparse/gated neural-network path or activation families.
- [ ] Constrained symbolic/text encodings.
- [ ] Configuration/design-space analysis.
- [ ] Policy/access-control relation families.
- [ ] Program-synthesis sketch spaces.

## Exit products

The primary result is not required to be a library.

A successful project may instead produce:

- an executable finite-SEAR engine;
- a reusable ZDD-backed family algebra;
- a benchmark corpus;
- encoding and variable-order heuristics;
- a map from problem structure to practical feasibility;
- well-characterized negative results showing where this approach fails.
