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


## R4 — locality-preserving function-family frontier narrows to n=18–20

A bounded follow-up using the best observed encoding (row-major, `as-is`) narrows the current hosted-runner frontier:

- n=18: 18^18 = 39,346,408,075,296,537,575,424 functions; build ≈19.30 s; peak RSS ≈2,034,352 KiB.
- n=20: no completed measurement inside the 30 s resource bound.
- n=22: no completed measurement inside the 30 s resource bound.
- n=24: no completed measurement inside the 30 s resource bound.

A follow-up n=19 probe also produced no completed measurement inside the 30 s bound. The current practical integer crossover is therefore **between n=18 and n=19** under this exact backend, ordering, host class, and 30 s cap.

This result should not be generalized to all ZDD engines or all encodings. It is a measured frontier for Graphillion 2.1 using the current bipartite relation encoding and locality-preserving variable order.


## R5 — Graphillion's process-global universe requires an explicit Searillion workspace

The current Graphillion API maintains a process-global universe mapping. The initial Searillion wrapper incorrectly presented each `RelationUniverse` instance as though it owned an independent backend universe.

That is unsafe: constructing a second relation universe replaces Graphillion's global edge/object table while previously-created ZDDs still exist. Without a guard, later iteration or pair-based operations can decode or address those old diagrams through the wrong mapping and produce plausible but semantically incorrect results.

### Immediate remediation

Searillion now associates each `RelationUniverse` with the Graphillion-universe generation under which it was created. Creating a newer universe invalidates older universes and their families for backend-dependent operations. Stale use raises rather than silently returning corrupted semantics.

### Architectural consequence

This guard is intentionally an interim safety boundary, not the final composition model.

Relational composition, projection across signatures, and multi-relation finite models require an explicit shared compilation workspace that owns one coordinated backend atom universe. Related typed relation spaces should be compiled into that workspace together, with stable atom identities and a semantically chosen variable order.

This becomes a prerequisite for a defensible implementation of composition.


## R6 — shared multi-signature workspace validated

A compiled `RelationWorkspace` now permits multiple typed relation signatures to coexist safely inside one Graphillion universe.

The workspace:

- tags atoms by relation signature and endpoint side;
- compiles all declared signatures into one stable backend universe;
- restricts each signature's families to that signature's atom slice using a Graphillion search space;
- preserves simultaneous validity of families from different signatures;
- supports per-signature full powersets, exact-cardinality families, explicit families, total functions, and bijections;
- invalidates an older workspace if a newer workspace replaces the process-global Graphillion universe.

CI regression tests verify that using one signature does not invalidate another within the same workspace and that local family counts do not accidentally include atoms belonging to neighboring signatures.

This removes the immediate global-universe blocker for composition. It does not yet provide symbolic relational composition itself.


## R7 — disjoint family product is effectively free after factor construction

Graphillion's family `join` provides an extremely cheap symbolic Cartesian product when the participating relation signatures occupy disjoint atom slices.

Observed in a shared workspace:

- n=12:
  - each function family contains 12^12 = 8,916,100,448,256 relations;
  - building R functions ≈0.394 s;
  - building S functions ≈0.311 s;
  - joint product contains 12^24 = 79,496,847,203,390,844,133,441,536 relation-choice pairs;
  - building the joint product ≈0.00012 s;
  - exact joint count ≈0.00013 s.

- n=16:
  - each factor contains 16^16 = 18,446,744,073,709,551,616 relations;
  - building R functions ≈4.93 s;
  - building S functions ≈3.45 s;
  - joint product contains 16^32 = 2^128 = 340,282,366,920,938,463,463,374,607,431,768,211,456 relation-choice pairs;
  - building the joint product ≈0.00015 s;
  - exact joint count ≈0.00021 s;
  - peak RSS remained ≈459,564 KiB, dominated by factor construction.

### Interpretation

For independent relation signatures with disjoint variables, product cardinality is almost irrelevant to the cost of combining already-compiled families. The ZDD representation preserves the factorization directly.

This supplies the first half of generic relational composition: symbolic pairing of candidate R and S relations is practical. The unresolved half is enforcing composition semantics and existentially projecting away intermediate/source relation atoms.


## R8 — exact existential projection remains cheap on factorized joint families

