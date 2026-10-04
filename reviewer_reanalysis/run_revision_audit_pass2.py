#!/usr/bin/env python3
"""Targeted analyses for PONE-D-26-19588 revision-audit pass 2.

This script intentionally works from the participant-level survey workbook and
writes only aggregate/audit outputs. It does not copy row-level data into the
output directory.

Outputs close or diagnose the remaining audit items:
  * paired Wilcoxon signed-rank tests for willingness vs confidence;
  * matched-pairs rank-biserial effect sizes;
  * exact raw gender-category accounting and regression inclusion counts;
  * final-model VIF table and range verification;
  * participant-flow diagnostics, including a transparent missing-count
    sensitivity probe and candidate eligibility/membership columns;
  * a machine-readable manifest of the generated files.

The participant-flow section is deliberately conservative: it does not claim
that a >=41-missing rule has been reconstructed unless the supplied workbook
actually contains the pre-exclusion records needed to do so.
"""
from __future__ import annotations

from pathlib import Path
import argparse
import json
import math
import re

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "S2_Survey_Data.xlsx"
DEFAULT_OUT = Path(__file__).resolve().parent / "output_pass2"

COL = {
    "age": "age_group.q1",
    "gender": "gender.q2",
    "role": "pro_role.q4",
    "academic_center": "at_academic_center.q5",
    "years_specialty": "yrs_experience_speciality.q9",
    "familiarity": "ai_familiar.q10",
    "ai_experience": "ai_experience.q11",
    "willingness": "ai_willing_to_use.q12",
    "general_opinion": "ai_use_gen_opinion.q13",
    "ai_required_likelihood": "ai_required_likelihood.q16",
    "ai_knowledge": "ai_knowledge.q17",
    "ai_training": "ai_training.q18",
    "use_confidence": "ai_use_confidence.q19",
    "discuss_confidence": "ai_discuss_confidence.q20",
    "current_ai_use": "curr_use_ai_tools.q37",
}

MAP = {
    "familiarity": {
        "Not at all familiar": 1,
        "Slightly familiar": 2,
        "Moderately familiar": 3,
        "Very familiar": 4,
        "Extremely familiar": 5,
    },
    "willingness": {
        "Not at all willing": 1,
        "Slightly willing": 2,
        "Moderately willing": 3,
        "Very willing": 4,
        "Extremely willing": 5,
    },
    "general_opinion": {
        "Very unfavorable": 1,
        "Unfavorable": 2,
        "Neither favorable nor unfavorable": 3,
        "Favorable": 4,
        "Very favorable": 5,
    },
    "use_confidence": {
        "Not at all confident": 1,
        "Slightly confident": 2,
        "Moderately confident": 3,
        "Very confident": 4,
        "Extremely confident": 5,
    },
    "discuss_confidence": {
        "Not at all confident": 1,
        "Slightly confident": 2,
        "Moderately confident": 3,
        "Very confident": 4,
        "Extremely confident": 5,
    },
    "ai_required_likelihood": {
        "Extremely unlikely": 1,
        "Unlikely": 2,
        "Likely": 3,
        "Extremely likely": 4,
    },
    "ai_knowledge": {"Very low": 1, "Low": 2, "Moderate": 3, "High": 4, "Very high": 5},
    "ai_training": {"No": 0, "Yes, but very limited": 1, "Yes": 2},
    "ai_experience": {"No": 0, "Unsure": 1, "Yes": 2},
    "current_ai_use": {"No": 0, "Unsure": 1, "Yes": 2},
}

COMP = ["familiarity", "willingness", "general_opinion", "use_confidence", "discuss_confidence"]


def clean(x):
    return np.nan if pd.isna(x) else str(x).strip()


def ordered(s: pd.Series, mapping: dict) -> pd.Series:
    n = pd.to_numeric(s, errors="coerce")
    denom = max(1, int(0.8 * s.notna().sum()))
    if n.notna().sum() >= denom:
        return n.astype(float)
    return s.map(clean).map(mapping).astype(float)


