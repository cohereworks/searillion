from __future__ import annotations

from typing import Hashable, Iterable

from graphillion import GraphSet

from searillion.relation import (
    Carrier,
    RelationFamily,
    _claim_backend_universe,
    _require_backend_generation,
)


class RelationWorkspace:
    """Shared Graphillion compilation context for multiple typed relation spaces.

    Graphillion exposes one process-global universe. A workspace makes that
    explicit: relation signatures are declared first, then compiled together
    into one tagged edge universe with a stable variable order.
    """

    def __init__(self, *, traversal: str = "as-is"):
        self.traversal = traversal
        self._signatures: list[RelationSignature] = []
        self._by_name: dict[str, RelationSignature] = {}
        self._compiled = False
        self._generation: int | None = None
        self._edges: tuple[tuple[Hashable, Hashable], ...] = ()

    def relation(
        self,
        name: str,
        left: Carrier,
        right: Carrier,
        *,
        pair_order: str = "row-major",
    ) -> "RelationSignature":
        if self._compiled:
            raise RuntimeError("workspace is already compiled")
        if name in self._by_name:
            raise ValueError(f"duplicate relation signature: {name}")
        sig = RelationSignature(self, name, left, right, pair_order=pair_order)
        self._signatures.append(sig)
        self._by_name[name] = sig
        return sig

    def compile(
        self,
        atom_order: Iterable[tuple["RelationSignature", tuple]] | None = None,
    ) -> "RelationWorkspace":
        if self._compiled:
            self._require_active()
            return self
        if not self._signatures:
            raise ValueError("workspace must contain at least one relation signature")

        expected_edges = {
            edge
            for sig in self._signatures
            for edge in sig._edges
        }

        if atom_order is None:
            edges = [
                edge
                for sig in self._signatures
                for edge in sig._edges
            ]
        else:
            edges = []
            seen = set()
            for sig, pair in atom_order:
                if sig not in self._signatures:
                    raise ValueError("atom order contains a signature outside this workspace")
                edge = sig._encode_pair(pair)
                if edge in seen:
                    raise ValueError("atom order contains a duplicate atom")
                seen.add(edge)
                edges.append(edge)

            if seen != expected_edges:
                raise ValueError("atom order must contain every workspace atom exactly once")

        GraphSet.set_universe(edges, traversal=self.traversal)
        self._edges = tuple(edges)
        self._generation = _claim_backend_universe()
        self._compiled = True
        return self

    @property
    def signatures(self) -> tuple["RelationSignature", ...]:
        return tuple(self._signatures)

    @property
    def atom_count(self) -> int:
        return sum(sig.atom_count for sig in self._signatures)

    def _require_active(self) -> None:
        if not self._compiled or self._generation is None:
            raise RuntimeError("workspace has not been compiled")
        _require_backend_generation(self._generation)

    def _other_edges(self, signature: "RelationSignature"):
        return [
            edge
            for sig in self._signatures
            if sig is not signature
            for edge in sig._edges
        ]

    def product(self, *families: RelationFamily) -> "JointFamily":
        """Return the Cartesian product of families on disjoint signatures.

        Because signature atom slices are disjoint, Graphillion's family join
        (pairwise set union) is a one-to-one encoding of relation-choice tuples.
        """
        self._require_active()
        if not families:
            raise ValueError("at least one relation family is required")

        signatures: list[RelationSignature] = []
        seen: set[RelationSignature] = set()
        graphset: GraphSet | None = None

        for family in families:
            sig = family.universe
            if not isinstance(sig, RelationSignature) or sig.workspace is not self:
                raise ValueError("all families must belong to this workspace")
            if sig in seen:
                raise ValueError("joint product requires disjoint relation signatures")
            seen.add(sig)
            signatures.append(sig)
            sig._require_active()

            if graphset is None:
                graphset = family._graphset.copy()
            else:
                graphset = graphset.join(family._graphset)

        assert graphset is not None
        return JointFamily(self, tuple(signatures), graphset)

    def _validate_composition_inputs(
        self,
        r_family: RelationFamily,
        s_family: RelationFamily,
        target: "RelationSignature",
    ) -> tuple["RelationSignature", "RelationSignature"]:
        r, s = self._validate_composition_inputs(r_family, s_family, target)

        return r, s

    def _composition_joint(
        self,
        r_family: RelationFamily,
        s_family: RelationFamily,
        target: "RelationSignature",
    ) -> "JointFamily":
        """Build the constrained R,S,T family before existential projection."""
        self._require_active()

        r = r_family.universe
        s = s_family.universe

        if (
            not isinstance(r, RelationSignature)
            or not isinstance(s, RelationSignature)
            or not isinstance(target, RelationSignature)
            or r.workspace is not self
            or s.workspace is not self
            or target.workspace is not self
        ):
            raise ValueError("composition families and target must belong to this workspace")

        if r is s or r is target or s is target:
            raise ValueError("composition requires three distinct relation signatures")

        if r.right is not s.left:
            raise ValueError("composition middle carriers must be the same ambient carrier")
        if target.left is not r.left or target.right is not s.right:
            raise ValueError("target signature must have type R.left × S.right")

        # Every pair (R,S) begins with every possible candidate target T.
        joint = self.product(r_family, s_family, target.all())
        graphset = joint._graphset

        # Enforce T(a,c) iff there exists b with R(a,b) and S(b,c).
        for a in r.left.elements:
            for c_value in s.right.elements:
                t_edge = target._encode_pair((a, c_value))
                witness = GraphSet([])

                for b_value in r.right.elements:
                    witness |= (
                        graphset
                        .including(r._encode_pair((a, b_value)))
                        .including(s._encode_pair((b_value, c_value)))
                    )

                no_witness = graphset - witness
                graphset = (
                    witness.including(t_edge)
                    | no_witness.excluding(t_edge)
                )

        return JointFamily(self, (r, s, target), graphset)

    def _composition_joint_graft(
        self,
        r_family: RelationFamily,
        s_family: RelationFamily,
        target: "RelationSignature",
    ) -> "JointFamily":
        """Construct composition targets deterministically from R×S witnesses.

        Unlike _composition_joint(), this does not introduce P(T) and filter it
        afterward.  It begins with R×S and grafts a target atom onto exactly
        those assignments that have at least one middle-carrier witness.
        """
        r, s = self._validate_composition_inputs(r_family, s_family, target)

        joint = self.product(r_family, s_family)
        graphset = joint._graphset

        for a in r.left.elements:
            for c_value in s.right.elements:
                t_edge = target._encode_pair((a, c_value))
                witness = GraphSet([])

                for b_value in r.right.elements:
                    witness |= (
                        graphset
                        .including(r._encode_pair((a, b_value)))
                        .including(s._encode_pair((b_value, c_value)))
                    )

                no_witness = graphset - witness
                # Graphillion join is pairwise set union. Joining the witness
                # family with {{t_edge}} grafts the deterministic target atom
                # without introducing unconstrained T choices.
                witness_with_target = witness.join(GraphSet([[t_edge]]))
                graphset = no_witness | witness_with_target

        return JointFamily(self, (r, s, target), graphset)

    def compose(
        self,
        r_family: RelationFamily,
        s_family: RelationFamily,
        target: "RelationSignature",
    ) -> RelationFamily:
        """Return the exact family {S o R | R in r_family, S in s_family}.

        R must have type A×B, S must have type B×C, and target must have
        type A×C. Carrier identity is intentional: SEAR relation typing is
        ambient-set sensitive, so equal-looking but distinct carriers are not
        silently identified.
        """
        return self._composition_joint(r_family, s_family, target).project_to(target)


