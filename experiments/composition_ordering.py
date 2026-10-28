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


def atom_order(strategy, r, s, t):
    if strategy == "signature-major":
        return None

    order = []
    seen = set()

    def add(sig, pair):
        key = (sig, pair)
        if key not in seen:
            seen.add(key)
            order.append(key)

    if strategy == "row-block-rst":
        for i in range(len(r.left.elements)):
            a = r.left.elements[i]
            b_row = s.left.elements[i]
            for b in r.right.elements:
                add(r, (a, b))
            for c in s.right.elements:
                add(s, (b_row, c))
            for c in t.right.elements:
                add(t, (a, c))

    elif strategy == "witness-first":
        for a in r.left.elements:
            for c in s.right.elements:
                for b in r.right.elements:
                    add(r, (a, b))
                    add(s, (b, c))
                add(t, (a, c))

    elif strategy == "target-first":
        for a in r.left.elements:
            for c in s.right.elements:
                add(t, (a, c))
                for b in r.right.elements:
                    add(r, (a, b))
                    add(s, (b, c))

    elif strategy == "middle-first":
        for b in r.right.elements:
            for a in r.left.elements:
                add(r, (a, b))
            for c in s.right.elements:
                add(s, (b, c))
        for pair in t._pairs:
            add(t, pair)

    else:
        raise ValueError(strategy)

    # First-touch strategies can intentionally defer atoms, but must never omit.
    for sig in (r, s, t):
        for pair in sig._pairs:
            add(sig, pair)

    return order


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, required=True)
    p.add_argument(
        "--strategy",
        choices=(
            "signature-major",
            "row-block-rst",
            "witness-first",
            "target-first",
            "middle-first",
        ),
        required=True,
    )
    p.add_argument("--output", required=True)
    args = p.parse_args()

    a = Carrier("A", range(args.n))
    b = Carrier("B", range(args.n))
    c = Carrier("C", range(args.n))

    ws = RelationWorkspace(traversal="as-is")
    r = ws.relation("R", a, b, pair_order="row-major")
    s = ws.relation("S", b, c, pair_order="row-major")
    t = ws.relation("T", a, c, pair_order="row-major")
    ws.compile(atom_order=atom_order(args.strategy, r, s, t))

    print(
        f"START n={args.n} strategy={args.strategy} atoms={ws.atom_count}",
        flush=True,
    )

    boxes = {}

    build_r = measure(
        "build_R_functions",
        lambda: boxes.setdefault("R", r.functions()) is not None,
        n=args.n,
        strategy=args.strategy,
        expected=args.n ** args.n,
    )
    emit(args.output, build_r)

    build_s = measure(
        "build_S_functions",
        lambda: boxes.setdefault("S", s.functions()) is not None,
        n=args.n,
        strategy=args.strategy,
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
        strategy=args.strategy,
        source_pairs=args.n ** (2 * args.n),
    )
    emit(args.output, constrain)

    projection = measure(
        "project_composition_to_target",
        lambda: boxes.setdefault("T", boxes["joint"].project_to(t)) is not None,
        n=args.n,
        strategy=args.strategy,
        eliminated_atoms=r.atom_count + s.atom_count,
    )
    emit(args.output, projection)

    count = measure(
        "count_composed_family",
        lambda: boxes["T"].count(),
        n=args.n,
        strategy=args.strategy,
        expected=args.n ** args.n,
    )
    assert count.result == args.n ** args.n
    emit(args.output, count)


if __name__ == "__main__":
    main()
