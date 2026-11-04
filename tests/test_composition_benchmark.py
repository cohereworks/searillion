"""Smoke tests for the executable measurement protocol, not just the composer."""

import json
from pathlib import Path
import subprocess
import sys

import pytest


@pytest.mark.parametrize(
    "case,expected",
    [
        ("bijection-function", 4),
        ("function-bijection", 4),
        ("bijection-identity", 2),
        ("identity-bijection", 2),
    ],
)
def test_mixed_family_benchmark_records_exact_oracle_and_row_nodes(
    tmp_path, case, expected
):
    output = tmp_path / "trace.jsonl"
    runner = Path(__file__).resolve().parents[1] / "experiments" / "composition_graft.py"
    subprocess.run(
        [
            sys.executable, str(runner),
            "--n", "2",
            "--algorithm", "row-graft",
            "--family", case,
            "--zdd-nodes",
            "--output", str(output),
        ],
        cwd=runner.parents[1],
        check=True,
        capture_output=True,
        text=True,
        timeout=20,
    )
    rows = [json.loads(line) for line in output.read_text().splitlines()]
    checkpoints = [row for row in rows if row["name"] == "finish_target_row_and_eliminate_r_row"]
    count = next(row for row in rows if row["name"] == "count_composed_family")
    oracle = next(row for row in rows if row["name"] == "verify_against_independent_target_family"
                  or row["name"] == "verify_against_independent_target_function_family")

    assert len(checkpoints) == 2
    assert all(row["metadata"]["zdd_nodes"] > 0 for row in checkpoints)
    assert count["result"] == expected
    assert oracle["result"] is True
    assert checkpoints[0]["metadata"]["r_family"] in ("bijections", "total-functions", "identity")
