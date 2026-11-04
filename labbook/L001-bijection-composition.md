# L001 — Why is n=8 bijection composition unexpectedly expensive?

**Date:** 2026-11-04. **Status:** exploratory mechanism, CI-reproduced
original anomaly (R15), exact outputs verified for completed controls.
**Related evidence:** [R13](../RESEARCH.md#r13--github-actions-confirms-r12-row-elimination-becomes-default),
[R15](../RESEARCH.md#r15--structural-controls-replicated-in-ci-row-graft-is-not-uniformly-optimal).

## Purpose and significance

In CI, composing *all* n=8 bijection families took 7.55 s and 803,812 KiB
peak RSS to produce only 40,320 distinct output relations. Composing two
larger total-function families at n=8 took 2.89 s and 399,120 KiB, despite
16,777,216 outputs. Is that a correctness bug, measurement artifact, or
a predictable consequence of different dependencies in the input families?

This matters because Searillion's goal is to predict the compression frontier
from **problem structure**, not output count.

## Hypothesis and falsifiers

- **H1 (correctness issue):** the composition may be wrong. Test independently
  constructed target-family *equality*, not only counts, and small explicit
  product oracles. A mismatch confirms an actual semantic bug.
- **H2 (cross-row structure):** bijectivity couples R rows via injectivity.
  After eliminating k rows, the joint family must retain information about
  the set of k middle-carrier elements already used. Expect intermediate DD
  shape with a central binomial peak, unlike row-independent total functions.
  A monotone/constant bijection node trace or the same trace for total
  functions would contradict this proposed mechanism.
- **H3 (shared S interaction):** the expensive case requires both a
  nontrivial R choice and unknown shared S. Replacing S with a fixed identity
  or replacing bijective R with row-independent functions should materially
  reduce cost. These counterfactuals isolate constraints, not output size.

## Method and controls

- Three finite n×n relation signatures R:A×B, S:B×C, T:A×C.
- Tagged Graphillion relation-edge atoms, **signature-major/row-major**
  order, `as-is` traversal; Graphillion 2.1, Python 3.12.14, Linux x86-64.
- Construct source families independently, join R×S, then for each source
  row graft each target witness atom and existentially eliminate that R row.
  Project shared S only after completing all target rows.
- Instrument row-boundary diagram size by counting nonterminal lines in
  Graphillion's internal `graphset._ss.dumps()` representation. This is an
  **opt-in, potentially expensive diagnostic**; it does not measure
  transient peak nodes and is not a stable public Graphillion API.
- Compare complete bijections/bijections to total-functions/total-functions
  (n=8) and four asymmetric substitutions (n=8). Run bijections at
  n=5,6,7,8 for a size-pattern check.
- All families are deterministic exhaustive constructors; **no random seed**.
  Each completed target family is tested by exact GraphSet equality against
  an independent target family constructor. Small n=2,3 mixed cases also
  compare against explicit Cartesian-product composition oracles.
- **30 s bounded CI** with JSONL artifacts; local diagnostic runs below
  were bounded at 20–45 s per case. Construction excludes factor builds
  and final S projection, which are measured separately.

## Findings (observed)

### A. Original n=8 anomaly, independent CI (R13/R15)

| Input families | Final distinct T count | Constraint wall time | Peak RSS |
| --- | ---: | ---: | ---: |
| R,S all bijections | 40,320 | 7.5533 s | 803,812 KiB |
| R,S all total functions | 16,777,216 | 2.8897 s | 399,120 KiB |

Both completed cases passed exact target-family equality. This establishes
the performance asymmetry and argues against a wrong final answer.

### B. Row-boundary serialized nonterminal nodes, local diagnostic

| Completed R rows k | Bijections→bijections, n=8 | Functions→functions, n=8 |
| ---: | ---: | ---: |
| 1 | 9,216 | 8,006 |
| 2 | 29,696 | 9,022 |
| 3 | 58,368 | 10,038 |
| 4 | **72,704** | 11,054 |
| 5 | 58,368 | 12,070 |
| 6 | 29,696 | 13,086 |
| 7 | 9,216 | 14,102 |
| 8 | 2,048 | 15,118 |

For bijections, all measured row-boundary counts at n=5–8 fit the **empirical**
formula

\[
N(n,k)=n\,2^{n-1}\bigl(\binom nk+1\bigr).
\]

The measured coefficients \(n2^{n-1}\) are 80, 192, 448, 1,024 at
n=5,6,7,8. This exact numerical fit is not a theorem about ZDD size for
arbitrary n, orders, or algorithms. The n=8 total-function counts instead
grow linearly by 1,016 serialized nodes per completed row.

The instrumented local n=8 constraint times were **10.166 s** for
bijections and **3.625 s** for total functions; they must not be compared
as if they were cost-neutral replicas of the uninstrumented CI times.
Their process peak RSS was 804,948 vs 396,544 KiB.

### C. One-factor substitutions, local n=8 with node diagnostic

| R choices | S choices | T count | Constraint wall | Peak RSS |
| --- | --- | ---: | ---: | ---: |
| Bijections | Bijections | 40,320 | 10.166 s | 804,948 KiB |
| Bijections | **Identity only** | 40,320 | **0.080 s** | 26,388 KiB |
| **Identity only** | Bijections | 40,320 | 2.113 s | 162,372 KiB |
| **Total functions** | Bijections | 16,777,216 | **0.452 s** | 69,156 KiB |
| Bijections | **Total functions** | 16,777,216 | **25.437 s** | 1,586,204 KiB |

All five completed and passed independently built exact target-family
equality. Bijection/identity has the same 40,320 outputs as the expensive
bijection/bijection case but is about 127× faster in these instrumented
local runs. Replacing the *R* constraint with functions makes it fast;
replacing only the *S* constraint with functions makes it substantially
slower. The order of constraint types matters.

## Interpretation and significance

**Correctness:** An output-count bug is not supported by these tests:
completed n=8 controls passed exact family equality, and explicit smaller
controls validate composition semantics. This does not constitute a proof
that every internal state is optimal or every input is correct.

**Mechanism:** Bijections require each source row to choose a distinct
middle element. After k rows the surviving constraints depend on which
k-element subset of B has been used. The \(\binom nk\)-shaped **retained
node count** is precisely the pattern this hypothesis predicts. Unknown,
shared S couples those choices to target rows; fixing S to identity
removes most of that cost. This is evidence for a representation-cost
mechanism, not a complete derivation of the Graphillion serialization
coefficient.

**Practical consequence:** A plan selector must consider cross-row
constraints, relation ordering, and how long shared variables survive.
Neither final cardinality nor source-family cardinality selects a good
composition plan. The first R9–R11 composition cliff and this new
asymmetry are different examples of expensive intermediates despite
cheap final families.

## Alternative explanations and limits

- Row-boundary reachable-node counts are **not** transient peaks.
  Peak RSS also includes allocation, graph operations, and the Python
  process; the 72,704 retained nodes do not alone explain ~786 MiB.
- `setset.dumps()` node parsing is backend-specific and may perturb time
  and memory. A lower-level operation-level node counter is still needed.
- Each timing is one process; paired repetitions and CI replication of the
  new substitutions remain outstanding. Original anomaly has independent CI.
- `as-is` signature-major ordering can make semantically trivial copies
  across R/S/T expensive; identity→bijection costing 2.11 s is a warning.
- The empirical formula is an observation at n=5–8, not an asymptotic
  complexity classification.

## Next discriminating experiment

Reproduce the row traces and asymmetric controls through a dedicated
bounded [GitHub Actions workflow](../.github/workflows/composition-bijection-diagnostics.yml).
Then compare a different elimination schedule/atom order and measure **peak
operation-level** DD nodes. A true graph-state mechanism should persist
qualitatively but respond to compilation scheduling; an instrumentation
artifact would not.

## Reproduction and evidence

From the repository root after `pip install -e '.[dev]'`:

```bash
python experiments/composition_graft.py --n 8 --family bijections --algorithm row-graft --zdd-nodes --output /tmp/bij8.jsonl
python experiments/composition_graft.py --n 8 --family total-functions --algorithm row-graft --zdd-nodes --output /tmp/fun8.jsonl
python experiments/composition_graft.py --n 8 --family bijection-identity --algorithm row-graft --zdd-nodes --output /tmp/bij-identity8.jsonl
python experiments/composition_graft.py --n 8 --family identity-bijection --algorithm row-graft --zdd-nodes --output /tmp/identity-bij8.jsonl
python experiments/composition_graft.py --n 8 --family function-bijection --algorithm row-graft --zdd-nodes --output /tmp/fun-bij8.jsonl
python experiments/composition_graft.py --n 8 --family bijection-function --algorithm row-graft --zdd-nodes --output /tmp/bij-fun8.jsonl
```

- Code: [row-graft composer](../src/searillion/workspace.py),
  [instrumented runner](../experiments/composition_graft.py).
- Oracles: [composition tests](../tests/test_workspace.py),
  [benchmark smoke tests](../tests/test_composition_benchmark.py).
- Frozen uninstrumented CI measurements:
  [R13 run](https://github.com/cohereworks/searillion/actions/runs/41882644698),
  [R15 raw artifacts](https://github.com/cohereworks/searillion/actions/runs/41885045040),
  [R15 derived JSONL](../experiments/results/r15-composition-families.jsonl).
- The diagnostic workflow will retain raw JSONL with row checkpoints and
  timeout classifications; add the first verified run link as an addendum.

## Corrections / addenda

None yet. CI results for the new row-node matrix are pending.
