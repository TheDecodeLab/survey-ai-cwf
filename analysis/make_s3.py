#!/usr/bin/env python3
"""Build Supporting Information S3 v3 from the reanalysis outputs."""
import argparse
from pathlib import Path
import json
import pandas as pd
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

TERM = {
    "Intercept": "Intercept",
    "age": "Age (per year, category midpoint)",
    "woman": "Gender: woman (reference: man)",
    "ai_knowledge": "Self-assessed AI knowledge (1-5)",
    "ai_required_likelihood": "Perceived likelihood AI will be required (1-4)",
    "ai_training": "Prior AI training (0 = no, 1 = very limited, 2 = yes)",
    "ai_experience": "Prior AI experience (0 = no, 1 = unsure, 2 = yes)",
    "current_ai_use": "Current AI tool use (0 = no, 1 = unsure, 2 = yes)",
    "academic_center": "Academic centre (reference: non-academic)",
    "years_specialty": "Years in specialty (category midpoint)",
    "tr_lim": "Prior AI training: very limited (reference: none)",
    "tr_yes": "Prior AI training: yes (reference: none)",
    "exp_unsure": "AI experience: unsure (reference: no)",
    "exp_yes": "AI experience: yes (reference: no)",
    "use_unsure": "Current AI use: unsure (reference: no)",
    "use_yes": "Current AI use: yes (reference: no)",
    "C(role)[T.Advanced Practitioner (Nurse Practitioner or Physician Assistant)]":
        "Role: advanced practitioner (reference: medical student)",
    "C(role)[T.Physician]": "Role: physician (reference: medical student)",
    "C(role)[T.Resident or Fellow]": "Role: resident/fellow (reference: medical student)",
    "clair": "ClAIR composite score",
    "gender_display": "Gender (all displayed categories)",
    "familiarity": "Familiarity", "willingness": "Willingness",
    "general_opinion": "General opinion", "use_confidence": "Confidence in use",
    "discuss_confidence": "Confidence in discussion",
}
CONF_LAB = {1: "Not at all confident", 2: "Slightly confident", 3: "Moderately confident",
            4: "Very confident", 5: "Extremely confident"}
TRAIN_LAB = {"No": "No training", "Yes, but very limited": "Very limited training",
             "Yes": "Training received"}


def fmt(x, dp=3):
    if pd.isna(x) or x == "":
        return ""
    if isinstance(x, str):
        return x
    if abs(x) < 1e-4 and x != 0:
        return f"{x:.2e}"
    if float(x).is_integer() and abs(x) >= 1:
        return f"{int(x):,}"
    return f"{x:,.{dp}f}"