Joint-family projection now uses exact Boolean existential elimination one atom at a time. For an eliminated atom x:

- negative cofactor: members excluding x;
- positive cofactor: Graphillion quotient by the singleton family {{x}}, which removes x from members containing it;
- projected family: union of the two cofactors.

A correlated-family regression test verifies true existential semantics and deduplication, not only recovery of an independent product factor.

Observed on Graphillion 2.1 / Python 3.12.15:

- n=4: eliminate 16 atoms in ≈0.0020 s.
- n=8: eliminate 64 atoms in ≈0.0071 s.
- n=12: eliminate 144 atoms in ≈0.0186 s.
- n=16: eliminate 256 atoms in ≈0.0441 s.

At n=16 the two function-family factors required ≈4.70 s and ≈3.37 s to build, while their symbolic join required ≈0.00016 s and existentially eliminating one entire 256-atom signature required ≈0.044 s. The projected result exactly recovered all 16^16 functions.

### Interpretation

For this factorized workload, both multi-family product and generic existential elimination are cheap once the source factors exist. Factor construction remains dominant.

This does not establish that projection is universally cheap: entangled constraints can create very different intermediate diagrams. The next experiment deliberately introduces such coupling by enforcing exact relational composition,
T(a,c) iff there exists b with R(a,b) and S(b,c), before projecting R and S away.


## R9 — exact relational composition works, with an entanglement-driven frontier between n=5 and n=6

Searillion now computes the exact family
{S o R | R in F_R, S in F_S}
inside one shared workspace.

The construction is:

1. symbolically form F_R × F_S × P(T);
2. for every target atom T(a,c), partition the current joint family by whether some b witnesses R(a,b) and S(b,c);
3. require T(a,c) on the witness partition and exclude it on the no-witness partition;
4. existentially project the R and S signatures away.

Small-universe tests compare the symbolic result against an explicit extensional oracle and cover multiple witnesses, no witnesses, duplicate composed results, and ambient-carrier identity.

For total functions A→B and B→C with |A|=|B|=|C|=n, every function A→C is realizable, giving an exact final-family oracle of n^n.

Observed on Graphillion 2.1 / Python 3.12.15:

- n=2: 16 source-function pairs → 4 distinct compositions; full composition ≈0.0011 s.
- n=3: 729 source pairs → 27 distinct compositions; full composition ≈0.0062 s.
- n=4: 65,536 source pairs → 256 distinct compositions.
  - composition-constraint family ≈0.0331 s;
  - final projection ≈0.0028 s;
  - peak RSS ≈36 MiB.
- n=5: 9,765,625 source pairs → 3,125 distinct compositions.
  - composition-constraint family ≈2.893 s;
  - final projection ≈0.365 s;
  - peak RSS ≈399 MiB before projection and ≈409 MiB overall.
- n=6: both input function families build in ≈0.002–0.003 s, but the composition-constraint family does not complete within the 30 s resource bound; final projection is never reached.

### Interpretation

This is the first measured frontier caused by semantic coupling rather than merely poor variable order or raw family cardinality.

Independent family product is nearly free and generic existential projection is cheap on the factorized workload. The sharp n=5→n=6 increase appears when the constraints T(a,c) iff there exists b: R(a,b) and S(b,c) entangle the three relation signatures and destroy much of the previous factorization.

The current practical composition crossover is therefore between n=5 and n=6 for this exact encoding, ordering, Graphillion version, host class, and 30 s cap. This is a target for representation/order optimization, not a claim about an intrinsic ZDD complexity bound.


## R10 — simple global variable orders do not remove the n=6 composition frontier

The first composition-ordering pass compared five workspace-wide atom orders at n=5 and n=6:

- signature-major (baseline);
- row-block R/S/T;
- witness-first;
- target-first;
- middle-carrier-first.

At n=5, all strategies produced the correct 3,125-function result family.

Representative timings:

- signature-major:
  - constraint family ≈2.705 s;
  - projection ≈0.308 s;
  - peak RSS ≈399–409 MiB.
- middle-first:
  - constraint family ≈2.611 s;
  - projection ≈0.471 s;
  - peak RSS ≈398–400 MiB.
- row-block R/S/T:
  - constraint family ≈4.688 s;
  - projection ≈0.208 s;
  - peak RSS ≈430–436 MiB.
