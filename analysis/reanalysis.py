#!/usr/bin/env python3
"""
PONE-D-26-19588 -- reanalysis runner.

Rebuilds every reported statistic from a single source workbook so that
coefficients, standard errors, confidence intervals, p-values and fit
statistics for a given model all come from ONE fitted result object.

Usage:  python reanalysis.py --data "<path to S2 Survey Data.xlsx>" --out outputs/

Outputs (CSV, one file per reported table) are written to --out.
"""
import argparse, json, sys, math
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.miscmodels.ordinal_model import OrderedModel
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.proportion import proportion_confint
from statsmodels.stats.diagnostic import linear_reset
from scipy import stats

# ----------------------------------------------------------------------------
# Coding dictionaries.  Every ordered scale is coded in the direction of
# greater readiness-related endorsement.
# ----------------------------------------------------------------------------
FAMILIAR = {"Not at all familiar":1,"Slightly familiar":2,"Moderately familiar":3,
            "Very familiar":4,"Extremely familiar":5}
WILLING  = {"Not at all willing":1,"Slightly willing":2,"Moderately willing":3,
            "Very willing":4,"Extremely willing":5}
OPINION  = {"Very unfavorable":1,"Unfavorable":2,"Neither favorable nor unfavorable":3,
            "Favorable":4,"Very favorable":5}
CONF     = {"Not at all confident":1,"Slightly confident":2,"Moderately confident":3,
            "Very confident":4,"Extremely confident":5}
KNOW     = {"Very low":1,"Low":2,"Moderate":3,"High":4,"Very high":5}
REQUIRED = {"Extremely unlikely":1,"Unlikely":2,"Likely":3,"Extremely likely":4}
TRAIN    = {"No":0,"Yes, but very limited":1,"Yes":2}
YNU      = {"No":0,"Unsure":1,"Yes":2}
AGE_MID  = {"18 to 25 years old":21.5,"26 to 35 years old":30.5,"36 to 45 years old":40.5,
            "46 to 55 years old":50.5,"56 to 65 years old":60.5,"66 to 75 years old":70.5,
            "76 years and older":76.0}
YRS_MID  = {"0-5 years":2.5,"6-10 years":8.0,"11-20 years":15.5,"more than 20 years":25.0}

COMPONENTS = [("ai_familiar.q10","familiarity",FAMILIAR),
              ("ai_willing_to_use.q12","willingness",WILLING),
              ("ai_use_gen_opinion.q13","general_opinion",OPINION),
              ("ai_use_confidence.q19","use_confidence",CONF),
              ("ai_discuss_confidence.q20","discuss_confidence",CONF)]

PREDICTORS = ["age","woman","ai_knowledge","ai_required_likelihood",
              "ai_training","ai_experience","current_ai_use"]
ROLE_REF = "Medical Student"


def load(path):
    df = pd.read_excel(path)
    out = pd.DataFrame(index=df.index)
    for src, name, mapping in COMPONENTS:
        out[name] = df[src].map(mapping)
    out["age"] = df["age_group.q1"].map(AGE_MID)
    out["age_group"] = df["age_group.q1"]
    g = df["gender.q2"]
    out["gender_display"] = np.where(g.eq("Woman"), "Woman",
                             np.where(g.eq("Man"), "Man",
                             np.where(g.isin(["Non-binary","Woman, Non-binary"]), "Non-binary",
                             np.where(g.isna(), "Missing", "Other/none listed"))))
    out["woman"] = np.where(g.eq("Woman"), 1.0, np.where(g.eq("Man"), 0.0, np.nan))
    out["role"] = df["pro_role.q4"]
    out["ai_knowledge"] = df["ai_knowledge.q17"].map(KNOW)
    out["ai_required_likelihood"] = df["ai_required_likelihood.q16"].map(REQUIRED)
    out["ai_training"] = df["ai_training.q18"].map(TRAIN)
    out["ai_training_lab"] = df["ai_training.q18"]
    out["ai_experience"] = df["ai_experience.q11"].map(YNU)
    out["current_ai_use"] = df["curr_use_ai_tools.q37"].map(YNU)
    out["academic_center"] = df["at_academic_center.q5"].map({"Yes":1.0,"No":0.0})
    out["years_specialty"] = df["yrs_experience_speciality.q9"].map(YRS_MID)
    out["race"] = df["race_ethnicity.q3"]
    out["region"] = df["med_prac_region.q6"]
    out["specialty"] = df["med_specialty.q8"]
    return out