class JointFamily:
    """Family of simultaneous relation choices over disjoint signatures."""

    def __init__(
        self,
        workspace: RelationWorkspace,
        signatures: tuple["RelationSignature", ...],
        graphset: GraphSet,
    ):
        self.workspace = workspace
        self.signatures = signatures
        self._graphset = graphset

    def __len__(self) -> int:
        self.workspace._require_active()
        return len(self._graphset)

    def __bool__(self) -> bool:
        self.workspace._require_active()
        return bool(self._graphset)

    def count(self) -> int:
        self.workspace._require_active()
        return self._graphset.len()

    def assignments(self):
        """Yield joint members as {signature_name: relation} mappings."""
        self.workspace._require_active()
        by_name = {sig.name: sig for sig in self.signatures}

        for graph in self._graphset:
            buckets = {sig.name: set() for sig in self.signatures}
            for edge in graph:
                u, _v = edge
                name = u[1]
                sig = by_name[name]
                buckets[name].add(sig._decode_edge(edge))
            yield {
                name: frozenset(pairs)
                for name, pairs in buckets.items()
            }

    def project_to(self, signature: "RelationSignature") -> RelationFamily:
        """Existentially eliminate every atom outside one retained signature."""
        self.workspace._require_active()
        if signature not in self.signatures:
            raise ValueError("retained signature is not part of this joint family")

        graphset = self._graphset.copy()
        for sig in self.signatures:
            if sig is signature:
                continue
            for edge in sig._edges:
                absent = graphset.excluding(edge)
                positive_cofactor = graphset.quotient(GraphSet([[edge]]))
                graphset = absent | positive_cofactor

        return RelationFamily(signature, graphset)


