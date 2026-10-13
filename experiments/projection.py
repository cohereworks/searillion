from __future__ import annotations

import argparse

from searillion.measurement import measure, write_jsonl
from searillion.relation import Carrier, RelationUniverse


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--forget", type=int, required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    u = RelationUniverse(Carrier("A", range(args.n)), Carrier("B", range(args.n)))
    family = u.bijections()
    pairs = list(u._pairs)[: args.forget]

    projected_box = {}
    projection = measure(
        "forget_relation_atoms",
        lambda: projected_box.setdefault("family", family.forget_many(pairs)) is not None,
        n=args.n,
        atoms=u.atom_count,
        forgotten=args.forget,
        source_family="bijections",
        source_count=family.count(),
    )
    count = measure(
        "count_projected_family",
        lambda: projected_box["family"].count(),
        n=args.n,
        atoms=u.atom_count,
        forgotten=args.forget,
        source_family="bijections",
    )

    rows = [projection, count]
    write_jsonl(args.output, rows)
    for row in rows:
        print(row.to_json())


if __name__ == "__main__":
    main()