def build(df):
    comp = [n for _, n, _ in COMPONENTS]
    n_avail = df[comp].notna().sum(axis=1)
    analytic = df[n_avail > 0].copy()          # 314 -> 307
    analytic["n_components"] = n_avail[n_avail > 0]
    analytic["clair"] = analytic[comp].mean(axis=1, skipna=True)
    return analytic


def tidy(res, label, note=""):
    """Coefficients, SEs, CIs, p-values -- all from ONE result object."""
    ci = res.conf_int()
    t = pd.DataFrame({
        "model": label,
        "term": res.params.index,
        "beta": res.params.values,
        "se": res.bse.values,
        "ci_low": ci.iloc[:, 0].values,
        "ci_high": ci.iloc[:, 1].values,
        "p": res.pvalues.values,
    })
    t["note"] = note
    return t


def fit_summary(res, label, cov, extra=None):
    d = {"model": label, "n": int(res.nobs), "df_resid": int(res.df_resid),
         "df_model": int(res.df_model), "r2": res.rsquared, "adj_r2": res.rsquared_adj,
         "F": res.fvalue, "F_p": res.f_pvalue, "cov_type": cov,
         "F_inference": "robust (HC3)" if cov == "HC3" else "classical"}
    if extra:
        d.update(extra)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", default="outputs")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)

    raw = load(a.data)
    df = build(raw)
    comp = [n for _, n, _ in COMPONENTS]
    log = {"records_in_workbook": int(len(raw)),
           "excluded_no_clair_component": int(len(raw) - len(df)),
           "analytic_n": int(len(df))}

    # ---- component completion ------------------------------------------------
    log["component_completion"] = {str(k): int(v) for k, v in
                                   df["n_components"].value_counts().sort_index(ascending=False).items()}

    # ---- missingness ---------------------------------------------------------
    miss_vars = comp + ["age", "woman", "gender_display", "ai_knowledge",
                        "ai_required_likelihood", "ai_training", "ai_experience",
                        "current_ai_use", "academic_center", "years_specialty", "clair"]
    miss = pd.DataFrame({
        "variable": miss_vars,
        "n_nonmissing": [int(df[v].notna().sum()) for v in miss_vars],
        "n_missing": [int(df[v].isna().sum()) for v in miss_vars],
    })
    miss["pct_missing"] = (100 * miss["n_missing"] / len(df)).round(1)
    miss.to_csv(out / "T_missingness.csv", index=False)

    # ---- ClAIR distribution --------------------------------------------------
    c = df["clair"]
    log["clair"] = {"mean": round(c.mean(), 4), "sd": round(c.std(ddof=1), 4),
                    "median": round(c.median(), 3),
                    "q1": round(c.quantile(.25), 3), "q3": round(c.quantile(.75), 3),
                    "min": round(c.min(), 3), "max": round(c.max(), 3),
                    "pct_at_floor_1": round(100 * (c == 1).mean(), 2),
                    "pct_at_ceiling_5": round(100 * (c == 5).mean(), 2)}

    # ---- structural diagnostics (complete-five-component respondents) ---------
    Cmat = df.loc[df["n_components"] == 5, comp]
    log["structural_n"] = int(len(Cmat))
    pear = Cmat.corr(method="pearson"); spear = Cmat.corr(method="spearman")
    pear.round(3).to_csv(out / "T_interitem_pearson.csv")
    spear.round(3).to_csv(out / "T_interitem_spearman.csv")

    Z = (Cmat - Cmat.mean()) / Cmat.std(ddof=1)
    k = len(comp)
    R = pear.values
    alpha = k / (k - 1) * (1 - np.trace(R) / R.sum())     # standardized alpha
    ev = np.linalg.eigvalsh(R)[::-1]
    # one-factor loadings by iterated principal-axis factoring (squared multiple
    # correlations as initial communalities), which is what omega assumes.
    Rw = R.copy()
    h2 = 1 - 1 / np.diag(np.linalg.inv(R))
    for _ in range(200):
        np.fill_diagonal(Rw, h2)
        w, V = np.linalg.eigh(Rw)
        lam = V[:, -1] * np.sqrt(max(w[-1], 1e-12))
        new_h2 = np.clip(lam ** 2, 0, 0.999)
        if np.max(np.abs(new_h2 - h2)) < 1e-9:
            h2 = new_h2
            break
        h2 = new_h2
    load1 = lam if lam.sum() >= 0 else -lam
    omega = load1.sum() ** 2 / (load1.sum() ** 2 + (1 - load1 ** 2).sum())

    item = []
    for i, nm in enumerate(comp):
        rest = Z[[x for x in comp if x != nm]].sum(axis=1)
        r_it = np.corrcoef(Z[nm], rest)[0, 1]
        sub = pear.drop(index=nm, columns=nm).values
        kk = k - 1
        a_del = kk / (kk - 1) * (1 - np.trace(sub) / sub.sum())
        item.append({"component": nm, "corrected_item_total_r": round(r_it, 3),
                     "std_alpha_if_deleted": round(a_del, 3),
                     "one_factor_loading": round(load1[i], 3)})
    pd.DataFrame(item).to_csv(out / "T_item_diagnostics.csv", index=False)
    log["reliability"] = {"standardized_alpha": round(alpha, 3),
                          "mcdonald_omega_approx": round(omega, 3),
                          "eigenvalues": [round(x, 3) for x in ev]}

    # ---- parallel analysis ---------------------------------------------------
    rng = np.random.default_rng(20260905)
    n_obs, n_var, n_sim = len(Cmat), k, 10000
    sim = np.empty((n_sim, n_var))
    for i in range(n_sim):
        X = rng.standard_normal((n_obs, n_var))
        sim[i] = np.linalg.eigvalsh(np.corrcoef(X, rowvar=False))[::-1]
    pa = pd.DataFrame({"component": np.arange(1, n_var + 1),
                       "observed_eigenvalue": ev.round(3),
                       "random_mean": sim.mean(0).round(3),
                       "random_p95": np.percentile(sim, 95, axis=0).round(3)})
    pa["retained"] = pa["observed_eigenvalue"] > pa["random_p95"]
    pa.to_csv(out / "T_parallel_analysis.csv", index=False)

    # ---- primary model -------------------------------------------------------
    df["role"] = pd.Categorical(df["role"],
                                categories=[ROLE_REF] + sorted(set(df["role"]) - {ROLE_REF}))
    f = "clair ~ " + " + ".join(PREDICTORS) + " + C(role)"
    model_df = df.dropna(subset=["clair"] + PREDICTORS + ["role"])
    m_cls = smf.ols(f, data=model_df).fit()
    m = smf.ols(f, data=model_df).fit(cov_type="HC3")
    log["primary_n"] = int(m.nobs)

    prim = tidy(m, "primary_ClAIR_HC3", "HC3 robust; CI, p and SE all from this object")
    # y-standardized-and-x-standardized betas, numeric predictors only
    sy = model_df["clair"].std(ddof=1)
    std = {}
    for term in m.params.index:
        base = term
        if term == "Intercept" or term.startswith("C(role)"):
            std[term] = np.nan
        else:
            std[term] = m.params[term] * model_df[base].std(ddof=1) / sy
    prim["standardized_beta"] = [round(std[t], 3) if pd.notna(std[t]) else "" for t in prim["term"]]
    prim.to_csv(out / "T_primary_model.csv", index=False)

    fits = [fit_summary(m, "primary_ClAIR_HC3", "HC3"),
            fit_summary(m_cls, "primary_ClAIR_classical", "nonrobust")]

    # ---- diagnostics ---------------------------------------------------------
    bp = het_breuschpagan(m_cls.resid, m_cls.model.exog)
    infl = m_cls.get_influence()
    cooks = infl.cooks_distance[0]
    X = model_df[PREDICTORS].astype(float)
    Xc = sm.add_constant(X)
    vif_num = pd.DataFrame({"term": X.columns,
                            "VIF": [variance_inflation_factor(Xc.values, i + 1)
                                    for i in range(X.shape[1])]})
    Xd = pd.get_dummies(model_df[["role"]], drop_first=True).astype(float)
    Xall = sm.add_constant(pd.concat([X.reset_index(drop=True), Xd.reset_index(drop=True)], axis=1))
    vif_all = pd.DataFrame({"term": Xall.columns[1:],
                            "VIF": [variance_inflation_factor(Xall.values, i + 1)
                                    for i in range(Xall.shape[1] - 1)]})
    vif_all.round(3).to_csv(out / "T_vif.csv", index=False)

    # linearity / functional form
    reset = linear_reset(m_cls, power=2, test_type="fitted", use_f=True)
    diag = {"breusch_pagan_LM": round(bp[0], 4), "breusch_pagan_p": round(bp[1], 5),
            "max_cooks_d": round(float(cooks.max()), 5),
            "n_cooks_gt_4_over_n": int((cooks > 4 / len(cooks)).sum()),
            "shapiro_wilk_p": round(float(stats.shapiro(m_cls.resid)[1]), 5),
            "ramsey_reset_F": round(float(reset.statistic), 4),
            "ramsey_reset_p": round(float(reset.pvalue), 5),
            "vif_min": round(vif_all["VIF"].min(), 3),
            "vif_max": round(vif_all["VIF"].max(), 3)}
    log["diagnostics"] = diag

    # ---- sensitivity: complete 5 components ----------------------------------
    sub5 = model_df[model_df["n_components"] == 5]
    m5 = smf.ols(f, data=sub5).fit(cov_type="HC3")
    fits.append(fit_summary(m5, "complete5_ClAIR_HC3", "HC3"))
    t5 = tidy(m5, "complete5_ClAIR_HC3")

    # ---- sensitivity: drop self-assessed knowledge ----------------------------
    f_nok = "clair ~ " + " + ".join([p for p in PREDICTORS if p != "ai_knowledge"]) + " + C(role)"
    m_nok = smf.ols(f_nok, data=model_df).fit(cov_type="HC3")
    fits.append(fit_summary(m_nok, "no_AIknowledge_HC3", "HC3",
                            {"note": "same records as primary model"}))
    t_nok = tidy(m_nok, "no_AIknowledge_HC3", "same N as primary")

    # ---- sensitivity: indicator coding for Unsure -----------------------------
    md2 = model_df.copy()
    md2["exp_unsure"] = (md2["ai_experience"] == 1).astype(float)
    md2["exp_yes"] = (md2["ai_experience"] == 2).astype(float)
    md2["use_unsure"] = (md2["current_ai_use"] == 1).astype(float)
    md2["use_yes"] = (md2["current_ai_use"] == 2).astype(float)
    md2["tr_lim"] = (md2["ai_training"] == 1).astype(float)
    md2["tr_yes"] = (md2["ai_training"] == 2).astype(float)
    f_ind = ("clair ~ age + woman + ai_knowledge + ai_required_likelihood + "
             "tr_lim + tr_yes + exp_unsure + exp_yes + use_unsure + use_yes + C(role)")
    m_ind = smf.ols(f_ind, data=md2).fit(cov_type="HC3")
    fits.append(fit_summary(m_ind, "indicator_coding_HC3", "HC3",
                            {"note": "Unsure/limited entered as separate indicators"}))
    t_ind = tidy(m_ind, "indicator_coding_HC3",
                 "tests the linear No<Unsure<Yes assumption")

    # ---- leave-one-component-out ---------------------------------------------
    loo = []
    for drop in comp:
        keep = [x for x in comp if x != drop]
        d2 = df.copy()
        d2["clair"] = d2[keep].mean(axis=1, skipna=True)
        d2 = d2.dropna(subset=["clair"] + PREDICTORS + ["role"])
        mm = smf.ols(f, data=d2).fit(cov_type="HC3")
        tt = tidy(mm, f"leave_out_{drop}")
        loo.append(tt)
        fits.append(fit_summary(mm, f"leave_out_{drop}", "HC3"))
    loo = pd.concat(loo)

    # ---- practice subset ------------------------------------------------------
    prac = df.dropna(subset=["clair"] + PREDICTORS + ["academic_center", "years_specialty"])
    prac = prac[prac["role"].isin(["Physician",
                                   "Advanced Practitioner (Nurse Practitioner or Physician Assistant)"])].copy()
    prac["role"] = pd.Categorical(
        prac["role"].astype(str),
        categories=["Advanced Practitioner (Nurse Practitioner or Physician Assistant)",
                    "Physician"])
    f_pr = ("clair ~ " + " + ".join(PREDICTORS) +
            " + academic_center + years_specialty + C(role)")
    m_pr = smf.ols(f_pr, data=prac).fit(cov_type="HC3")
    fits.append(fit_summary(m_pr, "practice_subset_HC3", "HC3",
                            {"note": "reference role = Advanced Practitioner; "
                                     "years in specialty = category midpoint, "
                                     "'more than 20 years' = 25"}))
    t_pr = tidy(m_pr, "practice_subset_HC3")

    pd.concat([prim.drop(columns=["standardized_beta"]), t5, t_nok, t_ind, loo, t_pr]) \
      .round(6).to_csv(out / "T_all_models_coefficients.csv", index=False)
    pd.DataFrame(fits).round(6).to_csv(out / "T_model_fit.csv", index=False)

    # ---- component-level models (OLS + ordinal) -------------------------------
    rows_ols, rows_ord = [], []
    for nm in comp:
        d2 = df.dropna(subset=[nm] + PREDICTORS + ["role"])
        mo = smf.ols(f.replace("clair", nm), data=d2).fit(cov_type="HC3")
        rows_ols.append(tidy(mo, f"component_OLS_{nm}"))
        fits.append(fit_summary(mo, f"component_OLS_{nm}", "HC3"))
        Xo = pd.get_dummies(d2[PREDICTORS + ["role"]], columns=["role"],
                            drop_first=True).astype(float)
        try:
            om = OrderedModel(d2[nm].astype(int), Xo, distr="logit").fit(method="bfgs", disp=False)
            ci = om.conf_int()
            rows_ord.append(pd.DataFrame({
                "outcome": nm, "term": om.params.index, "log_odds": om.params.values,
                "se": om.bse.values, "ci_low": ci.iloc[:, 0].values,
                "ci_high": ci.iloc[:, 1].values, "p": om.pvalues.values,
                "n": int(om.nobs), "llf": om.llf}))
        except Exception as e:                       # pragma: no cover
            print(f"ordinal model failed for {nm}: {e}", file=sys.stderr)
    pd.concat(rows_ols).round(6).to_csv(out / "T_component_models_ols.csv", index=False)
    if rows_ord:
        pd.concat(rows_ord).round(6).to_csv(out / "T_component_models_ordinal.csv", index=False)
    pd.DataFrame(fits).round(6).to_csv(out / "T_model_fit.csv", index=False)

    # ---- readiness gap --------------------------------------------------------
    gap = []
    for cf, lab in [("use_confidence", "use"), ("discuss_confidence", "discussion")]:
        d2 = df.dropna(subset=["willingness", cf])
        hi = d2["willingness"] >= 4
        lo = d2[cf] <= 2
        n, x = len(d2), int((hi & lo).sum())
        lo_ci, hi_ci = proportion_confint(x, n, method="wilson")
        w = stats.wilcoxon(d2["willingness"], d2[cf], zero_method="wilcox",
                           alternative="two-sided", method="approx")
        d = d2["willingness"] - d2[cf]
        nz = d[d != 0]
        rb = ((nz > 0).sum() - (nz < 0).sum()) / len(nz)
        rk = stats.rankdata(nz.abs())
        rb_true = (rk[nz > 0].sum() - rk[nz < 0].sum()) / rk.sum()
        gap.append({"comparison": f"willingness vs {lab} confidence", "paired_n": n,
                    "high_willing_low_conf": x, "pct": round(100 * x / n, 1),
                    "wilson_lo": round(100 * lo_ci, 1), "wilson_hi": round(100 * hi_ci, 1),
                    "n_willing_gt_conf": int((d > 0).sum()), "n_equal": int((d == 0).sum()),
                    "n_willing_lt_conf": int((d < 0).sum()),
                    "wilcoxon_W": float(w.statistic), "wilcoxon_p": float(w.pvalue),
                    "matched_pairs_rank_biserial_r": round(rb_true, 3)})
        pd.crosstab(pd.cut(d2["willingness"], [0, 2, 3, 5], labels=["low(1-2)", "mod(3)", "high(4-5)"]),
                    pd.cut(d2[cf], [0, 2, 3, 5], labels=["low(1-2)", "mod(3)", "high(4-5)"])) \
          .to_csv(out / f"T_joint_willingness_{lab}.csv")
    pd.DataFrame(gap).to_csv(out / "T_readiness_gap.csv", index=False)

    # ---- training x confidence, with exact / Monte Carlo p --------------------
    tc = []
    for cf, lab in [("use_confidence", "use"), ("discuss_confidence", "discussion")]:
        d2 = df.dropna(subset=["ai_training_lab", cf])
        ct = pd.crosstab(d2["ai_training_lab"], d2[cf])
        ct.to_csv(out / f"T_training_by_{lab}_confidence.csv")
        chi2, p, dof, exp = stats.chi2_contingency(ct.values, correction=False)
        n = ct.values.sum()
        V = math.sqrt(chi2 / (n * (min(ct.shape) - 1)))
        mc = monte_carlo_p(ct.values, chi2, rng)
        tc.append({"outcome": f"{lab} confidence", "n": int(n), "chi2": round(chi2, 4),
                   "df": int(dof), "asymptotic_p": p,
                   "cells_expected_lt_5": int((exp < 5).sum()), "n_cells": int(exp.size),
                   "min_expected": round(float(exp.min()), 3),
                   "monte_carlo_p_20000": mc, "cramers_V": round(V, 4)})
    pd.DataFrame(tc).to_csv(out / "T_training_confidence_tests.csv", index=False)

    with open(out / "run_log.json", "w") as fh:
        json.dump(log, fh, indent=2)
    print(json.dumps(log, indent=2))


def monte_carlo_p(M, obs, rng, B=20000):
    r = M.sum(1); c = M.sum(0)
    ge = 0
    for _ in range(B):
        lab = np.repeat(np.arange(len(c)), c)
        rng.shuffle(lab)
        sim = np.zeros_like(M); s = 0
        for i, ri in enumerate(r):
            for v in lab[s:s + ri]:
                sim[i, v] += 1
            s += ri
        st, _, _, _ = stats.chi2_contingency(sim, correction=False)
        if st >= obs - 1e-9:
            ge += 1
    return round((ge + 1) / (B + 1), 5)


if __name__ == "__main__":
    main()