class RelationSignature:
    def __init__(
        self,
        workspace: RelationWorkspace,
        name: str,
        left: Carrier,
        right: Carrier,
        *,
        pair_order: str,
    ):
        self.workspace = workspace
        self.name = name
        self.left = left
        self.right = right
        self.pair_order = pair_order

        if pair_order == "row-major":
            self._pairs = tuple((a, b) for a in left.elements for b in right.elements)
        elif pair_order == "column-major":
            self._pairs = tuple((a, b) for b in right.elements for a in left.elements)
        else:
            raise ValueError("pair_order must be 'row-major' or 'column-major'")

        self._edges = tuple(self._encode_pair(pair) for pair in self._pairs)

    @property
    def atom_count(self) -> int:
        return len(self._pairs)

    @property
    def relation_count(self) -> int:
        return 1 << self.atom_count

    def _require_active(self) -> None:
        self.workspace._require_active()

    def _tag(self, side: str, value: Hashable):
        return ("REL", self.name, side, value)

    def _encode_pair(self, pair):
        a, b = pair
        if a not in self.left.elements or b not in self.right.elements:
            raise KeyError(pair)
        return (self._tag("L", a), self._tag("R", b))

    def _decode_edge(self, edge):
        u, v = edge
        if u[2] == "L":
            return (u[3], v[3])
        return (v[3], u[3])

    def _local_space(self) -> GraphSet:
        self._require_active()
        other_edges = self.workspace._other_edges(self)
        if not other_edges:
            return GraphSet({})
        return GraphSet({"exclude": other_edges})

    def all(self) -> RelationFamily:
        return RelationFamily(self, self._local_space())

    def empty_family(self) -> RelationFamily:
        self._require_active()
        return RelationFamily(self, GraphSet([]))

    def explicit(self, relations: Iterable[Iterable[tuple]]) -> RelationFamily:
        self._require_active()
        graphs = [
            [self._encode_pair(pair) for pair in relation]
            for relation in relations
        ]
        return RelationFamily(self, GraphSet(graphs))

    def exactly(self, pair_count: int) -> RelationFamily:
        self._require_active()
        if pair_count < 0 or pair_count > self.atom_count:
            return self.empty_family()
        return RelationFamily(
            self,
            GraphSet.graphs(
                num_edges=pair_count,
                graphset=self._local_space(),
            ),
        )

    def functions(self) -> RelationFamily:
        self._require_active()
        dc = {self._tag("L", a): 1 for a in self.left.elements}
        return RelationFamily(
            self,
            GraphSet.graphs(
                degree_constraints=dc,
                graphset=self._local_space(),
            ),
        )

    def bijections(self) -> RelationFamily:
        self._require_active()
        if len(self.left.elements) != len(self.right.elements):
            return self.empty_family()

        dc = {self._tag("L", a): 1 for a in self.left.elements}
        dc.update({self._tag("R", b): 1 for b in self.right.elements})
        return RelationFamily(
            self,
            GraphSet.graphs(
                degree_constraints=dc,
                graphset=self._local_space(),
            ),
        )