- witness-first:
  - constraint family ≈6.159 s;
  - projection ≈0.896 s;
  - peak RSS ≈790–809 MiB.
- target-first:
  - constraint family ≈6.033 s;
  - projection ≈0.696 s;
  - peak RSS ≈788–793 MiB.

At n=6, every tested order built the two 46,656-member input function families in milliseconds, but none completed the composition-constraint family within the 30 s resource bound.

### Interpretation

Unlike the earlier total-function result, this frontier is not removed by obvious locality-preserving or constraint-local atom orders. Ordering still matters quantitatively, but the tested global orders do not explain the n=5→n=6 cliff.

The next hypothesis targets the construction algorithm itself. The current composer begins with F_R × F_S × P(T), introducing every possible target relation before filtering it to the unique composition. A deterministic target-construction algorithm can instead begin with F_R × F_S and graft T(a,c) only onto assignments for which a witness exists, avoiding the 2^(|A||C|) unconstrained target factor.


## R11 — deterministic target grafting halves memory at n=5 but does not move the n=6 frontier

A second exact composition construction avoids the unconstrained P(T) factor entirely.

Instead of starting from F_R × F_S × P(T) and filtering T, the graft algorithm starts from F_R × F_S. For each target atom T(a,c), it identifies assignments with at least one R/S witness and uses Graphillion family join with {{T(a,c)}} to graft the target atom onto exactly those assignments.

Extensional tests verify that graft and filter produce exactly the same composed relation families, including multiple-witness and no-witness cases.

At n=5:

- filter:
  - constraint construction ≈2.44 s;
  - projection ≈0.31 s;
  - peak RSS ≈399–409 MiB.
- graft:
  - constraint construction ≈1.55 s;
  - projection ≈0.35 s;
  - peak RSS ≈212–217 MiB.

Thus graft reduces constraint time by roughly one third and approximately halves peak memory at the largest successful benchmark.

However, graft does not move the current 30 s frontier:

- n=6: input factors build in milliseconds, but graft constraint construction does not complete inside 30 s.
- n=7: same resource-bound outcome.
- n=8: same resource-bound outcome.

### Interpretation

The unconstrained target powerset was a substantial but secondary source of cost. Removing it improves the successful regime without eliminating the sharp entanglement frontier.

Graft becomes the default composition constructor because it is exact, conceptually direct, and materially cheaper. The original filter constructor is retained as an experimental baseline.

The remaining bottleneck is the symbolic enforcement of the witness-dependent target relation itself, not target-choice multiplicity, generic projection, or independent family product.


## R12 — early source-row elimination moves composition's practical frontier to n=9–10 (local, awaiting CI replication)

### Hypothesis and exactness argument

The R9–R11 constructors retain *all* R/S assignment atoms while every target witness constraint is added. This may force the diagram to represent correlations that need not survive until the final target is complete.

For each source row `a`, every constraint for `T(a,*)` depends on `R(a,*)` and the **shared** S relation, but no subsequent target row reads `R(a,*)`. Therefore, after grafting an entire target row, we can existentially eliminate its R atoms before moving to the next row. Existential elimination commutes with future constraints that do not mention the eliminated atoms. This holds even when the input R family couples different rows: elimination retains those correlations as restrictions on the surviving R/S/T atoms. Eliminating S early or treating target rows as independent would *not* be sound in general.

The new `_composition_joint_graft_rows()` returns a joint family over S,T, after having already projected out R one row at a time. Explicit tests cover cross-row R correlation with shared S, rectangular families, empty families, and an independent total-function target oracle. The original filter and graft constructors remain as controls.

### Local measurements (2026-11-04)

Python 3.12.14, Graphillion 2.1, Linux 6.18.57 x86-64, tagged Graphillion relation edges, `as-is` traversal, signature-major/row-major atom order. Inputs are deterministic *complete* total-function families (no seed). The rows below measure only composition-constraint construction, **excluding factor builds and final S projection**. Peak RSS is the process high-water mark in KiB converted approximately to MiB. A 30-second bound is used throughout. The new runner instrumentation emits a per-row measurement immediately after that row's R atoms are eliminated.

