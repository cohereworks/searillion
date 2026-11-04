from __future__ import annotations

import argparse
from importlib.metadata import version
from math import factorial
import platform
from pathlib import Path
import resource
import sys
import time

from searillion.measurement import Measurement, measure
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
    p.add_argument("--algorithm", choices=("filter", "graft", "row-graft"), required=True)
    p.add_argument("--family", choices=("total-functions", "bijections", "single-edge", "unrestricted"),
                   default="total-functions")
    p.add_argument("--zdd-nodes", action="store_true",
                   help="serialize intermediate ZDDs to count nodes (extra time/memory)")
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

    expected_source = {
        "total-functions": args.n ** args.n,
        "bijections": factorial(args.n),
        "single-edge": args.n ** 2,
        "unrestricted": 1 << (args.n ** 2),
    }[args.family]
    expected_target_count = {
        "total-functions": args.n ** args.n,
        "bijections": factorial(args.n),
        "single-edge": args.n ** 2 + (args.n > 1),
        "unrestricted": 1 << (args.n ** 2),
    }[args.family]

    def construct_family(signature):
        return {
            "total-functions": signature.functions,
            "bijections": signature.bijections,
            "single-edge": lambda: signature.exactly(1),
            "unrestricted": signature.all,
        }[args.family]()

    def target_oracle():
        if args.family == "single-edge":
            return t.exactly(1) | (t.explicit([[]]) if args.n > 1 else t.empty_family())
        return construct_family(t)

    encoding = {
        "encoding": "tagged_relation_edge_atoms",
        "atom_order": "signature-major/row-major",
        "traversal": "as-is",
        "atom_count": ws.atom_count,
        "input_family": args.family,
        "seed": None,  # Exhaustive deterministic family, no generator.
    }

    print(
        f"START n={args.n} algorithm={args.algorithm} family={args.family} atoms={ws.atom_count}",
        flush=True,
    )

    boxes = {}

    for name, sig in (("R", r), ("S", s)):
        row = measure(
            (f"build_{name}_functions" if args.family == "total-functions"
             else f"build_{name}_family"),
            lambda sig=sig, name=name: boxes.setdefault(name, construct_family(sig)) is not None,
            n=args.n,
            algorithm=args.algorithm,
            expected=expected_source,
            **encoding,
        )
        emit(args.output, row)

    builders = {
        "filter": ws._composition_joint,
        "graft": ws._composition_joint_graft,
        "row-graft": ws._composition_joint_graft_rows,
    }
    builder = builders[args.algorithm]

    last_wall = time.perf_counter()
    last_cpu = time.process_time()

    def on_row(row_index, graphset):
        nonlocal last_wall, last_cpu
        now_wall, now_cpu = time.perf_counter(), time.process_time()
        node_count = None
        if args.zdd_nodes:
            # Graphillion 2.1 setset serialization: one node per non-terminal
            # line, followed by '.'. Internal format; opt-in, not stable API.
            serialized = graphset._ss.dumps()
            lines = serialized.splitlines()
            node_count = 0 if lines[0] in ("B", "T") else len(lines) - 1
        emit(args.output, Measurement(
            name="finish_target_row_and_eliminate_r_row",
            wall_seconds=now_wall - last_wall,
            cpu_seconds=now_cpu - last_cpu,
            peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            python=sys.version.split()[0],
            platform=platform.platform(),
            graphillion=version("graphillion"),
            metadata={
                "algorithm": args.algorithm,
                "n": args.n,
                "row_index": row_index,
                "r_atoms_remaining": r.atom_count - row_index * len(b.elements),
                "zdd_nodes": node_count,
                "zdd_node_method": "setset.dumps" if args.zdd_nodes else None,
                **encoding,
            },
            result=True,
        ))
        last_wall, last_cpu = time.perf_counter(), time.process_time()

    constrain = measure(
        "build_composition_constraint_family",
        lambda: boxes.setdefault(
            "joint",
            (builder(boxes["R"], boxes["S"], t, on_row=on_row)
             if args.algorithm == "row-graft" else
             builder(boxes["R"], boxes["S"], t)),
        ) is not None,
        n=args.n,
        algorithm=args.algorithm,
        source_pairs=expected_source ** 2,
        **encoding,
    )
    emit(args.output, constrain)

    projection = measure(
        "project_composition_to_target",
        lambda: boxes.setdefault("T", boxes["joint"].project_to(t)) is not None,
        n=args.n,
        algorithm=args.algorithm,
        eliminated_atoms=(s.atom_count if args.algorithm == "row-graft"
                          else r.atom_count + s.atom_count),
        **encoding,
    )
    emit(args.output, projection)

    count = measure(
        "count_composed_family",
        lambda: boxes["T"].count(),
        n=args.n,
        algorithm=args.algorithm,
        expected=expected_target_count,
        **encoding,
    )
    assert count.result == expected_target_count
    emit(args.output, count)

    oracle = measure(
        ("verify_against_independent_target_function_family"
         if args.family == "total-functions" else
         "verify_against_independent_target_family"),
        lambda: boxes["T"]._graphset == target_oracle()._graphset,
        n=args.n,
        algorithm=args.algorithm,
        oracle="GraphSet exact equality vs independent target-family construction",
        **encoding,
    )
    assert oracle.result is True
    emit(args.output, oracle)


if __name__ == "__main__":
    main()
