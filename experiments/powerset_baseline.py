from __future__ import annotations

import argparse
from math import comb

from searillion.measurement import measure, write_jsonl


def brute_force_count(n: int, k: int) -> int:
    return sum(1 for mask in range(1 << n) if mask.bit_count() <= k)


def combinatorial_count(n: int, k: int) -> int:
    return sum(comb(n, i) for i in range(k + 1))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=16)
    p.add_argument("--k", type=int, default=4)
    p.add_argument("--output", default="artifacts/powerset-baseline.jsonl")
    args = p.parse_args()

    rows = [
        measure(
            "brute_force_count",
            lambda: brute_force_count(args.n, args.k),
            n=args.n,
            k=args.k,
            represented_family="subsets with cardinality <= k",
        ),
        measure(
            "combinatorial_count",
            lambda: combinatorial_count(args.n, args.k),
            n=args.n,
            k=args.k,
            represented_family="subsets with cardinality <= k",
        ),
    ]
    assert rows[0].result == rows[1].result
    write_jsonl(args.output, rows)
    for row in rows:
        print(row.to_json())


if __name__ == "__main__":
    main()
