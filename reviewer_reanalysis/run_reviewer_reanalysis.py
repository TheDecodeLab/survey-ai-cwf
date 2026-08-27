#!/usr/bin/env python3
"""Reviewer-response reanalysis for survey-ai-cwf.

Designed for the PLOS ONE major revision. Reads data/S2_Survey_Data.xlsx and writes
all requested diagnostics/tables/figures to reviewer_reanalysis/output/, then creates
reviewer_reanalysis_results.zip.

The script does not change the source data.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import OLSInfluence, variance_inflation_factor
from sklearn.decomposition import FactorAnalysis
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "S2_Survey_Data.xlsx"
OUT = Path(__file__).resolve().parent / "output"

COMPONENTS = {
    "familiarity": "ai_familiar.q10",
    "willingness": "ai_willing_to_use.q12",
    "general_opinion": "ai_use_gen_opinion.q13",
    "use_confidence": "ai_use_confidence.q19",
    "discuss_confidence": "ai_discuss_confidence.q20",
}
PREDICTOR_Q = {
    "ai_experience": "q11",
    "ai_required_likelihood": "q16",
    "ai_knowledge": "q17",
    "ai_training": "q18",
    "current_ai_use": "q37",
}
LIKERT_MAPS = {
    "familiarity": {"Not at all familiar": 1, "Slightly familiar": 2, "Moderately familiar": 3, "Very familiar": 4, "Extremely familiar": 5},
    "willingness": {"Not at all willing": 1, "Slightly willing": 2, "Moderately willing": 3, "Very willing": 4, "Extremely willing": 5},
    "general_opinion": {"Very unfavorable": 1, "Unfavorable": 2, "Neither favorable nor unfavorable": 3, "Favorable": 4, "Very favorable": 5},
    "use_confidence": {"Not at all confident": 1, "Slightly confident": 2, "Moderately confident": 3, "Very confident": 4, "Extremely confident": 5},
    "discuss_confidence": {"Not at all confident": 1, "Slightly confident": 2, "Moderately confident": 3, "Very confident": 4, "Extremely confident": 5},
}
DEMOGRAPHIC_PATTERNS = {
    "age": [r"(^|[._])age([._]|$)", r"age.*q"],
    "gender": [r"gender", r"sex"],
    "role": [r"professional.*role", r"clinician.*role", r"role.*q"],
    "academic_center": [r"academic.*center", r"academic.*medical", r"practice.*academic"],
    "years_specialty": [r"years.*special", r"years.*practice", r"experience.*years"],
}

def clean_text(x):
    if pd.isna(x): return np.nan
    return str(x).strip()

def map_ordered(series, mapping):
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().sum() >= max(1, int(0.8 * series.notna().sum())):
        return numeric.astype(float)
    return series.map(clean_text).map(mapping).astype(float)

def find_q_column(columns, qtoken):
    patt = re.compile(rf"(^|[._]){re.escape(qtoken)}($|[._])", re.I)
    matches = [c for c in columns if patt.search(str(c))]
    if not matches: matches = [c for c in columns if qtoken.lower() in str(c).lower()]
    return matches[0] if matches else None

def find_pattern_column(columns, patterns):
    for p in patterns:
        rx = re.compile(p, re.I)
        matches = [c for c in columns if rx.search(str(c))]
        if len(matches) == 1: return matches[0]
    return None

def cronbach_alpha(X):
    z = X.dropna()
    if len(z) < 3 or z.shape[1] < 2: return np.nan
    item_vars = z.var(axis=0, ddof=1).sum(); total_var = z.sum(axis=1).var(ddof=1); k = z.shape[1]
    return (k/(k-1))*(1-item_vars/total_var) if total_var > 0 else np.nan

def omega_one_factor(X):
    z = X.dropna()
    if len(z) < 10: return np.nan, pd.DataFrame()
    Z = StandardScaler().fit_transform(z)
    fa = FactorAnalysis(n_components=1, random_state=0).fit(Z)
    load = fa.components_[0]; uniq = fa.noise_variance_
    omega = (np.sum(load)**2)/((np.sum(load)**2)+np.sum(uniq))
    return float(omega), pd.DataFrame({"item": z.columns, "loading_1factor": load, "uniqueness": uniq})

def wilson_ci(k,n,alpha=.05):
    if n == 0: return np.nan,np.nan
    z=stats.norm.ppf(1-alpha/2); ph=k/n; den=1+z*z/n
    ctr=(ph+z*z/(2*n))/den; half=z*math.sqrt(ph*(1-ph)/n+z*z/(4*n*n))/den
    return ctr-half,ctr+half

def save_csv(df,name,index=False): df.to_csv(OUT/name,index=index)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--data",default=str(DEFAULT_DATA)); ap.add_argument("--sheet",default="Sheet 1"); args=ap.parse_args()
    data_path=Path(args.data); OUT.mkdir(parents=True,exist_ok=True)
    for p in OUT.iterdir():
        if p.is_file() or p.is_symlink(): p.unlink()
        elif p.is_dir(): shutil.rmtree(p)
    df=pd.read_excel(data_path,sheet_name=args.sheet); columns=list(df.columns)
    save_csv(pd.DataFrame({"column":columns}),"00_column_inventory.csv")
    mapping_log=[]
    for key,col in COMPONENTS.items():
        if col not in df.columns: raise KeyError(f"Required ClAIR component column missing: {col}")
        mapping_log.append((key,col,"confirmed from existing figure scripts"))
    resolved={}
    for key,q in PREDICTOR_Q.items():
        c=find_q_column(columns,q); resolved[key]=c; mapping_log.append((key,c or "UNRESOLVED",f"resolved by {q}"))
    for key,pats in DEMOGRAPHIC_PATTERNS.items():
        c=find_pattern_column(columns,pats); resolved[key]=c; mapping_log.append((key,c or "UNRESOLVED","pattern resolver; verify in mapping file"))
    save_csv(pd.DataFrame(mapping_log,columns=["analytic_name","source_column","resolution"]),"01_variable_mapping.csv")

    X=pd.DataFrame(index=df.index)
    for key,col in COMPONENTS.items(): X[key]=map_ordered(df[col],LIKERT_MAPS[key])
    X["n_components_nonmissing"]=X[list(COMPONENTS)].notna().sum(axis=1)
    X["clair_available_mean"]=X[list(COMPONENTS)].mean(axis=1,skipna=True); X.loc[X.n_components_nonmissing==0,"clair_available_mean"]=np.nan
    X["clair_complete5"]=X[list(COMPONENTS)].mean(axis=1,skipna=False)
    save_csv(X.reset_index(names="row_index"),"02_clair_scored_rows.csv")

    miss=[]
    for key,col in COMPONENTS.items(): miss.append([key,col,int(df[col].notna().sum()),int(df[col].isna().sum()),float(df[col].isna().mean())])
    for key,col in resolved.items():
        if col: miss.append([key,col,int(df[col].notna().sum()),int(df[col].isna().sum()),float(df[col].isna().mean())])
    for key in ["clair_available_mean","clair_complete5"]:
        miss.append([key,"derived",int(X[key].notna().sum()),int(X[key].isna().sum()),float(X[key].isna().mean())])
    save_csv(pd.DataFrame(miss,columns=["variable","source_column","n_nonmissing","n_missing","missing_fraction"]),"03_missingness.csv")

    complete=X[list(COMPONENTS)].dropna(); desc=[]
    for col in list(COMPONENTS)+["clair_available_mean","clair_complete5"]:
        s=X[col].dropna()
        if len(s): desc.append([col,len(s),s.mean(),s.std(ddof=1),s.median(),s.quantile(.25),s.quantile(.75),s.min(),s.max(),(s==s.min()).mean(),(s==s.max()).mean()])
    save_csv(pd.DataFrame(desc,columns=["variable","n","mean","sd","median","q1","q3","min","max","prop_at_observed_min","prop_at_observed_max"]),"04_clair_descriptives.csv")
    complete.corr(method="spearman").to_csv(OUT/"05_component_spearman_correlations.csv")
    complete.corr(method="pearson").to_csv(OUT/"06_component_pearson_correlations.csv")
    alpha=cronbach_alpha(complete); omega,fa_tbl=omega_one_factor(complete)
    save_csv(pd.DataFrame([{"complete_case_n":len(complete),"cronbach_alpha":alpha,"mcdonald_omega_1factor_approx":omega}]),"07_reliability_descriptive.csv")
    save_csv(fa_tbl,"08_one_factor_loadings_descriptive.csv")
    if len(complete)>2:
        eig=np.linalg.eigvalsh(complete.corr().values)[::-1]
        save_csv(pd.DataFrame({"component_number":range(1,len(eig)+1),"eigenvalue":eig}),"09_correlation_eigenvalues.csv")

    loo=[]
    for omit in COMPONENTS:
        keep=[k for k in COMPONENTS if k!=omit]; score=X[keep].mean(axis=1,skipna=False); pair=pd.concat([X.clair_complete5,score],axis=1).dropna(); r=pair.corr().iloc[0,1] if len(pair)>2 else np.nan
        loo.append([omit,len(pair),r,score.mean(),score.std(ddof=1)])
    save_csv(pd.DataFrame(loo,columns=["omitted_component","n_pairwise_complete","pearson_r_with_full_clair","loo_mean","loo_sd"]),"10_leave_one_out_scores.csv")

    gap=[]
    for conf in ["use_confidence","discuss_confidence"]:
        eligible=X[["willingness",conf]].dropna(); mask=(eligible.willingness>=4)&(eligible[conf]<=2); k,n=int(mask.sum()),len(eligible); lo,hi=wilson_ci(k,n)
        gap.append([conf,n,k,k/n if n else np.nan,lo,hi])
        pd.crosstab(pd.cut(eligible.willingness,bins=[0,2,3,5],labels=["low_1_2","moderate_3","high_4_5"]),pd.cut(eligible[conf],bins=[0,2,3,5],labels=["low_1_2","moderate_3","high_4_5"]),dropna=False).to_csv(OUT/f"11_gap_crosstab_{conf}.csv")
    save_csv(pd.DataFrame(gap,columns=["confidence_outcome","paired_n","high_willing_low_conf_n","proportion","ci95_low","ci95_high"]),"11_gap_summary.csv")

    tr_col=resolved.get("ai_training"); trres=[]
    if tr_col:
        tr=df[tr_col].map(clean_text)
        for conf in ["use_confidence","discuss_confidence"]:
            tmp=pd.DataFrame({"training":tr,"confidence":X[conf]}).dropna(); ct=pd.crosstab(tmp.training,tmp.confidence); ct.to_csv(OUT/f"12_training_{conf}_crosstab.csv")
            if ct.shape[0]>=2 and ct.shape[1]>=2:
                chi2,p,dof,_=stats.chi2_contingency(ct); n=ct.values.sum(); r,c=ct.shape; v=math.sqrt(chi2/(n*max(1,min(r-1,c-1)))); trres.append([conf,n,chi2,dof,p,v])
    save_csv(pd.DataFrame(trres,columns=["confidence_outcome","n","chi2","df","p_value","cramers_v"]),"12_training_confidence_tests.csv")

    corrdf=X[list(COMPONENTS)].copy()
    for key in ["ai_required_likelihood","ai_knowledge","ai_experience","current_ai_use"]:
        col=resolved.get(key)
        if col:
            num=pd.to_numeric(df[col],errors="coerce")
            if num.notna().sum()<max(3,int(.5*df[col].notna().sum())): num=pd.Series(pd.factorize(df[col],sort=True)[0]+1,index=df.index,dtype=float).where(df[col].notna())
            corrdf[key]=num
    corrdf.corr(method="spearman").to_csv(OUT/"13_predictor_component_spearman.csv")

    reg=pd.DataFrame({"clair":X.clair_complete5}); terms=[]
    for key in ["ai_knowledge","ai_required_likelihood","ai_training","ai_experience","current_ai_use"]:
        col=resolved.get(key)
        if not col: continue
        s=df[col]; num=pd.to_numeric(s,errors="coerce")
        if num.notna().sum()>=max(3,int(.7*s.notna().sum())): reg[key]=num; terms.append(key)
        else: reg[key]=s.astype("category"); terms.append(f"C({key})")
    for key in ["age","years_specialty"]:
        col=resolved.get(key)
        if not col: continue
        s=df[col]; num=pd.to_numeric(s,errors="coerce")
        if num.notna().sum()<max(3,int(.5*s.notna().sum())):
            def midpoint(v):
                if pd.isna(v): return np.nan
                nums=[float(x) for x in re.findall(r"\d+(?:\.\d+)?",str(v))]; return np.mean(nums[:2]) if len(nums)>=2 else (nums[0] if nums else np.nan)
            num=s.map(midpoint)
        reg[key]=num; terms.append(key)
    for key in ["gender","academic_center","role"]:
        col=resolved.get(key)
        if col: reg[key]=df[col].astype("category"); terms.append(f"C({key})")

    notes=[]
    if terms:
        formula="clair ~ "+" + ".join(terms); fitdf=reg.dropna()
        if len(fitdf)>=30:
            model=smf.ols(formula,data=fitdf).fit(); hc3=model.get_robustcov_results(cov_type="HC3"); ci=model.conf_int()
            save_csv(pd.DataFrame({"term":model.params.index,"beta":model.params.values,"se":model.bse.values,"p_value":model.pvalues.values,"ci95_low":ci[0].values,"ci95_high":ci[1].values}),"14_primary_ols_complete_case_coefficients.csv")
            save_csv(pd.DataFrame([{"formula":formula,"n":int(model.nobs),"r2":model.rsquared,"adj_r2":model.rsquared_adj,"f":model.fvalue,"f_p":model.f_pvalue,"df_model":model.df_model,"df_resid":model.df_resid}]),"15_primary_ols_fit.csv")
            save_csv(pd.DataFrame({"term":model.params.index,"beta":hc3.params,"hc3_se":hc3.bse,"hc3_p_value":hc3.pvalues}),"16_primary_ols_hc3.csv")
            resid=model.resid; bp=het_breuschpagan(resid,model.model.exog); infl=OLSInfluence(model); diag={"breusch_pagan_lm":bp[0],"breusch_pagan_p":bp[1],"max_cooks_d":float(np.nanmax(infl.cooks_distance[0])),"n_cooks_gt_4_over_n":int(np.sum(infl.cooks_distance[0]>4/len(fitdf)))}
            if len(resid)<=5000: sw=stats.shapiro(resid); diag.update({"shapiro_W":sw.statistic,"shapiro_p":sw.pvalue})
            save_csv(pd.DataFrame([diag]),"17_primary_ols_diagnostics.csv")
            exog=pd.DataFrame(model.model.exog,columns=model.model.exog_names); vif=[]
            for i,c in enumerate(exog.columns):
                if c.lower()=="intercept": continue
                try: vv=variance_inflation_factor(exog.values,i)
                except Exception: vv=np.nan
                vif.append([c,vv])
            save_csv(pd.DataFrame(vif,columns=["term","vif"]),"18_primary_ols_vif.csv")
            y=(fitdf.clair-fitdf.clair.mean())/fitdf.clair.std(ddof=0); design=pd.DataFrame(model.model.exog,columns=model.model.exog_names,index=fitdf.index)
            for c in design.columns:
                if c!="Intercept" and design[c].nunique(dropna=True)>2 and design[c].std(ddof=0)>0: design[c]=(design[c]-design[c].mean())/design[c].std(ddof=0)
            stdm=sm.OLS(y,design).fit(cov_type="HC3"); ci2=stdm.conf_int()
            save_csv(pd.DataFrame({"term":stdm.params.index,"standardized_beta":stdm.params.values,"hc3_se":stdm.bse.values,"p_value":stdm.pvalues.values,"ci95_low":ci2[0].values,"ci95_high":ci2[1].values}),"19_primary_ols_standardized.csv")
            if "ai_knowledge" in terms:
                f2="clair ~ "+" + ".join([t for t in terms if t!="ai_knowledge"]); m2=smf.ols(f2,data=fitdf).fit(cov_type="HC3"); ci3=m2.conf_int()
                save_csv(pd.DataFrame({"term":m2.params.index,"beta":m2.params.values,"hc3_se":m2.bse.values,"p_value":m2.pvalues.values,"ci95_low":ci3[0].values,"ci95_high":ci3[1].values}),"20_sensitivity_no_ai_knowledge.csv")
                notes.append({"analysis":"no_ai_knowledge","formula":f2,"n":int(m2.nobs),"r2":m2.rsquared,"adj_r2":m2.rsquared_adj})
            loom=[]
            for omit in COMPONENTS:
                tmp=reg.copy(); tmp["loo"]=X[[k for k in COMPONENTS if k!=omit]].mean(axis=1,skipna=False); mdf=tmp.dropna()
                if len(mdf)<30: continue
                mm=smf.ols("loo ~ "+" + ".join(terms),data=mdf).fit(cov_type="HC3"); loom.append([omit,int(mm.nobs),mm.rsquared,mm.rsquared_adj])
            save_csv(pd.DataFrame(loom,columns=["omitted_component","n","r2","adj_r2"]),"21_leave_one_out_model_fit.csv")
        else: notes.append({"analysis":"primary_ols","status":"insufficient complete cases","n":len(fitdf),"formula":formula})
    save_csv(pd.DataFrame(notes),"22_model_notes.csv")

    rolecol=resolved.get("role")
    if rolecol: df[rolecol].value_counts(dropna=False).rename_axis("role_value").reset_index(name="n").to_csv(OUT/"23_role_counts.csv",index=False)
    save_csv(pd.DataFrame([["rows_in_workbook",len(df)],["complete_5_clair",int(X.clair_complete5.notna().sum())],["any_component_clair",int(X.clair_available_mean.notna().sum())]],columns=["check","value"]),"23_sample_count_checks.csv")

    summary={"data_file":str(data_path),"sheet":args.sheet,"n_rows":len(df),"component_columns":COMPONENTS,"resolved_predictors":resolved,"complete_5_n":int(X.clair_complete5.notna().sum()),"available_mean_n":int(X.clair_available_mean.notna().sum()),"cronbach_alpha_descriptive":None if pd.isna(alpha) else float(alpha),"omega_1factor_approx_descriptive":None if pd.isna(omega) else float(omega)}
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    (OUT/"RUN_SUMMARY.md").write_text("\n".join(["# Reviewer reanalysis run summary","",f"- Workbook rows: {len(df)}",f"- Complete all five ClAIR components: {summary['complete_5_n']}",f"- ClAIR calculable from >=1 available component: {summary['available_mean_n']}",f"- Cronbach alpha (descriptive only): {summary['cronbach_alpha_descriptive']}",f"- One-factor omega approximation (descriptive only): {summary['omega_1factor_approx_descriptive']}","","## Important","","ClAIR is treated here as an exploratory descriptive composite, not a validated psychometric instrument.","Review 01_variable_mapping.csv before using regression outputs in the manuscript.","The script reports both a complete-five ClAIR and an available-item mean because the prior manuscript N=307 with smaller component Ns requires explicit reconciliation."]),encoding="utf-8")

    zipbase=Path(__file__).resolve().parent/"reviewer_reanalysis_results"; zipfile=zipbase.with_suffix(".zip")
    if zipfile.exists(): zipfile.unlink()
    staging=Path(__file__).resolve().parent/"_bundle"
    if staging.exists(): shutil.rmtree(staging)
    staging.mkdir()
    for p in OUT.iterdir():
        if p.name!="02_clair_scored_rows.csv" and p.is_file(): shutil.copy2(p,staging/p.name)
    shutil.make_archive(str(zipbase),"zip",root_dir=staging); shutil.rmtree(staging)
    print(f"Done. Upload this file to ChatGPT: {zipfile}")

if __name__=="__main__": main()