| n | row-graft constraints | peak RSS | exact final target count | result |
| ---: | ---: | ---: | ---: | --- |
| 4 | 0.030 s | 19.5 MiB | 256 | completed |
| 5 | 0.027–0.048 s | 21.8–22.3 MiB | 3,125 | completed |
| 6 | 0.111 s | 41.5 MiB | 46,656 | completed |
| 7 | 0.872 s | 110.6 MiB | 823,543 | completed |
| 8 | 3.840 s | 384.7 MiB | 16,777,216 | completed |
| 9 | 16.507 s | 1,457.2 MiB | 387,420,489 | completed |
| 10 | no completion in 30 s | 1,547.4 MiB at fifth completed row | not reached | resource-bound timeout after 5/10 rows; 6.5 GB virtual-memory cap |

Same-host n=5 control, separate processes on the same Python/Graphillion environment:

- original graft: constraint construction **1.720 s**, peak RSS ≈202.5 MiB; final projection ≈0.426 s;
- row-graft: constraint construction **0.027 s**, peak RSS ≈21.7 MiB; final projection ≈0.0017 s;
- exact counts match, and both final families compare equal to an independently compiled target total-function family by GraphSet equality.

For the n=7 row-graft run, the same independent GraphSet equality oracle passed. The n=8 and n=9 local runs prior to adding that benchmark check have exact final counts but not independently verified full-family equality in those *individual* runs; small-family extensional tests and the n=7 independent symbolic oracle provide additional coverage. CI will execute the independent equality oracle on every completed case.

An optional diagnostic counts nonterminal serialization lines from Graphillion 2.1's internal `setset.dumps()` format; n=4 row checkpoints recorded 134, 162, 190, and 218 nodes. This is **provisional node-count instrumentation**, not yet an audited public API or cost-neutral measurement. It is opt-in because serialization may add material time and memory.

### Revised interpretation

R9–R11 remain valid observations about *those constructors*, but the claim that the n=5→n=6 cliff is inherent to witness-dependent semantic entanglement is too strong. A substantial part of that cliff was **delayed existential elimination**. The exact same semantic operation can finish n=9 with early row elimination, while retaining shared S correlations.

The new local practical knee is between n=9 and n=10 under the 30-second bound; this is still a steeply growing intermediate-diagram problem, not polynomial scaling. Next: reproduce the comparison on the same GitHub Actions runner, then test adversarial correlated, sparse, bijection, and partial-function families; identify whether the remaining blow-up is due to surviving S/T coupling or a more favorable elimination order is possible.


## R13 — GitHub Actions confirms R12; row elimination becomes default

PR #14 merged at `9bfdcd4eedef6758925d36ac0db639d995b7b6b6`. The [composition-graft CI run](https://github.com/cohereworks/searillion/actions/runs/41882644698) executed thirteen bounded jobs on Ubuntu hosted runners, Python 3.12.15, Graphillion 2.1. All thirteen jobs **passed their workflow contract**, with expected 30-second resource-bound cases classified rather than mistaken for successful completion. The other nine triggered workflows also passed; the full test suite was green. The composition run retained thirteen named JSONL artifacts, including incremental row checkpoints and timeout classifications.

Exact total-function composition on the same runner class:

| n | constructor | constraints (s) | process peak RSS (KiB) | result |
| ---: | --- | ---: | ---: | --- |
| 5 | graft (R11) | 1.1896 | 212,368 | exact T-function family |
| 5 | row-graft (R12) | 0.0222 | 27,668 | exact T-function family |
| 6 | row-graft | 0.1197 | 47,600 | 46,656, exact T-function family |
| 7 | row-graft | 0.6648 | 118,224 | 823,543, exact T-function family |
| 8 | row-graft | 2.8897 | 399,120 | 16,777,216, exact T-function family |
| 9 | row-graft | 12.4422 | 1,496,440 | 387,420,489, exact T-function family |
| 10 | row-graft | incomplete >30 | 2,987,240 at row 6/10 | resource-bound timeout |

Each completed row-graft job performed exact GraphSet equality against an independently compiled target total-function family; n=5 legacy graft passed the same independent oracle. The n=6–8 legacy graft and n=6 filter jobs completed their *bounded workflow* successfully through timeout classification, not by computing a target result. Their historical performance cliff remains valid.

