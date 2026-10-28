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

    def compile(self) -> "RelationWorkspace":
        if self._compiled:
            self._require_active()
            return self
        if not self._signatures:
            raise ValueError("workspace must contain at least one relation signature")

        edges: list[tuple[Hashable, Hashable]] = []
        for sig in self._signatures:
            edges.extend(sig._edges)

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
