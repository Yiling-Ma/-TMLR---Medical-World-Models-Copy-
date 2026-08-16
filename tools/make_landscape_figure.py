#!/usr/bin/env python3
"""Regenerate the audited capability-by-clinical-setting landscape figure."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np


PAPER_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = PAPER_ROOT.parent
DEFAULT_DB = PROJECT_ROOT / "audits" / "fulltext_20260717" / "all_papers_audit_master.csv"
DEFAULT_OUT = PAPER_ROOT / "figures" / "fig_landscape.pdf"

INK = "#1A2A3A"
BLUE = "#0072B2"
GRAY = "#6E7B8B"
GRID = "#DDE3E8"
PALE = "#F0F5FA"

LEVELS = ["L0", "L1", "L2", "L3", "L4"]
NONCLINICAL_SETTINGS = {"general_world_model_context", "biomedical_cellular_context"}
SETTINGS = [
    ("Imaging", "medical_imaging_representation"),
    ("Longitudinal", "longitudinal_disease_progression"),
    ("EHR", "ehr_patient_trajectory"),
    ("Digital twin", "digital_twin"),
    ("Treatment /\ncausal", "counterfactual_treatment_planning"),
    ("Population\nhealth", "population_health_policy_simulation"),
    ("Surgery /\nphysiology", "surgical_robotic_physiology"),
    ("Other medical", "other_medical"),
]
DISEASE_LABEL = {
    "not_disease_specific": "Not disease-specific",
    "general_or_multidisease": "General / multi-disease",
    "oncology": "Oncology",
    "critical_illness": "Critical illness",
    "cardiovascular_disease": "Cardiovascular",
    "neurologic_disease": "Neurologic",
    "metabolic_endocrine_disease": "Metab. / endocrine",
    "respiratory_disease": "Respiratory",
    "musculoskeletal_disease": "Musculoskeletal",
    "infectious_disease": "Infectious",
    "renal_urologic_disease": "Renal / urologic",
    "ophthalmic_disease": "Ophthalmic",
    "psychiatric_behavioral_disease": "Psychiatric / behavioral",
    "reproductive_obstetric_disease": "Reproductive / obstetric",
    "not_applicable": "N/A",
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def is_canonical_work_record(row: dict[str, str]) -> bool:
    return not row.get("duplicate_of") and row.get("record_status") != "duplicate_version"


def build_figure(rows: list[dict[str, str]], output: Path) -> None:
    rows = [
        row for row in rows
        if is_canonical_work_record(row)
        and row.get("adjudication_status") == "dual_review_complete"
        and row.get("implemented_level") in LEVELS
        and row.get("clinical_setting_primary") not in NONCLINICAL_SETTINGS
    ]
    if not rows:
        raise ValueError("no dual-reviewed implemented medical records found")
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.size": 8,
            "axes.titlesize": 9.2,
            "axes.labelsize": 8,
            "xtick.labelsize": 7.2,
            "ytick.labelsize": 7.2,
            "text.color": INK,
            "axes.labelcolor": INK,
            "axes.edgecolor": INK,
            "xtick.color": INK,
            "ytick.color": INK,
            "pdf.fonttype": 42,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.02,
        }
    )

    matrix = np.array(
        [
            [
                sum(
                    row["clinical_setting_primary"] == setting_field
                    and row["implemented_level"] == level
                    for row in rows
                )
                for level in LEVELS
            ]
            for _, setting_field in SETTINGS
        ]
    )
    level_totals = matrix.sum(axis=0)
    if int(level_totals.sum()) != len(rows):
        raise ValueError("clinical-setting x level matrix does not sum to the filtered record count")

    disease_counts = Counter(row["disease_family_primary"] for row in rows)
    domains = sorted(
        ((DISEASE_LABEL.get(key, key.replace("_", " ").title()), value) for key, value in disease_counts.items()),
        key=lambda item: item[1],
        reverse=True,
    )
    disease_total = sum(value for _, value in domains)

    fig = plt.figure(figsize=(7.0, 3.0))
    grid = fig.add_gridspec(1, 2, width_ratios=[1.18, 1.0], wspace=0.72)

    ax_h = fig.add_subplot(grid[0, 0])
    cmap = LinearSegmentedColormap.from_list("mwm_blue", [PALE, "#8DC5E4", BLUE])
    ax_h.imshow(matrix, cmap=cmap, aspect="auto", vmin=0, vmax=matrix.max())
    ax_h.set_xticks(range(len(LEVELS)))
    ax_h.set_xticklabels([f"{level}\n$n={total}$" for level, total in zip(LEVELS, level_totals)])
    ax_h.set_yticks(range(len(SETTINGS)))
    ax_h.set_yticklabels([label for label, _ in SETTINGS])
    for row_index in range(matrix.shape[0]):
        for col_index in range(matrix.shape[1]):
            value = int(matrix[row_index, col_index])
            text_color = "white" if value >= matrix.max() * 0.55 else INK
            ax_h.text(col_index, row_index, str(value), ha="center", va="center", color=text_color)
    ax_h.set_title("(a) Clinical setting $\\times$ capability", loc="left", pad=7)
    ax_h.tick_params(length=0)
    for spine in ax_h.spines.values():
        spine.set_visible(False)

    ax_d = fig.add_subplot(grid[0, 1])
    labels = [label for label, _ in domains]
    values = [value for _, value in domains]
    positions = np.arange(len(labels))[::-1]
    ax_d.barh(positions, values, color="#009E73", alpha=0.86, height=0.62, zorder=3)
    for position, value in zip(positions, values):
        share = 100.0 * value / disease_total
        ax_d.text(value + 2.0, position, f"{value}  ({share:.1f}%)", va="center", fontsize=6.8)
    ax_d.set_yticks(positions)
    ax_d.set_yticklabels(labels)
    ax_d.tick_params(axis="y", labelsize=6.4, pad=2)
    ax_d.set_xlim(0, max(values) * 1.30)
    ax_d.set_xlabel(f"canonical works (total={disease_total})")
    ax_d.set_title("(b) Primary disease family", loc="left", pad=7)
    ax_d.grid(axis="x", color=GRID, linewidth=0.7, zorder=0)
    ax_d.tick_params(length=0)
    ax_d.spines["top"].set_visible(False)
    ax_d.spines["right"].set_visible(False)
    ax_d.spines["left"].set_visible(False)

    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output)
    fig.savefig(output.with_suffix(".png"), dpi=220)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    rows = read_rows(args.db)
    build_figure(rows, args.out)
    print(f"wrote {args.out} from {args.db} ({len(rows)} records)")


if __name__ == "__main__":
    main()
