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
    ws.compile()

    print(f"START n={args.n} atoms={ws.atom_count}", flush=True)

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

    build_joint = measure(
        "build_joint_product",
        lambda: boxes.setdefault("joint", ws.product(boxes["R"], boxes["S"])) is not None,
        n=args.n,
        expected=args.n ** (2 * args.n),
    )
    emit(args.output, build_joint)

    projection = measure(
        "project_joint_to_R",
        lambda: boxes.setdefault("projected", boxes["joint"].project_to(r)) is not None,
        n=args.n,
        eliminated_atoms=s.atom_count,
        expected=args.n ** args.n,
    )
    emit(args.output, projection)

    count_projection = measure(
        "count_projected_R",
        lambda: boxes["projected"].count(),
        n=args.n,
        expected=args.n ** args.n,
    )
    assert count_projection.result == args.n ** args.n
    emit(args.output, count_projection)


if __name__ == "__main__":
    main()
