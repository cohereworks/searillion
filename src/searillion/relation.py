from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Hashable, Iterable, Iterator, TypeVar

from graphillion import GraphSet

A = TypeVar("A", bound=Hashable)
B = TypeVar("B", bound=Hashable)


@dataclass(frozen=True)
class Carrier(Generic[A]):
    name: str
    elements: tuple[A, ...]

    def __init__(self, name: str, elements: Iterable[A]):
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "elements", tuple(elements))
        if len(set(self.elements)) != len(self.elements):
            raise ValueError("carrier elements must be unique")


class RelationUniverse(Generic[A, B]):
    """Finite binary-relation universe A×B encoded as a bipartite edge universe.

    Graphillion's GraphSet stores undirected edge subsets.  We avoid collapsing
    (a,b) with any other semantic pair by tagging the left and right endpoints.
    Each relation R⊆A×B is therefore represented by one subgraph of the complete
    tagged bipartite graph.
    """

    def __init__(self, left: Carrier[A], right: Carrier[B]):
        self.left = left
        self.right = right
        self._pairs = tuple((a, b) for a in left.elements for b in right.elements)
        self._edges = tuple(self._encode_pair(p) for p in self._pairs)
        GraphSet.set_universe(list(self._edges))

    @staticmethod
    def _tag(side: str, value: Hashable) -> tuple[str, Hashable]:
        return (side, value)

    def _encode_pair(self, pair: tuple[A, B]):
        a, b = pair
        if a not in self.left.elements or b not in self.right.elements:
            raise KeyError(pair)
        return (self._tag("L", a), self._tag("R", b))

    def _decode_edge(self, edge):
        u, v = edge
        if u[0] == "L":
            return (u[1], v[1])
        return (v[1], u[1])

    @property
    def atom_count(self) -> int:
        return len(self._pairs)

    @property
    def relation_count(self) -> int:
        return 1 << self.atom_count

    def all(self) -> "RelationFamily[A, B]":
        return RelationFamily(self, GraphSet({}))

    def empty_family(self) -> "RelationFamily[A, B]":
        return RelationFamily(self, GraphSet([]))

    def explicit(
        self, relations: Iterable[Iterable[tuple[A, B]]]
    ) -> "RelationFamily[A, B]":
        graphs = [
            [self._encode_pair(pair) for pair in relation]
            for relation in relations
        ]
        return RelationFamily(self, GraphSet(graphs))

    def exactly(self, pair_count: int) -> "RelationFamily[A, B]":
        if pair_count < 0 or pair_count > self.atom_count:
            return self.empty_family()
        return RelationFamily(self, GraphSet.graphs(num_edges=pair_count))


class RelationFamily(Generic[A, B]):
    def __init__(self, universe: RelationUniverse[A, B], graphset: GraphSet):
        self.universe = universe
        self._graphset = graphset

    def __len__(self) -> int:
        # Python's __len__ is limited to Py_ssize_t. Preserve normal semantics
        # for small families and direct callers to count() for astronomical ones.
        return len(self._graphset)

    def count(self) -> int:
        """Return the exact family cardinality using Graphillion's big-int path."""
        return self._graphset.len()

    def __bool__(self) -> bool:
        return bool(self._graphset)

    def __or__(self, other: "RelationFamily[A, B]") -> "RelationFamily[A, B]":
        self._require_same_universe(other)
        return RelationFamily(self.universe, self._graphset | other._graphset)

    def __and__(self, other: "RelationFamily[A, B]") -> "RelationFamily[A, B]":
        self._require_same_universe(other)
        return RelationFamily(self.universe, self._graphset & other._graphset)

    def __sub__(self, other: "RelationFamily[A, B]") -> "RelationFamily[A, B]":
        self._require_same_universe(other)
        return RelationFamily(self.universe, self._graphset - other._graphset)

    def including(self, pair: tuple[A, B]) -> "RelationFamily[A, B]":
        edge = self.universe._encode_pair(pair)
        return RelationFamily(self.universe, self._graphset.including(edge))

    def excluding(self, pair: tuple[A, B]) -> "RelationFamily[A, B]":
        edge = self.universe._encode_pair(pair)
        return RelationFamily(self.universe, self._graphset.excluding(edge))

    def relations(self) -> Iterator[frozenset[tuple[A, B]]]:
        for graph in self._graphset:
            yield frozenset(self.universe._decode_edge(edge) for edge in graph)

    def _require_same_universe(self, other: "RelationFamily[A, B]") -> None:
        if self.universe is not other.universe:
            raise ValueError("relation families belong to different universes")
