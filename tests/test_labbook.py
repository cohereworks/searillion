"""Minimal guard against regressing to unframed benchmark-only research."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_SECTIONS = (
    "## Purpose and significance",
    "## Hypothesis and falsifiers",
    "## Method and controls",
    "## Findings (observed)",
    "## Interpretation and significance",
    "## Alternative explanations and limits",
    "## Next discriminating experiment",
    "## Reproduction and evidence",
)


def test_every_lab_experiment_has_all_interpretive_sections_and_is_indexed():
    entries = list((ROOT / "labbook").glob("L[0-9][0-9][0-9]-*.md"))
    assert entries, "lab book must contain at least one full experiment"
    index = (ROOT / "LABBOOK.md").read_text(encoding="utf-8")
    for entry in entries:
        content = entry.read_text(encoding="utf-8")
        assert entry.name in index, f"{entry.name} missing from LABBOOK index"
        for section in REQUIRED_SECTIONS:
            assert section in content, f"{entry.name} missing {section}"
