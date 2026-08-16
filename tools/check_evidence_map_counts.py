#!/usr/bin/env python3
"""Check that corpus distribution tables agree with the canonical CSV."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


PAPER_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = PAPER_ROOT.parent
DB = PROJECT_ROOT / "db" / "papers.csv"

LEVEL_ORDER = [
    "L0 static prediction",
    "L1 future prediction",
    "L2 action-conditioned simulation",
    "L3 counterfactual reasoning",
    "L4 planning/control",
]


def read_rows() -> list[dict[str, str]]:
    with DB.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def assert_table_values(path: Path, counts: Counter[str], labels: list[str]) -> None:
    source = path.read_text(encoding="utf-8")
    total = sum(counts[label] for label in labels)
    for label in labels:
        count = counts[label]
        percent = 100.0 * count / total
        token = f"& {count} & {percent:.1f} &"
        if token not in source:
            raise AssertionError(f"{path.name}: missing current token {token!r} for {label}")


def main() -> None:
    rows = read_rows()
    if len(rows) != 247:
        raise AssertionError(f"expected 247 rows, found {len(rows)}")

    level_counts = Counter(row["capability_level"] for row in rows)
    assert_table_values(PAPER_ROOT / "table_levels.tex", level_counts, LEVEL_ORDER)

    track_counts = Counter(row["topic_track"] for row in rows)
    track_order = [
        "T1_definition_review_digital_twin",
        "T4_ehr_patient_trajectory",
        "T5_counterfactual_treatment_planning",
        "T6_surgical_robotic_physiology_world_model",
        "T7_background_methods",
        "T2_imaging_representation_world_model",
        "T3_longitudinal_disease_progression",
    ]
    assert_table_values(PAPER_ROOT / "table_tracks.tex", track_counts, track_order)

    print("PASS: Table 2 and Table 3 agree with db/papers.csv")
    print("levels:", [level_counts[label] for label in LEVEL_ORDER])
    print("tracks:", [track_counts[label] for label in track_order])


if __name__ == "__main__":
    main()
