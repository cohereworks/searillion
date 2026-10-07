# Work Plan

This file is the canonical execution plan for Searillion. It is expected to evolve as evidence changes the research direction.

## Phase 0 — substrate and measurement

- [ ] Record supported Python and Graphillion versions.
- [ ] Add CI matrix covering current Graphillion plus selected historical baselines.
- [ ] Establish deterministic experiment runner and machine-readable result schema.
- [ ] Capture wall time, CPU time, peak RSS, ZDD size/node count where available, variable order, package versions, seed, and failure classification.
- [ ] Add explicit brute-force/combinatorial baselines.
- [ ] Establish artifact retention for benchmark results.

## Phase 1 — finite SEAR kernel

- [ ] Define canonical finite carriers and stable atom indexing.
- [ ] Represent sets and families of sets.
- [ ] Represent binary relations as subsets of Cartesian-product universes.
- [ ] Implement family union/intersection/difference.
- [ ] Implement projection / existential elimination.
- [ ] Implement relational composition.
- [ ] Implement exact counting without member enumeration where supported.
- [ ] Validate every operation against explicit ground truth on small universes.

## Phase 2 — compression frontier

- [ ] Full power-set baseline.
- [ ] Cardinality-constrained families.
- [ ] Implication/exclusion constrained families.
- [ ] Structured relation families.
- [ ] Equivalence relations / partitions.
- [ ] Measure variable-order sensitivity.
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
