# Experiment-record protocol

One question, one falsifiable experiment, one durable record. Experiment IDs
are stable; corrections are dated addenda, never silent historical rewrites.
Use this template for **each new material experiment**, successful or not.

## Required sections

1. **Purpose and significance.** Plain-language question; why the answer
   matters to the overall research map; which claim would change.
2. **Hypothesis and falsifiers.** Predict something measurable before running
   it, including controls and a result that would count against the hypothesis.
3. **Method.** Exact family constructors, carrier sizes, atom encoding/order,
   traversal, algorithm, elimination schedule, independent oracle, seed (or
   explicit deterministic/no seed), environment, version, resource bounds.
4. **Findings.** Observation table with sample IDs; build time separated from
   constraint/operation/projection/count/oracle time; wall/CPU, high-water RSS,
   node-count method and phase if available, exactness, completed/timeout/
   resource failure classification. Put raw JSONL and logs in artifacts.
5. **Interpretation and significance.** What is established, what mechanism
   the evidence supports, what previous claim is corrected, what a reader
   should infer, and what they **must not** infer. Separate measurements from
   hypotheses and library-specific effects.
6. **Alternative explanations and limits.** Include timing noise, ordering,
   transient vs retained nodes, allocator/GC effects, and oracle coverage when
   relevant. A correct family count alone is not an extensional oracle.
7. **Next discriminating experiment.** Choose an experiment whose possible
   outcomes would distinguish the remaining explanations.
8. **Reproduction and provenance.** Exact commands, Git commit, CI run IDs
   and raw artifact names, and links to relevant tests/code/ledger entries.

## Confidence labels

- **Exploratory**: local measurement, incomplete replication or diagnostics.
- **Reproduced**: same qualitative result on independent CI execution.
- **Exact output verified**: completed output compared with a defensible
  independent extensional or family-equality oracle.
- **Bounded**: explicit timeout/OOM/cap; no final claim of correctness.
- **Unresolved**: competing explanations not discriminated.

Labels may coexist (a reproduced performance result can still have an
unresolved mechanism). Do not infer model-wide conclusions from one runner.

## Reporting invariants

- Keep stable raw measurements alongside derived summaries; never overwrite
  an old dataset with an improved interpretation.
- State whether telemetry changes the measured runtime or memory. In
  particular, `setset.dumps()` per-row counts only serialized reachable
  nonterminal nodes *at checkpoints*, not transient peak allocation.
- Preserve resource-bound outcomes with the last reliable checkpoint.
- Do not flatten observations from separate CI jobs into paired measurements.
- Every optimization that relies on a structure assumption must be checked
  against nonconforming controls.

## Copyable entry scaffold

```markdown
# LNNN — [question] (date; status)

## Purpose and significance
## Hypothesis and falsifiers
## Method and controls
## Findings (observed)
## Interpretation and significance
## Alternative explanations and limits
## Next discriminating experiment
## Reproduction and evidence
## Corrections / addenda
```