def midpoint(v):
    if pd.isna(v):
        return np.nan
    nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", str(v))]
    if len(nums) >= 2:
        return float(np.mean(nums[:2]))
    return nums[0] if nums else np.nan


def save(df: pd.DataFrame, out: Path, name: str):
    df.to_csv(out / name, index=False)


def rank_biserial_from_paired_differences(diff: pd.Series):
    """Matched-pairs rank-biserial correlation from non-zero paired differences.

    r_rb = (sum positive ranks - sum negative ranks) / total rank sum.
    Positive values mean the first variable is larger than the second.
    """
    d = pd.Series(diff).dropna().astype(float)
    d = d[d != 0]
    if len(d) == 0:
        return np.nan, 0.0, 0.0, 0
    ranks = stats.rankdata(np.abs(d), method="average")
    w_plus = float(ranks[d.to_numpy() > 0].sum())
    w_minus = float(ranks[d.to_numpy() < 0].sum())
    total = w_plus + w_minus
    r_rb = (w_plus - w_minus) / total if total else np.nan
    return float(r_rb), w_plus, w_minus, int(len(d))


def paired_wilcoxon(scored: pd.DataFrame, confidence_col: str) -> dict:
    z = scored[["willingness", confidence_col]].dropna().copy()
    diff = z["willingness"] - z[confidence_col]
    nonzero = diff[diff != 0]
    if len(nonzero):
        # scipy handles ties/zeros appropriately; use asymptotic method because ties are common.
        test = stats.wilcoxon(
            z["willingness"],
            z[confidence_col],
            zero_method="wilcox",
            correction=False,
            alternative="two-sided",
            method="approx",
        )
        W = float(test.statistic)
        p = float(test.pvalue)
    else:
        W, p = 0.0, 1.0
    rrb, wplus, wminus, n_nonzero = rank_biserial_from_paired_differences(diff)
    return {
        "comparison": f"willingness_vs_{confidence_col}",
        "paired_n": int(len(z)),
        "n_nonzero_differences": n_nonzero,
        "n_willingness_gt_confidence": int((diff > 0).sum()),
        "n_equal": int((diff == 0).sum()),
        "n_willingness_lt_confidence": int((diff < 0).sum()),
        "median_willingness": float(z["willingness"].median()),
        "median_confidence": float(z[confidence_col].median()),
        "median_paired_difference": float(diff.median()),
        "mean_paired_difference": float(diff.mean()),
        "wilcoxon_W": W,
        "wilcoxon_p": p,
        "rank_sum_positive": wplus,
        "rank_sum_negative": wminus,
        "matched_pairs_rank_biserial_r": rrb,
        "effect_direction": "positive means willingness > confidence",
    }


def gender_audit(raw: pd.DataFrame, scored_mask: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame]:
    g = raw.loc[scored_mask, COL["gender"]]
    raw_counts = (
        g.fillna("<MISSING>")
        .map(lambda x: str(x).strip())
        .value_counts(dropna=False)
        .rename_axis("raw_gender_value")
        .reset_index(name="n")
    )
    raw_counts["included_in_woman_vs_man_regression"] = raw_counts["raw_gender_value"].isin(["Woman", "Man"])
    raw_counts["regression_code_if_included"] = raw_counts["raw_gender_value"].map({"Woman": 1, "Man": 0})

    cleaned = g.map(clean)
    summary = pd.DataFrame(
        [
            ["analytic_rows_with_any_ClAIR_component", int(scored_mask.sum())],
            ["gender_source_nonmissing", int(g.notna().sum())],
            ["gender_source_missing", int(g.isna().sum())],
            ["woman_exact", int((cleaned == "Woman").sum())],
            ["man_exact", int((cleaned == "Man").sum())],
            ["woman_or_man_regression_eligible", int(cleaned.isin(["Woman", "Man"]).sum())],
            ["excluded_from_woman_vs_man_term", int((~cleaned.isin(["Woman", "Man"])).sum())],
        ],
        columns=["metric", "n"],
    )
    return raw_counts, summary


