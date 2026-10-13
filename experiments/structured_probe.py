from __future__ import annotations

import argparse
from math import factorial
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
    p.add_argument("--kind", choices=("function", "bijection"), required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    u = RelationUniverse(Carrier("A", range(args.n)), Carrier("B", range(args.n)))
    print(f"START kind={args.kind} n={args.n} atoms={u.atom_count}", flush=True)

    box = {}
    if args.kind == "function":
        expected = args.n ** args.n
        builder = u.functions
        build_name = "build_function_family"
        count_name = "count_function_family"
    else:
        expected = factorial(args.n)
        builder = u.bijections
        build_name = "build_bijection_family"
        count_name = "count_bijection_family"

    built = measure(
        build_name,
        lambda: box.setdefault("family", builder()) is not None,
        n=args.n,
        atoms=u.atom_count,
        expected=expected,
    )
    emit(args.output, built)

    counted = measure(
        count_name,
        lambda: box["family"].count(),
        n=args.n,
        atoms=u.atom_count,
        expected=expected,
    )
    assert counted.result == expected
    emit(args.output, counted)


if __name__ == "__main__":
    main()
