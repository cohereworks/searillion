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
    p.add_argument("--algorithm", choices=("filter", "graft"), required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    a = Carrier("A", range(args.n))
    b = Carrier("B", range(args.n))
    c = Carrier("C", range(args.n))

    ws = RelationWorkspace(traversal="as-is")
    r = ws.relation("R", a, b)
    s = ws.relation("S", b, c)
    t = ws.relation("T", a, c)
    ws.compile()

    print(
        f"START n={args.n} algorithm={args.algorithm} atoms={ws.atom_count}",
        flush=True,
    )

    boxes = {}

    for name, sig in (("R", r), ("S", s)):
        row = measure(
            f"build_{name}_functions",
            lambda sig=sig, name=name: boxes.setdefault(name, sig.functions()) is not None,
            n=args.n,
            algorithm=args.algorithm,
            expected=args.n ** args.n,
        )
        emit(args.output, row)

    builder = (
        ws._composition_joint
        if args.algorithm == "filter"
        else ws._composition_joint_graft
    )

    constrain = measure(
        "build_composition_constraint_family",
        lambda: boxes.setdefault(
            "joint",
            builder(boxes["R"], boxes["S"], t),
        ) is not None,
        n=args.n,
        algorithm=args.algorithm,
        source_pairs=args.n ** (2 * args.n),
    )
    emit(args.output, constrain)

    projection = measure(
        "project_composition_to_target",
        lambda: boxes.setdefault("T", boxes["joint"].project_to(t)) is not None,
        n=args.n,
        algorithm=args.algorithm,
        eliminated_atoms=r.atom_count + s.atom_count,
    )
    emit(args.output, projection)

    count = measure(
        "count_composed_family",
        lambda: boxes["T"].count(),
        n=args.n,
        algorithm=args.algorithm,
        expected=args.n ** args.n,
    )
    assert count.result == args.n ** args.n
    emit(args.output, count)


if __name__ == "__main__":
    main()
