# Searillion

**SEAR over ZDDs: a research engine for representing and manipulating enormous structured families of sets, relations, equivalences, logical forms, and paths without explicit enumeration—and mapping exactly where that compression stops paying.**

Searillion is an experimental research project investigating whether finite fragments of SEAR can provide a natural semantic surface over ZDD-backed families of subsets, initially using Graphillion.

The project is deliberately two-sided:

1. **Exploit the win zone.** Identify problems where a compact decision-diagram representation lets us retain, transform, count, project, compose, or constrain families that are infeasible to enumerate directly.
2. **Map the failure frontier.** Construct adversarial cases and measure where ZDD size, variable ordering, projection, composition, or representation churn recover the exponential cost.

## Core hypothesis

A large class of finite combinatorial problems can be represented as structured families of subsets of a suitably chosen universe. SEAR gives a compact language for sets, elements, and relations; ZDDs may give a compact executable representation when those families contain sufficient repeated structure.

This is **not** a claim that exponential complexity disappears. The central empirical question is where complexity migrates and when the resulting representation is practically advantageous.

## Initial research directions

- finite SEAR representation over Graphillion/ZDDs;
- power-set and constrained-family baselines;
- relational composition and projection;
- equivalence relations and quotients;
- logical canonicalization and derivation-family compression;
- software execution-path families;
- neural-network path/activation families where discretization and sparsity make the problem suitable;
- constrained symbolic/text encodings;
- adversarial constructions designed to force decision-diagram blow-up.

## Research posture

- Explicit baselines beside every symbolic result.
- Wall time, CPU time, memory, decision-diagram size, ordering, and environment captured where possible.
- Negative results are first-class results.
- Claims graduate only when reproducible.
- Frozen experimental evidence is not rewritten to improve the narrative.
- Repository-local plans and evidence are canonical.

## Status

Very early pre-release research. No public API stability is implied.

## License

No license has been selected yet.
