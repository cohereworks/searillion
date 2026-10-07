from __future__ import annotations

import argparse
from math import factorial

from searillion.measurement import measure, write_jsonl
from searillion.relation import Carrier, RelationUniverse


def build_universe(n: int) -> RelationUniverse[int, int]:
    return RelationUniverse(Carrier("A", range(n)), Carrier("B", range(n)))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    u = build_universe(args.n)

    function_box = {}
    build_functions = measure(
        "build_function_family",
        lambda: function_box.setdefault("family", u.functions()) is not None,
        n=args.n,
        atoms=u.atom_count,
        expected=args.n ** args.n,
    )
    count_functions = measure(
        "count_function_family",
        lambda: function_box["family"].count(),
        n=args.n,
        atoms=u.atom_count,
        expected=args.n ** args.n,
    )
    assert count_functions.result == args.n ** args.n

    bijection_box = {}
    build_bijections = measure(
        "build_bijection_family",
        lambda: bijection_box.setdefault("family", u.bijections()) is not None,
        n=args.n,
        atoms=u.atom_count,
        expected=factorial(args.n),
    )
    count_bijections = measure(
        "count_bijection_family",
        lambda: bijection_box["family"].count(),
        n=args.n,
        atoms=u.atom_count,
        expected=factorial(args.n),
    )
    assert count_bijections.result == factorial(args.n)

    rows = [
        build_functions,
        count_functions,
        build_bijections,
        count_bijections,
    ]
    write_jsonl(args.output, rows)
    for row in rows:
        print(row.to_json())


if __name__ == "__main__":
    main()
