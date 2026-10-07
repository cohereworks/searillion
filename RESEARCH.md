# Research Ledger

## R0 — framing

### Primary question

When can finite SEAR objects and operations be represented as compressed ZDD-backed families strongly enough that manipulating the family is materially cheaper than enumerating its members?

### Non-claim

Searillion does not assume that ZDDs change worst-case complexity classes. Exponential cost may reappear as decision-diagram size, poor variable ordering, expensive projection/composition, schema churn, or weak structural sharing.

## H1 — finite-SEAR substrate

Graphillion/ZDD machinery can support a useful finite fragment of SEAR with natural representations for sets, elements, binary relations, constrained relation families, projection, composition, and selected quotient/equivalence constructions.

**Falsifiers include:** representation impedance so large that the SEAR layer mostly reconstructs machinery outside Graphillion; common SEAR operations requiring repeated enumeration; or composition/projection destroying compression under otherwise favorable inputs.

## H2 — family-level computational leverage

For sufficiently structured families, cost correlates more strongly with compressed decision-diagram structure than with represented family cardinality, permitting exact operations over spaces that cannot be explicitly enumerated.

**Falsifiers include:** representative structured workloads producing diagrams comparable to explicit state spaces; construction cost dominating all subsequent reuse; or practically important operations consistently triggering explosive intermediate diagrams.

## H3 — logical derivation/canonicalization

Logical forms and derivation families contain enough repeated structure in selected regimes that ZDD-backed representations materially reduce the cost of retaining and transforming large equivalence or solution families.

This hypothesis is intentionally split by problem type and complexity regime. SAT decision, counting, formula equivalence, minimization, and rewrite closure are distinct problems and must not be conflated.

## H4 — transfer beyond graph problems

If H1/H2 hold, SEAR may provide a useful semantic bridge from ZDD techniques to non-obviously-graphical problems such as execution paths, constrained symbolic languages, policy spaces, and sparse neural computation.

Application probes do not graduate to claims until the core representation measurements justify them.

## Known risk register

1. Variable ordering dominates representation size.
2. Projection or relational composition creates catastrophic intermediate diagrams.
3. Partition/equivalence families resist compression despite natural representation.
4. Dense relations erase sparsity advantages.
5. Semantic remapping requires costly reconstruction.
6. Continuous-domain applications lose their semantics during discretization.
7. Graphillion's graph-oriented API becomes the wrong abstraction despite its ZDD substrate.
8. Benchmark selection accidentally favors compressible examples and overstates generality.
9. Counting appears cheap only because construction costs are hidden.
10. Memory locality and allocator behavior dominate nominal node-count improvements.

## Evidence rule

For each notable result, preserve:

- exact input/generator and seed;
- encoding;
- variable order;
- Graphillion/runtime version;
- baseline algorithm;
- build time and operation time separately;
- memory and diagram-size observations where measurable;
- output correctness oracle;
- failure/timeout/resource-cap status;
- interpretation and competing explanations.


## R1 — first structured-family result

Observed on GitHub Actions, Python 3.12.15, Graphillion 2.1:

- Total functions on a 10×10 relation universe (100 atoms): family size 10^10; build wall time ≈3.02 s; peak RSS ≈698,724 KiB; exact count ≈0.003 s.
- Total functions on a 12×12 relation universe (144 atoms): construction did not complete before external cancellation after >74 s. This is recorded as a resource-bound outcome, not a semantic failure.
- Bijections on a 16×16 relation universe (256 atoms): family size 16! = 20,922,789,888,000; build wall time ≈0.275 s; peak RSS ≈124,548 KiB; exact count ≈0.037 s.

### Interpretation

The first important result is **structural asymmetry**. Family cardinality alone does not predict difficulty: a 16×16 bijection family with ~2.09×10^13 members is easy to build and count, while the 12×12 total-function family becomes expensive despite having a highly regular closed-form description.

This supports H2 only in the qualified sense intended: useful leverage depends on the structure exposed to the chosen decision-diagram encoding, not merely on the number of represented relations.

The immediate follow-up is to probe n=11 for total functions and convert over-budget construction into an explicit benchmark classification rather than a failing CI job. Variable ordering and the Graphillion graph-oriented encoding remain live alternative explanations for the function-family blow-up.