def build_model_frame(raw: pd.DataFrame, scored: pd.DataFrame) -> pd.DataFrame:
    df = raw.loc[scored.index].copy()
    cd = pd.DataFrame(index=df.index)
    for k in ["ai_required_likelihood", "ai_knowledge", "ai_training", "ai_experience", "current_ai_use"]:
        cd[k] = ordered(df[COL[k]], MAP[k])
    cd["age"] = df[COL["age"]].map(midpoint)
    cd["woman"] = df[COL["gender"]].map(clean).map(lambda x: 1.0 if x == "Woman" else (0.0 if x == "Man" else np.nan))
    cd["role"] = df[COL["role"]].map(clean)
    cd["clair"] = scored[COMP].mean(axis=1, skipna=True)
    return cd


def vif_audit(cd: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cols = ["clair", "ai_knowledge", "ai_required_likelihood", "ai_training", "ai_experience", "current_ai_use", "age", "woman", "role"]
    md = cd[cols].dropna().copy()
    md["role"] = pd.Categorical(
        md["role"],
        categories=[
            "Medical Student",
            "Advanced Practitioner (Nurse Practitioner or Physician Assistant)",
            "Physician",
            "Resident or Fellow",
        ],
    )
    formula = 'clair ~ ai_knowledge + ai_required_likelihood + ai_training + ai_experience + current_ai_use + age + woman + C(role, Treatment(reference="Medical Student"))'
    model = smf.ols(formula, data=md).fit()
    ex = pd.DataFrame(model.model.exog, columns=model.model.exog_names)
    rows = []
    for i, c in enumerate(ex.columns):
        if c == "Intercept":
            continue
        try:
            v = float(variance_inflation_factor(ex.values, i))
        except Exception:
            v = np.nan
        rows.append([c, v])
    vif = pd.DataFrame(rows, columns=["term", "vif"])
    summary = pd.DataFrame(
        [
            {
                "complete_case_n": int(model.nobs),
                "vif_min": float(vif["vif"].min()),
                "vif_max": float(vif["vif"].max()),
            }
        ]
    )
    return vif, summary


def participant_flow_probe(raw: pd.DataFrame, scored_mask: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Produce diagnostics that help determine whether original exclusions are recoverable.

    We do NOT silently equate blank cells created by skip logic with missing responses.
    The threshold table below is therefore labeled a diagnostic probe only.
    """
    n_raw = len(raw)
    n_any_clair = int(scored_mask.sum())
    n_no_clair = int((~scored_mask).sum())

    # Candidate columns that may encode eligibility/target-population status.
    pat = re.compile(r"member|eligible|eligib|target|population|penn.?state|affiliat|employ|clinician|provider", re.I)
    candidates = [c for c in raw.columns if pat.search(str(c))]
    cand_rows = []
    for c in candidates:
        s = raw[c]
        vals = s.fillna("<MISSING>").astype(str).str.strip().value_counts().head(20)
        for value, n in vals.items():
            cand_rows.append([c, value, int(n)])
    candidate_df = pd.DataFrame(cand_rows, columns=["candidate_column", "value", "n"])

    # Diagnostic missing-count sensitivity across survey-like columns.
    # Exclude common Qualtrics/admin metadata columns if present.
    admin_pat = re.compile(r"^(StartDate|EndDate|Status|IPAddress|Progress|Duration|Finished|RecordedDate|ResponseId|Recipient|ExternalReference|Location|DistributionChannel|UserLanguage)$", re.I)
    survey_cols = [c for c in raw.columns if not admin_pat.search(str(c).strip())]
    missing_count = raw[survey_cols].isna().sum(axis=1)
    thresholds = list(range(35, 46))
    sens = pd.DataFrame(
        {
            "missing_threshold": thresholds,
            "n_rows_with_missing_count_ge_threshold": [int((missing_count >= t).sum()) for t in thresholds],
            "note": "diagnostic only; skip-logic blanks may be structural, so these are not claimed exclusion counts",
        }
    )

    summary = pd.DataFrame(
        [
            ["rows_in_supplied_workbook", n_raw, "This is not necessarily the number who opened/started the original Qualtrics survey."],
            ["rows_with_any_ClAIR_component", n_any_clair, "Matches the current analytic reconstruction when the workbook is the 314-row analysis workbook."],
            ["rows_with_no_ClAIR_component", n_no_clair, "Useful for reproducing the 314 to 307 step only."],
            ["candidate_eligibility_columns_found", len(candidates), "Review 33_flow_candidate_eligibility_columns.csv manually before using any column for exclusions."],
            ["survey_like_columns_in_missingness_probe", len(survey_cols), "Probe excludes common Qualtrics metadata columns but cannot distinguish skip-logic structural missingness."],
        ],
        columns=["stage_or_metric", "n", "interpretation"],
    )
    return summary, candidate_df, sens


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(DEFAULT_DATA))
    ap.add_argument("--sheet", default="Sheet 1")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for p in out.iterdir():
        if p.is_file():
            p.unlink()

    raw = pd.read_excel(args.data, sheet_name=args.sheet)
    required = [COL[k] for k in COMP + ["age", "gender", "role", "ai_experience", "ai_required_likelihood", "ai_knowledge", "ai_training", "current_ai_use"]]
    missing = [c for c in required if c not in raw.columns]
    if missing:
        raise KeyError("Missing expected columns: " + ", ".join(missing))

    scored_all = pd.DataFrame(index=raw.index)
    for k in COMP:
        scored_all[k] = ordered(raw[COL[k]], MAP[k])
    analytic_mask = scored_all[COMP].notna().any(axis=1)
    scored = scored_all.loc[analytic_mask].copy()

    paired = pd.DataFrame([
        paired_wilcoxon(scored, "use_confidence"),
        paired_wilcoxon(scored, "discuss_confidence"),
    ])
    save(paired, out, "30_paired_wilcoxon_readiness_gap.csv")

    graw, gsummary = gender_audit(raw, analytic_mask)
    save(graw, out, "31_gender_raw_category_audit.csv")
    save(gsummary, out, "31b_gender_regression_accounting.csv")

    cd = build_model_frame(raw, scored)
    vif, vif_summary = vif_audit(cd)
    save(vif, out, "32_primary_model_vif_verified.csv")
    save(vif_summary, out, "32b_primary_model_vif_range.csv")

    flow, candidates, sensitivity = participant_flow_probe(raw, analytic_mask)
    save(flow, out, "33_participant_flow_probe.csv")
    save(candidates, out, "33b_flow_candidate_eligibility_columns.csv")
    save(sensitivity, out, "33c_missing_threshold_sensitivity_probe.csv")

    manifest = {
        "data_path_used": str(Path(args.data)),
        "sheet": args.sheet,
        "rows_in_supplied_workbook": int(len(raw)),
        "analytic_rows_with_any_ClAIR_component": int(analytic_mask.sum()),
        "outputs": sorted(p.name for p in out.iterdir() if p.is_file()),
        "important_interpretation_notes": [
            "Wilcoxon/rank-biserial analyses use the original paired 1-5 item scores and retain ordinal information.",
            "Gender audit exports exact raw categories; no nonbinary or uninformative category is silently recoded to man/woman.",
            "VIFs are recomputed from the same complete-case primary-model design matrix.",
            "Participant-flow missing-threshold counts are diagnostic only unless the workbook contains the original pre-exclusion records and structural skip logic is explicitly reconstructed.",
        ],
    }
    (out / "34_pass2_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Wrote pass-2 audit outputs to: {out}")
    print("Please send back these files (or zip the whole output_pass2 directory):")
    for p in sorted(out.iterdir()):
        if p.is_file():
            print(" -", p.name)


if __name__ == "__main__":
    main()
