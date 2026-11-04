# Searillion lab book

This is the **reader-facing experimental record**. Start here to learn what
we tested, why it matters, and how much confidence the evidence warrants.
The append-only [research ledger](RESEARCH.md) retains chronological
observations and corrections; [WORKPLAN](WORKPLAN.md) governs future work.
Source code, executable tests, raw JSONL, and CI logs remain the evidence.

## The question in one minute

Can a ZDD retain *whole families of possible relations* so compactly that
computing with the family is cheaper than listing its members? The answer
depends on more than how many relations there are. We are measuring:

**input constraint structure → atom ordering → construction/elimination
schedule → intermediate ZDD shape → time/memory → exact output.**

A timeout is a valid boundary observation, not a successful computation.
These findings describe the tested Graphillion backend/encodings, not all
possible ZDD implementations or exact SEAR axioms.

## Experiment register

| Entry | Question / importance | Present finding | Evidence / limitation |
| --- | --- | --- | --- |
| [L001](labbook/L001-bijection-composition.md) | **Why can n=8 bijections cost more than millions of functions?** Diagnoses the compiler's next frontier. | Row-boundary DD nodes follow a binomial pattern; factor substitutions isolate cross-row and shared-relation dependencies. | Exact output oracles; instrumented local controls; CI replication of the original anomaly (R15). Node count is internal/provisional. |
| [R1 → R2](RESEARCH.md#r2--ordering-reverses-the-apparent-function-family-knee) | Is the first total-function cliff intrinsic? | **No**: changing the order eliminates most of it. | CI-reproduced; original R1 observation retained. |
| [R5 → R6](RESEARCH.md#r5--graphillions-process-global-universe-requires-an-explicit-searillion-workspace) | Can independent Graphillion universes safely coexist? | **No**: generation guards prevent stale reuse; a shared workspace supports simultaneous signatures. | Regression tests; direct Graphillion clients remain outside the wrapper's safety guarantee. |
| [R9 → R13](RESEARCH.md#r13--github-actions-confirms-r12-row-elimination-becomes-default) | Is the n=5→6 composition cliff inherent to witness constraints? | **No**: early elimination moves the 30 s frontier to n=9→10. | Matched CI; exact family oracle; strong algorithmic result, not polynomial scaling. |
| [R14 → R15](RESEARCH.md#r15--structural-controls-replicated-in-ci-row-graft-is-not-uniformly-optimal) | Does early elimination dominate for other inputs? | **No**: sparse and bijective/unrestricted controls behave differently. | CI controls, some resource-bound; sparse small timing gap needs repetitions. |

Earlier R-series results predate the lab-book convention. Their historical
ledger entries and CI artifacts are linked here without rewriting frozen
evidence or pretending all have full modern methodology records.

## Reading and contributing

- [Lab-book protocol and required sections](labbook/PROTOCOL.md)
- [Audit reconciliation: R1, global universe, missing M1 provenance](labbook/AUDIT-2026-11-04.md)
- [Machine-readable experiment controls and outputs](experiments/)

New material experiments receive their own `labbook/LNNN-*.md` entry.
Keep a succinct R-series ledger pointer and link the lab entry from this
register. Distinguish observed measurements, proven semantic properties,
mechanistic hypotheses, and speculative consequences.
