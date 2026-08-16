#!/usr/bin/env python3
"""Generate manuscript counts and audit tables from the adjudicated master CSV."""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path


PAPER = Path(__file__).resolve().parents[1]
PROJECT = PAPER.parent
MASTER = PROJECT / "audits" / "fulltext_20260717" / "all_papers_audit_master.csv"
LEVELS = ("L0", "L1", "L2", "L3", "L4")
NONCLINICAL_SETTINGS = {"general_world_model_context", "biomedical_cellular_context"}
REPRESENTATIVE_IDS = (
    "MWM0003", "MWM0136",
    "MWM0161", "MWM0307",
    "MWM0015", "MWM0077",
    "MWM0150", "MWM0152",
    "MWM0013", "MWM0014",
    "MWM0011", "MWM0306",
)
TRACK_WORK_IDS = {
    "medical_imaging_representation": ("MWM0003", "MWM0004", "MWM0161"),
    "longitudinal_disease_progression": ("MWM0307", "MWM0077", "MWM0079"),
    "ehr_patient_trajectory": ("MWM0008", "MWM0009", "MWM0010"),
    "digital_twin": ("MWM0129", "MWM0131", "MWM0132"),
    "counterfactual_treatment_planning": ("MWM0014", "MWM0146", "MWM0150"),
    "surgical_robotic_physiology": ("MWM0015", "MWM0018", "MWM0023"),
}
SETTING_SHORT = {
    "medical_imaging_representation": "medical imaging",
    "longitudinal_disease_progression": "longitudinal progression",
    "ehr_patient_trajectory": "EHR trajectory",
    "digital_twin": "digital twin",
    "counterfactual_treatment_planning": "treatment/causal",
    "population_health_policy_simulation": "population health policy",
    "surgical_robotic_physiology": "surgery/robotics",
    "review_definition_context": "review context",
    "general_world_model_context": "general context",
    "other_medical": "other medical",
}
SETTING_DISPLAY = {
    "medical_imaging_representation": "Medical imaging",
    "longitudinal_disease_progression": "Longitudinal progression",
    "ehr_patient_trajectory": "EHR trajectories",
    "digital_twin": "Digital twins",
    "counterfactual_treatment_planning": "Treatment and causal modeling",
    "population_health_policy_simulation": "Population-health policy simulation",
    "surgical_robotic_physiology": "Surgery, robotics, and physiology",
}


def read() -> list[dict[str, str]]:
    with MASTER.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
        "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
    }
    return "".join(replacements.get(char, char) for char in value)


def short(value: str, words: int = 18) -> str:
    tokens = value.split()
    return " ".join(tokens[:words]) + (" ..." if len(tokens) > words else "")


def percent(count: int, total: int) -> float:
    return 100 * count / total if total else 0.0


def is_canonical_work_record(row: dict[str, str]) -> bool:
    """Keep version records for provenance while counting each work once."""
    return not row.get("duplicate_of") and row.get("record_status") != "duplicate_version"


def code_group(status: str) -> str:
    status = status.lower()
    if status.startswith("not_applicable"):
        return "not_applicable"
    negative = (
        "not_found", "no_public", "unreleased", "not_released", "placeholder",
        "unavailable", "inaccessible", "claimed", "announced", "promises",
        "by_request", "proprietary", "pending", "broken", "no_paper_specific",
    )
    if any(token in status for token in negative):
        if any(token in status for token in ("claimed", "announced", "promises", "by_request", "pending")):
            return "claimed_or_pending"
        return "not_found_or_unreleased"
    positive = (
        "official_verified", "official_repository", "official_complete_public_code",
        "official_code", "official_framework_code", "official_multi_repository",
        "public_code", "repository_verified", "code_and_", "interactive_demos_and_code",
        "simulation_capsules_public", "official_model_and_checkpoints",
    )
    if any(token in status for token in positive):
        if any(token in status for token in ("partial", "no_weights", "base_weights_only")):
            return "public_partial_or_no_weights"
        return "public_verified"
    if any(token in status for token in ("partial", "component", "reused_public", "related_public")):
        return "public_partial_or_no_weights"
    return "not_found_or_unreleased"