def add_table(doc, df, caption, note=None, dp=3):
    p = doc.add_paragraph()
    p.add_run(caption).bold = True
    t = doc.add_table(rows=1, cols=len(df.columns))
    t.style = "Table Grid"
    for i, c in enumerate(df.columns):
        cell = t.rows[0].cells[i]
        cell.text = str(c)
        for r in cell.paragraphs[0].runs:
            r.bold = True
            r.font.size = Pt(8.5)
    for _, row in df.iterrows():
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = fmt(v, dp)
            for r in cells[i].paragraphs[0].runs:
                r.font.size = Pt(8.5)
    if note:
        q = doc.add_paragraph()
        run = q.add_run(note)
        run.font.size = Pt(8.5)
        run.italic = True
    doc.add_paragraph()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    T = Path(a.tables)
    log = json.loads((T / "run_log.json").read_text())

    doc = Document()
    for s in doc.sections:
        s.left_margin = s.right_margin = Inches(0.8)
    doc.styles["Normal"].font.name = "Calibri"
    doc.styles["Normal"].font.size = Pt(10)

    doc.add_heading("Supporting Information File S3", level=1)
    doc.add_heading("Supplementary statistical diagnostics and sensitivity analyses "
                    "for PONE-D-26-19588", level=2)
    doc.add_paragraph(
        "These analyses are descriptive and exploratory unless otherwise stated. They are "
        "provided to make the ClAIR construction, structural diagnostics, regression checks "
        "and sensitivity analyses transparent; they are not presented as formal psychometric "
        "validation.")
    doc.add_paragraph(
        "Every coefficient, standard error, confidence interval and p-value in this file is "
        "taken from a single fitted model object per model, so the reported uncertainty is "
        "internally consistent. Where a model uses HC3 heteroscedasticity-robust inference, "
        "the standard errors, confidence intervals, p-values and the model F test are all "
        "robust; classical fit statistics are labelled as such. Analyses were produced by "
        "analysis/reanalysis.py in the public repository; the command that generates every "
        "table below is given in the README.")

    # ---- S1 missingness
    m = pd.read_csv(T / "T_missingness.csv")
    m["variable"] = m["variable"].map(lambda v: TERM.get(v, v))
    add_table(doc, m.rename(columns={"variable": "Variable", "n_nonmissing": "N non-missing",
                                     "n_missing": "N missing", "pct_missing": "Missing (%)"}),
              "Table S1. Missingness and structural non-applicability (N = %d)" % log["analytic_n"],
              "Academic-centre status and years in specialty are structurally non-applicable to "
              "medical students and residents/fellows. Gender counts the woman-versus-man "
              "regression coding: non-binary, other and missing responses are excluded from that "
              "term and retained descriptively.", dp=1)

    # ---- S2/S3 correlations
    for f, nm, lab in [("T_interitem_pearson.csv", "Table S2. Pearson inter-item correlations",
                        "Pearson"),
                       ("T_interitem_spearman.csv", "Table S3. Spearman inter-item correlations",
                        "Spearman")]:
        c = pd.read_csv(T / f, index_col=0)
        c.index = [TERM.get(i, i) for i in c.index]
        c.columns = [TERM.get(i, i) for i in c.columns]
        add_table(doc, c.reset_index().rename(columns={"index": "Component"}),
                  f"{nm} among respondents completing all five components (n = {log['structural_n']})",
                  f"{lab} coefficients. Both matrices are reported because the components are "
                  "ordinal.")

    # ---- S4 item diagnostics
    it = pd.read_csv(T / "T_item_diagnostics.csv")
    it["component"] = it["component"].map(lambda v: TERM.get(v, v))
    add_table(doc, it.rename(columns={"component": "Component",
                                      "corrected_item_total_r": "Corrected item-total r",
                                      "std_alpha_if_deleted": "Standardized alpha if deleted",
                                      "one_factor_loading": "One-factor loading"}),
              "Table S4. Item-level descriptive diagnostics",
              f"Standardized Cronbach's alpha = {log['reliability']['standardized_alpha']}; "
              f"McDonald's omega = {log['reliability']['mcdonald_omega_approx']}. Loadings come "
              "from an iterated principal-axis solution with squared multiple correlations as "
              "initial communalities, which is the extraction omega assumes; the extraction "
              "method was not stated in the previous version of this file. Observed ClAIR range "
              f"{log['clair']['min']} to {log['clair']['max']}; no respondent reached the "
              "theoretical floor of 1.0 or ceiling of 5.0 (0% floor, 0% ceiling).")

    # ---- S5 parallel analysis
    pa = pd.read_csv(T / "T_parallel_analysis.csv")
    add_table(doc, pa.rename(columns={"component": "Component",
                                      "observed_eigenvalue": "Observed eigenvalue",
                                      "random_mean": "Random mean",
                                      "random_p95": "Random 95th percentile",
                                      "retained": "Retained vs 95th"}),
              "Table S5. Monte Carlo parallel analysis "
              f"(10,000 simulations; n = {log['structural_n']}, five variables)",
              "The first two observed eigenvalues exceed the simulated 95th-percentile random "
              "eigenvalues; later components do not. This supports caution against treating "
              "ClAIR as a single validated latent dimension.")

    # ---- S6 fit table
    fit = pd.read_csv(T / "T_model_fit.csv")
    keep = ["primary_ClAIR_HC3", "primary_ClAIR_classical", "complete5_ClAIR_HC3",
            "no_AIknowledge_HC3", "indicator_coding_HC3", "practice_subset_HC3"]
    f2 = fit[fit["model"].isin(keep)][["model", "n", "df_model", "df_resid", "r2", "adj_r2",
                                      "F", "F_p", "F_inference"]]
    add_table(doc, f2.rename(columns={"model": "Model", "n": "N", "df_model": "df model",
                                      "df_resid": "df resid", "r2": "R-squared",
                                      "adj_r2": "Adjusted R-squared", "F": "F",
                                      "F_p": "F p-value", "F_inference": "F inference"}),
              "Table S6. Model fit for the primary and sensitivity models",
              "The primary model is reported twice to make the inference basis explicit: the "
              "robust Wald F (HC3) and the classical F differ, and the manuscript reports the "
              "classical F alongside HC3 coefficient inference. Both are given here so the "
              "basis of every reported statistic is unambiguous.")

    # ---- S7 primary coefficients
    co = pd.read_csv(T / "T_primary_model.csv")
    co["term"] = co["term"].map(lambda v: TERM.get(v, v))
    add_table(doc, co[["term", "beta", "se", "ci_low", "ci_high", "p", "standardized_beta"]]
              .rename(columns={"term": "Predictor", "beta": "Beta", "se": "HC3 SE",
                               "ci_low": "95% CI lower", "ci_high": "95% CI upper",
                               "p": "P value", "standardized_beta": "Standardized beta"}),
              f"Table S7. Primary multiple linear regression for ClAIR (N = {log['primary_n']})",
              "HC3 heteroscedasticity-robust standard errors. Confidence intervals and p-values "
              "are taken from the same fitted object as the standard errors. Standardized betas "
              "are shown only for predictors entered numerically; categorical contrasts are "
              "differences from a reference category and are not comparable by magnitude.")

    # ---- S8 sensitivity coefficients
    allc = pd.read_csv(T / "T_all_models_coefficients.csv")
    for label, cap, note in [
        ("complete5_ClAIR_HC3",
         "Table S8. Sensitivity analysis: respondents completing all five ClAIR components",
         "Restricting to complete-component respondents."),
        ("no_AIknowledge_HC3",
         "Table S9. Sensitivity analysis: primary model excluding self-assessed AI knowledge",
         "Fitted on the same records as the primary model. The fall in R-squared shows how much "
         "variance self-assessed knowledge accounts for; it does not by itself demonstrate "
         "conceptual overlap, because removing any strongly associated predictor lowers "
         "R-squared. Overlap is addressed by the conceptual definitions in the Methods and by "
         "the inter-item and predictor correlations in Tables S2 and S3."),
        ("indicator_coding_HC3",
         "Table S10. Sensitivity analysis: indicator coding for 'unsure' and 'very limited'",
         "The primary model codes AI experience and current AI use as 0 = no, 1 = unsure, "
         "2 = yes, and training as 0/1/2, which assumes an ordered, equally spaced effect. "
         "'Unsure' expresses uncertainty rather than intermediate exposure, so this model "
         "enters each level as its own indicator. Conclusions for the focal predictors are "
         "unchanged."),
        ("practice_subset_HC3",
         "Table S11. Practice-subset model including academic centre and years in specialty",
         "Physicians and advanced practitioners only, for whom these two items apply. Reference "
         "role is advanced practitioner. Years in specialty uses category midpoints, with "
         "'more than 20 years' coded as 25."),
    ]:
        sub = allc[allc["model"] == label].copy()
        sub["term"] = sub["term"].map(lambda v: TERM.get(v, v))
        add_table(doc, sub[["term", "beta", "se", "ci_low", "ci_high", "p"]]
                  .rename(columns={"term": "Predictor", "beta": "Beta", "se": "HC3 SE",
                                   "ci_low": "95% CI lower", "ci_high": "95% CI upper",
                                   "p": "P value"}), cap, note)

    # ---- leave-one-out
    loo = allc[allc["model"].str.startswith("leave_out_")].copy()
    loo = loo[loo["term"].isin(["woman", "ai_knowledge", "ai_required_likelihood"])]
    loo["model"] = loo["model"].str.replace("leave_out_", "", regex=False).map(
        lambda v: TERM.get(v, v))
    loo["term"] = loo["term"].map(lambda v: TERM.get(v, v))
    fitl = fit[fit["model"].str.startswith("leave_out_")][["model", "n", "r2", "adj_r2"]].copy()
    fitl["model"] = fitl["model"].str.replace("leave_out_", "", regex=False).map(
        lambda v: TERM.get(v, v))
    add_table(doc, fitl.rename(columns={"model": "Component omitted", "n": "N",
                                        "r2": "R-squared", "adj_r2": "Adjusted R-squared"}),
              "Table S12. Leave-one-component-out ClAIR models: fit")
    add_table(doc, loo[["model", "term", "beta", "se", "ci_low", "ci_high", "p"]]
              .rename(columns={"model": "Component omitted", "term": "Predictor",
                               "beta": "Beta", "se": "HC3 SE", "ci_low": "95% CI lower",
                               "ci_high": "95% CI upper", "p": "P value"}),
              "Table S13. Leave-one-component-out ClAIR models: focal predictors",
              "Full coefficient tables for every model are in analysis/outputs/"
              "T_all_models_coefficients.csv in the repository.")

    # ---- component models
    cm = pd.read_csv(T / "T_component_models_ols.csv")
    cm = cm[cm["term"].isin(["woman", "ai_knowledge", "ai_required_likelihood"])].copy()
    cm["model"] = cm["model"].str.replace("component_OLS_", "", regex=False).map(
        lambda v: TERM.get(v, v))
    cm["term"] = cm["term"].map(lambda v: TERM.get(v, v))
    add_table(doc, cm[["model", "term", "beta", "se", "ci_low", "ci_high", "p"]]
              .rename(columns={"model": "Outcome", "term": "Predictor", "beta": "Beta",
                               "se": "HC3 SE", "ci_low": "95% CI lower",
                               "ci_high": "95% CI upper", "p": "P value"}),
              "Table S14. Exploratory component-level linear models: focal predictors",
              "Standard errors and confidence intervals are now reported for every estimate. "
              "These models are exploratory and correlated; isolated p-values are not "
              "interpreted as confirmatory.")

    ordm = pd.read_csv(T / "T_component_models_ordinal.csv")
    ordm = ordm[ordm["term"].isin(["woman", "ai_knowledge", "ai_required_likelihood"])].copy()
    ordm["outcome"] = ordm["outcome"].map(lambda v: TERM.get(v, v))
    ordm["term"] = ordm["term"].map(lambda v: TERM.get(v, v))
    add_table(doc, ordm[["outcome", "term", "log_odds", "se", "ci_low", "ci_high", "p", "n"]]
              .rename(columns={"outcome": "Outcome", "term": "Predictor",
                               "log_odds": "Log-odds", "se": "SE", "ci_low": "95% CI lower",
                               "ci_high": "95% CI upper", "p": "P value", "n": "N"}),
              "Table S15. Ordinal-logistic sensitivity analyses: focal predictors",
              "Proportional-odds models with the same predictor set. Threshold parameters and "
              "full specifications are in analysis/outputs/T_component_models_ordinal.csv.")

    # ---- VIF
    vif = pd.read_csv(T / "T_vif.csv")
    vif["term"] = vif["term"].map(lambda v: TERM.get(v, v.replace("role_", "Role: ")))
    add_table(doc, vif.rename(columns={"term": "Term", "VIF": "VIF"}),
              "Table S16. Primary-model variance inflation factors",
              f"Range {log['diagnostics']['vif_min']} to {log['diagnostics']['vif_max']}.")

    # ---- diagnostics
    d = log["diagnostics"]
    dg = pd.DataFrame([
        ["Breusch-Pagan LM", d["breusch_pagan_LM"]],
        ["Breusch-Pagan p", d["breusch_pagan_p"]],
        ["Ramsey RESET F (functional form)", d["ramsey_reset_F"]],
        ["Ramsey RESET p", d["ramsey_reset_p"]],
        ["Maximum Cook's distance", d["max_cooks_d"]],
        ["Observations with Cook's D > 4/N", d["n_cooks_gt_4_over_n"]],
        ["Shapiro-Wilk p (residual normality)", d["shapiro_wilk_p"]],
    ], columns=["Diagnostic", "Value"])
    add_table(doc, dg, "Table S17. Primary-model diagnostics",
              "The Breusch-Pagan test indicates heteroscedasticity, which is why primary "
              "inference uses HC3. The Ramsey RESET test addresses functional form, which "
              "robust standard errors do not: it gives no evidence of misspecification "
              f"(F = {d['ramsey_reset_F']}, p = {d['ramsey_reset_p']}). Residual normality is "
              "imperfect; with N = 284 and robust inference this is not a material concern.")

    # ---- joint distributions and paired tests
    for lab, cap in [("use", "Table S18. Joint willingness and confidence in using AI"),
                     ("discussion", "Table S19. Joint willingness and confidence in discussing AI")]:
        ct = pd.read_csv(T / f"T_joint_willingness_{lab}.csv", index_col=0)
        add_table(doc, ct.reset_index().rename(columns={ct.index.name or "index": "Willingness"}),
                  cap, "Counts. Rows are willingness categories; columns are confidence "
                       "categories.", dp=0)

    gap = pd.read_csv(T / "T_readiness_gap.csv")
    add_table(doc, gap[["comparison", "paired_n", "high_willing_low_conf", "pct",
                        "wilson_lo", "wilson_hi", "n_willing_gt_conf", "n_equal",
                        "n_willing_lt_conf", "wilcoxon_W", "wilcoxon_p",
                        "matched_pairs_rank_biserial_r"]]
              .rename(columns={"comparison": "Comparison", "paired_n": "Paired N",
                               "high_willing_low_conf": "High willingness, low confidence",
                               "pct": "%", "wilson_lo": "Wilson 95% lower",
                               "wilson_hi": "Wilson 95% upper",
                               "n_willing_gt_conf": "Willingness > confidence",
                               "n_equal": "Equal",
                               "n_willing_lt_conf": "Willingness < confidence",
                               "wilcoxon_W": "Wilcoxon W", "wilcoxon_p": "P value",
                               "matched_pairs_rank_biserial_r": "Rank-biserial r"}),
              "Table S20. Respondent-level willingness-confidence comparison",
              "Paired comparisons use the original 1-5 responses. Positive rank-biserial values "
              "indicate higher willingness than confidence.")

    # ---- training x confidence
    for lab, cap in [("use", "Table S21. Prior AI training by confidence in using AI"),
                     ("discussion", "Table S22. Prior AI training by confidence in discussing AI")]:
        ct = pd.read_csv(T / f"T_training_by_{lab}_confidence.csv", index_col=0)
        ct.columns = [CONF_LAB[int(float(c))] for c in ct.columns]
        ct.index = [TRAIN_LAB.get(i, i) for i in ct.index]
        add_table(doc, ct.reset_index().rename(columns={"index": "Prior AI training"}),
                  cap, "Counts.", dp=0)

    tc = pd.read_csv(T / "T_training_confidence_tests.csv")
    add_table(doc, tc.rename(columns={"outcome": "Outcome", "n": "N", "chi2": "Chi-square",
                                      "df": "df", "asymptotic_p": "Asymptotic p",
                                      "cells_expected_lt_5": "Cells with expected < 5",
                                      "n_cells": "Cells", "min_expected": "Minimum expected",
                                      "monte_carlo_p_20000": "Monte Carlo p (20,000)",
                                      "cramers_V": "Cramer's V"}),
              "Table S23. Training-confidence association tests",
              "Four of fifteen expected counts are below five in each table, so a Monte Carlo "
              "permutation p-value (20,000 permutations) is reported alongside the asymptotic "
              "chi-square. The association is unchanged.")

    # ---- additional construct and model checks
    doc.add_heading("Additional construct and model checks", level=2)
    doc.add_paragraph(
        "ClAIR is treated as a pragmatic descriptive composite index, not as a reflective scale. "
        "Its indicators are not assumed to be interchangeable manifestations of one latent trait. "
        "Equal item weighting was selected for transparency. Because this gives two fifths of the "
        "score to confidence items, we also fitted a domain-balanced score assigning equal total "
        "weight to familiarity, attitudes, and confidence.")
    x = pd.read_csv(T / "T_predictor_component_correlations.csv")
    add_table(doc, x,
              "Table S24. Spearman correlations between conceptually related predictors and ClAIR components",
              "Pairwise complete observations. These correlations describe empirical overlap; they do not establish construct equivalence.")
    x = pd.read_csv(T / "T_reliability_uncertainty.csv")
    add_table(doc, x, "Table S25. Internal-consistency estimates with bootstrap uncertainty",
              "Percentile confidence intervals from 10,000 respondent-level bootstrap samples among 297 respondents completing all five components.")
    x = pd.read_csv(T / "T_domain_weighting_sensitivity.csv")
    add_table(doc, x, "Table S26. Domain-balanced weighting sensitivity analysis",
              "Complete-five-component sample. Domain-balanced weighting assigns one third each to familiarity, attitudes (willingness and opinion), and confidence (use and discussion). Focal conclusions were unchanged.", dp=4)
    x = pd.read_csv(T / "T_proportional_odds_diagnostic.csv")
    add_table(doc, x, "Table S27. Threshold-specific cumulative-logit diagnostic for the proportional-odds models",
              "Separate binary logits were fitted at each outcome threshold. Coefficient instability and very wide intervals at sparse extreme thresholds show that the proportional-odds assumption cannot be verified reliably. The ordinal models are sensitivity analyses only and are not used for primary inference.")

    doc.save(a.out)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
