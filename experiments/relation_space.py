from __future__ import annotations

import argparse

from searillion.measurement import measure, write_jsonl
from searillion.relation import Carrier, RelationUniverse


def build_and_count(n_left: int, n_right: int):
    left = Carrier("A", range(n_left))
    right = Carrier("B", range(n_right))
    universe = RelationUniverse(left, right)
    family = universe.all()
    return {
        "atoms": universe.atom_count,
        "represented_relations": len(family),
        "expected_relations": 1 << universe.atom_count,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--left", type=int, default=4)
    p.add_argument("--right", type=int, default=4)
    p.add_argument("--output", default="artifacts/relation-space.jsonl")
    args = p.parse_args()

    row = measure(
        "all_binary_relations",
        lambda: build_and_count(args.left, args.right),
        left=args.left,
        right=args.right,
    )
    assert row.result["represented_relations"] == row.result["expected_relations"]
    write_jsonl(args.output, [row])
    print(row.to_json())


if __name__ == "__main__":
    main()