def write_macros(rows: list[dict[str, str]]) -> None:
    audited = [row for row in rows if row["adjudication_status"] in {"dual_review_complete", "codex_complete"}]
    dual = [row for row in rows if row["adjudication_status"] == "dual_review_complete"]
    canonical = [row for row in rows if is_canonical_work_record(row)]
    audited_works = [
        row for row in canonical
        if row["adjudication_status"] in {"dual_review_complete", "codex_complete"}
    ]
    dual_works = [row for row in canonical if row["adjudication_status"] == "dual_review_complete"]
    codex_only_works = [row for row in canonical if row["adjudication_status"] == "codex_complete"]
    implemented = [row for row in dual_works if row["implemented_level"] in LEVELS]
    medical = [row for row in implemented if row["clinical_setting_primary"] not in NONCLINICAL_SETTINGS]
    levels = Counter(row["implemented_level"] for row in implemented)
    macros = {
        "CorpusTotal": len(rows),
        "CanonicalWorkTotal": len(canonical),
        "OriginalCorpusTotal": sum(row["corpus_partition"] == "original_frozen_247" for row in rows),
        "SupplementalCorpusTotal": sum(row["corpus_partition"] == "supplemental_living" for row in rows),
        "AuditedTotal": len(audited),
        "AuditedWorkTotal": len(audited_works),
        "DualReviewedTotal": len(dual),
        "DualReviewedWorkTotal": len(dual_works),
        "CodexOnlyWorkTotal": len(codex_only_works),
        "BlockedTotal": sum(row["adjudication_status"].startswith("blocked") for row in rows),
        "ImplementedTotal": len(implemented),
        "MedicalImplementedTotal": len(medical),
        **{
            f"NLevel{name}": levels[level]
            for level, name in zip(LEVELS, ("Zero", "One", "Two", "Three", "Four"))
        },
    }
    lines = ["% Generated by tools/build_audit_latex_assets.py. Do not hand edit."]
    lines.extend(f"\\newcommand{{\\{key}}}{{{value}}}" for key, value in macros.items())
    (PAPER / "audit_numbers.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_levels(rows: list[dict[str, str]]) -> None:
    dual = [
        row for row in rows
        if is_canonical_work_record(row) and row["adjudication_status"] == "dual_review_complete"
    ]
    implemented = [row for row in dual if row["implemented_level"] in LEVELS]
    counts = Counter(row["implemented_level"] for row in implemented)
    descriptions = {
        "L0": "Current-state representation, calibration, or same-time synthesis; no directed future target.",
        "L1": "Directed future state or observation without a settable action entering the transition.",
        "L2": "A settable action changes an evaluated, meaningful post-action future.",
        "L3": "Alternative-intervention outcomes are estimated with an explicit causal identification contract.",
        "L4": "A world model is operationally used to rank, select, optimize, or control actions or policies.",
    }
    names = {
        "L0": "current-state modeling", "L1": "future prediction",
        "L2": "action-conditioned simulation", "L3": "counterfactual outcome reasoning",
        "L4": "planning/control",
    }
    body = []
    for level in LEVELS:
        count = counts[level]
        body.append(
            f"{level} {names[level]} & {descriptions[level]} & {count} & {percent(count, len(implemented)):.1f} \\\\"
        )
    text = f"""\\begin{{table}}[t]
\\caption{{Capability distribution after paper-level dual review ($n{{=}}{len(implemented)}$ implemented canonical works). The denominator counts each work once and excludes duplicate versions, NA records, and blocked full texts; inclusion does not imply clinical readiness. Levels are non-cumulative: L4 does not certify L3.}}
\\label{{tab:levels}}
\\centering
\\small
\\setlength{{\\tabcolsep}}{{4pt}}
\\renewcommand{{\\arraystretch}}{{1.08}}
\\begin{{tabularx}}{{\\linewidth}}{{@{{}}>{{\\raggedright\\arraybackslash}}p{{2.55cm}}Xrr@{{}}}}
\\toprule
\\textbf{{Capability category}} & \\textbf{{Operational decision rule}} & \\textbf{{$n$}} & \\textbf{{\\%}} \\\\
\\midrule
{chr(10).join(body)}
\\bottomrule
\\end{{tabularx}}
\\end{{table}}
"""
    (PAPER / "table_levels.tex").write_text(text, encoding="utf-8")


def write_settings(rows: list[dict[str, str]]) -> None:
    dual = [
        row for row in rows
        if is_canonical_work_record(row) and row["adjudication_status"] == "dual_review_complete"
    ]
    medical = [
        row for row in dual
        if row["implemented_level"] in LEVELS and row["clinical_setting_primary"] not in NONCLINICAL_SETTINGS
    ]
    counts = Counter(row["clinical_setting_primary"] for row in medical)
    labels = {
        "counterfactual_treatment_planning": "Counterfactuals and treatment planning",
        "population_health_policy_simulation": "Population-health policy simulation",
        "digital_twin": "Patient and health-system digital twins",
        "medical_imaging_representation": "Medical imaging representation",
        "surgical_robotic_physiology": "Surgical, robotic, and physiology models",
        "ehr_patient_trajectory": "EHR and patient trajectories",
        "longitudinal_disease_progression": "Longitudinal disease progression",
        "other_medical": "Other medical settings",
    }
    body = []
    for setting, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        body.append(f"{labels.get(setting, escape(setting))} & {count} & {percent(count, len(medical)):.1f} \\\\")
    text = f"""\\begin{{table}}[t]
\\caption{{Primary clinical-setting distribution among dual-reviewed implemented clinical works ($n{{=}}{len(medical)}$). Each canonical work is counted once. General-domain world-model anchors and biomedical cellular-context works remain in the capability analysis but are excluded from this clinical denominator. Setting is orthogonal to disease, organ system, modality, and capability level.}}
\\label{{tab:tracks}}
\\centering
\\small
\\setlength{{\\tabcolsep}}{{6pt}}
\\renewcommand{{\\arraystretch}}{{1.08}}
\\begin{{tabularx}}{{\\linewidth}}{{@{{}}Xrr@{{}}}}
\\toprule
\\textbf{{Primary clinical setting}} & \\textbf{{$n$}} & \\textbf{{\\%}} \\\\
\\midrule
{chr(10).join(body)}
\\midrule
\\textbf{{Total}} & \\textbf{{{len(medical)}}} & \\textbf{{100.0}} \\\\
\\bottomrule
\\end{{tabularx}}
\\end{{table}}
"""
    (PAPER / "table_tracks.tex").write_text(text, encoding="utf-8")


def write_openness(rows: list[dict[str, str]]) -> None:
    audited = [
        row for row in rows
        if is_canonical_work_record(row) and row["adjudication_status"] == "dual_review_complete"
    ]
    groups = Counter(code_group(row["code_status"]) for row in audited)
    labels = {
        "public_verified": "paper-linked public code verified",
        "public_partial_or_no_weights": "public but partial/related or without weights",
        "claimed_or_pending": "claimed, announced, by request, or pending",
        "not_found_or_unreleased": "not found, unavailable, proprietary, or unreleased",
        "not_applicable": "not applicable to review/perspective",
    }
    order = ("public_verified", "public_partial_or_no_weights", "claimed_or_pending", "not_found_or_unreleased", "not_applicable")
    body = [f"Code & {labels[group]} & {groups[group]} \\\\" for group in order]
    body.extend([
        f"Full text & local searchable PDF used for audit & {sum(row['pdf_exists'] == 'yes' for row in audited)} \\\\",
        f"Full text & blocked and excluded from primary counts & {sum(row['adjudication_status'].startswith('blocked') for row in rows)} \\\\",
    ])
    text = f"""\\begin{{table}}[t]
\\caption{{Public-resource audit after paper-level review. Code categories describe the artifacts visible on the verification date; ``not found'' does not prove that private code is absent. All {len(audited)} adjudicated canonical works have a local searchable PDF, while duplicate versions are retained only for provenance and blocked records are reported separately.}}
\\label{{tab:openness}}
\\centering
\\small
\\begin{{tabular}}{{p{{1.7cm}}p{{7.0cm}}r}}
\\toprule
\\textbf{{Axis}} & \\textbf{{Category}} & \\textbf{{Count}} \\\\
\\midrule
{chr(10).join(body)}
\\bottomrule
\\end{{tabular}}
\\end{{table}}
"""
    (PAPER / "table_openness.tex").write_text(text, encoding="utf-8")


def signal(status: str) -> str:
    group = code_group(status)
    if group == "public_verified":
        return r"\cgood yes"
    if group == "public_partial_or_no_weights":
        return r"\cpart partial"
    if group == "not_applicable":
        return r"\cgap n/a"
    return r"\cgap no*"


def write_track_works(rows: list[dict[str, str]], allow_incomplete: bool) -> None:
    by_id = {row["paper_id"]: row for row in rows}
    selected_ids = [paper_id for ids in TRACK_WORK_IDS.values() for paper_id in ids]
    if not allow_incomplete:
        pending = [paper_id for paper_id in selected_ids if by_id[paper_id]["adjudication_status"] != "dual_review_complete"]
        if pending:
            raise RuntimeError(f"track-work records are not dual reviewed: {pending}")
    modality_short = {
        "ehr_structured": "EHR",
        "medical_event_codes": "event codes",
        "mri": "MRI", "ct": "CT", "xray": "radiograph",
        "ultrasound_echo": "US/echo", "physiology_waveform": "physiology",
        "surgical_video_robotics": "surgical video/robot",
        "mechanistic_simulation": "mechanistic model",
        "synthetic_simulator_state": "simulator state",
        "clinical_text": "clinical text", "multimodal": "multimodal",
    }
    rows_tex = []
    for setting, paper_ids in TRACK_WORK_IDS.items():
        rows_tex.append(
            f"\\multicolumn{{7}}{{@{{}}l}}{{\\textit{{{escape(SETTING_DISPLAY[setting])}}}}} \\\\"
        )
        for paper_id in paper_ids:
            row = by_id[paper_id]
            rows_tex.append(
                f"{escape(short(row['title'], 8))} {{\\tiny {paper_id}}} & {escape(row['year'])} & "
                f"{escape(row['implemented_level'] or 'NA')} & {escape(row['disease_family_primary'].replace('_', ' '))} & "
                f"{escape(modality_short.get(row['modality_primary'], row['modality_primary'].replace('_', ' ')))} & "
                f"{escape(row['clinical_task_primary'].replace('_', ' '))} & {signal(row['code_status'])} \\\\"
            )
        rows_tex.append(r"\addlinespace")
    text = f"""\\begin{{table*}}[p]
\\caption{{Representative dual-reviewed works across the six clinical settings. Capability, disease family, modality, task, and code status are independent fields; the complete paper-level table is provided in the audit workbook.}}
\\label{{tab:track-works}}
\\centering
\\scriptsize
\\setlength{{\\tabcolsep}}{{3pt}}
\\renewcommand{{\\arraystretch}}{{1.02}}
\\begin{{tabularx}}{{\\textwidth}}{{@{{}}p{{3.45cm}}ccp{{2.45cm}}p{{1.9cm}}Xp{{1.1cm}}@{{}}}}
\\toprule
\\textbf{{Representative work}} & \\textbf{{Year}} & \\textbf{{Lvl}} & \\textbf{{Disease family}} & \\textbf{{Modality}} & \\textbf{{Evaluated task}} & \\textbf{{Code}} \\\\
\\midrule
{chr(10).join(rows_tex)}
\\bottomrule
\\end{{tabularx}}
\\end{{table*}}
"""
    (PAPER / "table_track_works.tex").write_text(text, encoding="utf-8")


def write_representatives(rows: list[dict[str, str]], allow_incomplete: bool) -> None:
    by_id = {row["paper_id"]: row for row in rows}
    selected = [by_id[paper_id] for paper_id in REPRESENTATIVE_IDS]
    if not allow_incomplete:
        pending = [row["paper_id"] for row in selected if row["adjudication_status"] != "dual_review_complete"]
        if pending:
            raise RuntimeError(f"representative records are not dual reviewed: {pending}")
    body = []
    for row in selected:
        level = row["implemented_level"] or "NA"
        body.append(
            f"{escape(short(row['title'], 8))} {{\\tiny {row['paper_id']}}} & {level} & "
            f"{escape(SETTING_SHORT.get(row['clinical_setting_primary'], row['clinical_setting_primary']))} & {escape(short(row['action_summary'], 9))} & "
            f"{escape(short(row['transition_summary'], 11))} & {signal(row['code_status'])} \\\\"
        )
    text = f"""\\begin{{table*}}[t]
\\caption{{Representative paper-level adjudications spanning the existence gate and L0--L4 boundaries. The complete {len(rows)}-record table, probability vectors, clinical facets, page evidence, and resource checks are supplied in the audit workbook. NA examples are retained because they show why branding or optimization language alone is insufficient.}}
\\label{{tab:core-matrix}}
\\centering
\\scriptsize
\\setlength{{\\tabcolsep}}{{3.0pt}}
\\renewcommand{{\\arraystretch}}{{1.05}}
\\begin{{tabularx}}{{\\textwidth}}{{@{{}}p{{3.1cm}}cp{{2.4cm}}p{{3.6cm}}Xp{{1.1cm}}@{{}}}}
\\toprule
\\textbf{{Paper}} & \\textbf{{Lvl}} & \\textbf{{Setting}} & \\textbf{{Action contract}} & \\textbf{{Transition contract}} & \\textbf{{Code}} \\\\
\\midrule
{chr(10).join(body)}
\\bottomrule
\\end{{tabularx}}
\\vspace{{2pt}}
\\\\{{\\scriptsize Code: {{\\color{{mwmteal}}\\faCheck}} paper-linked public artifact; {{\\color{{mwmamber}}\\faAdjust}} partial/related artifact; {{\\color{{mwmgray}}\\faMinus}} no verified public study code or not applicable.}}
\\end{{table*}}
"""
    (PAPER / "table_core_matrix.tex").write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-incomplete", action="store_true")
    args = parser.parse_args()
    rows = read()
    pending = [row["paper_id"] for row in rows if row["adjudication_status"] == "codex_complete"]
    if pending and not args.allow_incomplete:
        raise RuntimeError(f"{len(pending)} records remain Codex-only; do not generate final manuscript assets")
    write_macros(rows)
    write_levels(rows)
    write_settings(rows)
    write_openness(rows)
    write_representatives(rows, args.allow_incomplete)
    write_track_works(rows, args.allow_incomplete)
    print("generated audit_numbers.tex and five manuscript tables")


if __name__ == "__main__":
    main()
