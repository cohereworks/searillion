from __future__ import annotations

import argparse
from pathlib import Path

from searillion.measurement import measure
from searillion.relation import Carrier
from searillion.workspace import RelationWorkspace


def emit(path: str, row) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(row.to_json() + "\n")
    print(row.to_json(), flush=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    a = Carrier("A", range(args.n))
    b = Carrier("B", range(args.n))
    c = Carrier("C", range(args.n))

    ws = RelationWorkspace(traversal="as-is")
    r = ws.relation("R", a, b, pair_order="row-major")
    s = ws.relation("S", b, c, pair_order="row-major")
    t = ws.relation("T", a, c, pair_order="row-major")
    ws.compile()

    print(
        f"START n={args.n} atoms={ws.atom_count} expected_compositions={args.n ** args.n}",
        flush=True,
    )

    boxes = {}

    build_r = measure(
        "build_R_functions",
        lambda: boxes.setdefault("R", r.functions()) is not None,
        n=args.n,
        expected=args.n ** args.n,
    )
    emit(args.output, build_r)

    build_s = measure(
        "build_S_functions",
        lambda: boxes.setdefault("S", s.functions()) is not None,
        n=args.n,
        expected=args.n ** args.n,
    )
    emit(args.output, build_s)

    constrain = measure(
        "build_composition_constraint_family",
        lambda: boxes.setdefault(
            "joint",
            ws._composition_joint(boxes["R"], boxes["S"], t),
        ) is not None,
        n=args.n,
        source_pairs=args.n ** (2 * args.n),
        expected_distinct_results=args.n ** args.n,
    )
    emit(args.output, constrain)

    projection = measure(
        "project_composition_to_target",
        lambda: boxes.setdefault(
            "T",
            boxes["joint"].project_to(t),
        ) is not None,
        n=args.n,
        eliminated_atoms=r.atom_count + s.atom_count,
        expected_distinct_results=args.n ** args.n,
    )
    emit(args.output, projection)

    count = measure(
        "count_composed_family",
        lambda: boxes["T"].count(),
        n=args.n,
        expected=args.n ** args.n,
    )
    assert count.result == args.n ** args.n
    emit(args.output, count)


if __name__ == "__main__":
    main()