At n=5, early elimination reduces constraint-construction time by approximately **54×** and high-water RSS by **7.7×** on comparable GitHub Actions runners. It also shifts projection of R from the final projection phase into construction, so a fairer total composition comparison includes both phases: 1.4807 s for delayed graft vs 0.0237 s for row-graft, approximately **62×**. These ratios are workload/runner-specific, not asymptotic guarantees.

The n=10 benchmark timed out after row 6, retaining the row-6 RSS observation of ≈2.85 GiB (no final relation count). The frontier is thus **n=9 completed, n=10 resource-bound** under the exact 30-second rule and current encoding. R9–R11's n=5→6 cliff was a property of their delayed-elimination construction, not a necessary cost of exact composition.

### Decision and remaining uncertainty

Row-graft is now the default `RelationWorkspace.compose()` constructor; filter and delayed graft remain available as research controls. Tests include S/T pair-level oracles to prevent an incorrect row-independent shortcut. This is an algorithm-selection decision for the current implementation, **not** proof that row-graft dominates for all input-family structures.

Next tests must vary input family structure (bijections, sparse relations, partial functions, cross-row correlations), variable order and elimination schedule, and distinguish true ZDD node growth from process RSS/allocator effects. The serialization-line node diagnostic remains preliminary and does not yet establish a backend-independent metric.


## R14 — input-family structure radically changes composition cost (local controls, awaiting CI)

### Hypothesis and controls

The R12/13 improvement may depend on the factorized row structure of total functions. Use the same shared workspace, atom order, Graphillion 2.1 backend and exact composition constructors, varying **only the source-family constraints**:

- `bijections`: R,S each range over all permutations; exact target family is all permutations, size n!;
- `single-edge`: R,S each contain exactly one atom; for n≥2, the target family comprises the empty relation and each possible singleton target, size n²+1;
- `unrestricted`: R,S each range over the full powerset; for n=n=n with an available identity S, every T is attainable, giving 2^(n²) targets.

Independent GraphSet equality oracles verify the final family, not just its cardinality. Small explicit tests for each case were added before benchmark extension. The existing `composition_graft.py` runner now takes an optional `--family` flag, defaulting to the historical total-function workload; it retains factor/construction/projection separation and emits resource-bound row checkpoints.

### Preliminary local measurements (2026-11-04)

Graphillion 2.1, Python 3.12.14, Linux 6.18.57 x86-64, `as-is`, signature-major/row-major, no seed; 30-second bounds. Timings below are constraint construction only; peak RSS is process-wide. Completed runs pass the independent exact target-family oracle.

| family | n | algorithm | constraint (s) | peak RSS (KiB) | output family/result |
| --- | ---: | --- | ---: | ---: | --- |
| bijections | 5 | row-graft | 0.0227 | 22,496 | 120, exact |
| bijections | 8 | row-graft | 9.340 | 800,852 | 40,320, exact |
| bijections | 9 | row-graft | >30 | 1,555,272 at row 4/9 | timeout |
| single-edge | 9 | row-graft | 0.0444 | 22,716 | 82, exact |
| single-edge | 9 | delayed graft | 0.0298 | 22,724 | 82, exact |
| single-edge | 12 | row-graft | 0.1092 | 32,440 | 145, exact |
| unrestricted | 4 | row-graft | 1.607 | 207,544 | 65,536, exact |
| unrestricted | 5 | row-graft | >30 | 116,920 at row 1/5 | timeout |
| unrestricted | 4 | delayed graft | >30 | unavailable after bound | timeout |

For single-edge n=9, delayed graft's construction-plus-projection was **0.0358 s** versus row-graft's **0.0470 s**: an explicit counterexample to blanket row-graft superiority, though a small absolute difference susceptible to runner noise. With bijections at n=8, only 40,320 outputs cost ~9.3 s, versus 16.8 million total-function outputs costing ~3.5 s on the same local platform. The unrestricted case exposes a severe n=4→5 knee despite trivial input-family construction.

### Interpretation

The feasible regime is strongly dependent on **the geometry of correlations induced by family constraints**, not on final result cardinality or input cardinality alone. Row elimination is a good current default based on R13, not a universal winner. A compiler eventually needs a structural cost model and perhaps alternative composition schedules/engines; do not hardcode a universal "row-local" assumption from total functions.

CI will replicate this heterogeneous control matrix with exact output checks, 30-second resource classifications, and retained artifacts before promoting these observations beyond their local host.
