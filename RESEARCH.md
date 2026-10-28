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


## R2 — ordering reverses the apparent function-family knee

Follow-up ordering experiments show that the R1 total-function blow-up was largely an encoding-order artifact rather than an intrinsic consequence of the family cardinality.

For total functions on an 11×11 relation universe (121 atoms; 285,311,670,611 represented functions):

- `as-is` + row-major: build ≈0.039 s, peak RSS ≈30,228 KiB.
- `bfs` + column-major: build ≈0.039 s, peak RSS ≈31,044 KiB.
- `bfs` + row-major: build ≈0.052 s, peak RSS ≈30,120 KiB.
- `as-is` + column-major: build ≈26.64 s, peak RSS ≈4,696,920 KiB.
- `dfs` + row-major: build ≈20.70 s, peak RSS ≈4,823,864 KiB.
- `greedy` row-major, `greedy` column-major, and `dfs` column-major did not complete within the 30 s resource bound.

At n=10, locality-preserving orderings are already dramatically cheaper:

- `bfs` + row-major: ≈0.0116 s, ≈26,776 KiB.
- `as-is` + row-major: ≈0.0235 s, ≈26,232 KiB.
- `greedy` + row-major: ≈3.09 s, ≈691,796 KiB.

### Revised interpretation

The R1 result remains valid as an observation about the original Graphillion encoding, but its earlier interpretation is superseded.

The dominant factor is **constraint locality relative to decision-diagram variable order**. A total-function constraint decomposes naturally by left-domain element: exactly one atom from each row of A×B must be selected. Row-major `as-is` ordering keeps each such choice block contiguous, allowing compact factorization. Graph-oriented traversals can interleave those blocks and destroy that sharing.

This is stronger evidence for H2 than R1 alone: the same semantic family can move by orders of magnitude in time and memory solely from representation order. Searillion therefore must treat variable ordering as part of compilation semantics and benchmark metadata, not as an incidental backend tuning parameter.

The next experiment scales the locality-preserving `bfs` and row-major `as-is` orderings beyond n=11.


## R3 — locality-preserving ordering postpones, but does not remove, the scale frontier

Scaling the locality-preserving total-function encodings gives a second, more credible frontier.

Observed with Graphillion 2.1 / Python 3.12.15 on GitHub Actions:

- n=12, row-major `as-is`: 12^12 = 8,916,100,448,256 functions; build ≈0.131 s; peak RSS ≈40,840 KiB.
- n=12, row-major `bfs`: build ≈0.119 s; peak RSS ≈39,416 KiB.
- n=16, row-major `as-is`: 16^16 = 18,446,744,073,709,551,616 functions; build ≈3.60 s; peak RSS ≈493,592 KiB.
- n=16, row-major `bfs`: build ≈3.47 s; peak RSS ≈477,704 KiB.
- n=32, both row-major `as-is` and `bfs`: no completed measurement inside the 30 s resource bound.
- n=64, both row-major `as-is` and `bfs`: no completed measurement inside the 30 s resource bound.

### Interpretation

R2 corrected a severe ordering pathology, but ordering does not abolish the underlying growth. The currently defensible statement is:

1. semantic-locality-preserving variable order is necessary for practical scaling on this family;
2. once locality is preserved, the practical knee moves from roughly n≈11 to somewhere between n=16 and n=32 on the current Graphillion encoding and GitHub-hosted runner;
3. the represented family cardinality remains a poor predictor of cost by itself;
4. the next useful experiment is a bounded search over n in the interval (16,32), not another jump to larger powers of two.

This also strengthens the requirement that Searillion's compiler choose and record variable order from semantic constraint structure rather than accept backend defaults blindly.
