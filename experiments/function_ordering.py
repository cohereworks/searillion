from __future__ import annotations

import argparse
from pathlib import Path

from searillion.measurement import measure
from searillion.relation import Carrier, RelationUniverse


def emit(path: str, row) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(row.to_json() + "\n")
    print(row.to_json(), flush=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--traversal", choices=("greedy", "bfs", "dfs", "as-is"), required=True)
    p.add_argument("--pair-order", choices=("row-major", "column-major"), required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    u = RelationUniverse(
        Carrier("A", range(args.n)),
        Carrier("B", range(args.n)),
        traversal=args.traversal,
        pair_order=args.pair_order,
    )
    print(
        f"START n={args.n} traversal={args.traversal} pair_order={args.pair_order}",
        flush=True,
    )
    row = measure(
        "build_function_family",
        lambda: u.functions().count(),
        n=args.n,
        atoms=u.atom_count,
        expected=args.n ** args.n,
        traversal=args.traversal,
        pair_order=args.pair_order,
    )
    assert row.result == args.n ** args.n
    emit(args.output, row)


if __name__ == "__main__":
    main()
