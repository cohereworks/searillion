from __future__ import annotations

from graphillion import GraphSet

from searillion.measurement import measure, write_jsonl


def graphillion_smoke() -> dict[str, int]:
    # K4: six possible undirected edges.  GraphSet.graphs() constructs the
    # family satisfying edge-count constraints without enumerating members.
    universe = [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
    GraphSet.set_universe(universe)
    all_graphs = GraphSet({})
    two_edges = GraphSet.graphs(num_edges=2)
    three_edges = GraphSet.graphs(num_edges=3)
    return {
        "universe_edges": len(universe),
        "all_graphs": len(all_graphs),
        "two_edges": len(two_edges),
        "three_edges": len(three_edges),
        "union": len(two_edges | three_edges),
        "intersection": len(two_edges & three_edges),
    }


def main() -> None:
    row = measure("graphillion_smoke", graphillion_smoke)
    # Exact combinatorial oracle over six edge variables.
    assert row.result["all_graphs"] == 64
    assert row.result["two_edges"] == 15
    assert row.result["three_edges"] == 20
    assert row.result["union"] == 35
    assert row.result["intersection"] == 0
    write_jsonl("artifacts/graphillion-smoke.jsonl", [row])
    print(row.to_json())


if __name__ == "__main__":
    main()
