"""Additional checks needed for the final PLOS ONE revision package.

Uses only numpy/pandas so the script runs in the bundled workspace runtime.
"""
import argparse
from pathlib import Path
import json, math
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(description="Run additional revision analyses.")
parser.add_argument("--data", required=True, help="Path to the restricted source workbook")
parser.add_argument("--out", default="analysis/outputs", help="Output directory")
args = parser.parse_args()
SRC = Path(args.data)
OUT = Path(args.out)
OUT.mkdir(parents=True, exist_ok=True)

FAMILIAR = {"Not at all familiar":1,"Slightly familiar":2,"Moderately familiar":3,
            "Very familiar":4,"Extremely familiar":5}
WILLING = {"Not at all willing":1,"Slightly willing":2,"Moderately willing":3,
           "Very willing":4,"Extremely willing":5}
OPINION = {"Very unfavorable":1,"Unfavorable":2,"Neither favorable nor unfavorable":3,
           "Favorable":4,"Very favorable":5}
CONF = {"Not at all confident":1,"Slightly confident":2,"Moderately confident":3,
        "Very confident":4,"Extremely confident":5}
KNOW = {"Very low":1,"Low":2,"Moderate":3,"High":4,"Very high":5}
REQUIRED = {"Extremely unlikely":1,"Unlikely":2,"Likely":3,"Extremely likely":4}
TRAIN = {"No":0,"Yes, but very limited":1,"Yes":2}
YNU = {"No":0,"Unsure":1,"Yes":2}
AGE = {"18 to 25 years old":21.5,"26 to 35 years old":30.5,"36 to 45 years old":40.5,
       "46 to 55 years old":50.5,"56 to 65 years old":60.5,"66 to 75 years old":70.5,
       "76 years and older":76.0}
COMP = {
    "Familiarity":"ai_familiar.q10", "Willingness":"ai_willing_to_use.q12",
    "General opinion":"ai_use_gen_opinion.q13", "Confidence in use":"ai_use_confidence.q19",
    "Confidence in discussion":"ai_discuss_confidence.q20"}
MAP = {"Familiarity":FAMILIAR,"Willingness":WILLING,"General opinion":OPINION,
       "Confidence in use":CONF,"Confidence in discussion":CONF}

def normal_p(z):
    return math.erfc(abs(float(z))/math.sqrt(2.0))

def design(df):
    roles = ["Advanced Practitioner (Nurse Practitioner or Physician Assistant)",
             "Physician", "Resident or Fellow"]
    cols = [np.ones(len(df)), df.age, df.woman, df.knowledge, df.required,
            df.training, df.experience, df.current]
    names = ["Intercept","Age","Woman","AI knowledge","AI required likelihood",
             "Prior AI training","Prior AI experience","Current AI use"]
    for role in roles:
        cols.append((df.role == role).astype(float)); names.append("Role: "+role)
    return np.column_stack(cols).astype(float), names

def ols_hc3(X, y):
    inv = np.linalg.pinv(X.T @ X)
    b = inv @ X.T @ y
    e = y - X @ b
    h = np.einsum("ij,jk,ik->i", X, inv, X)
    u = e / np.maximum(1-h, 1e-8)
    cov = inv @ (X.T @ ((u*u)[:,None]*X)) @ inv
    se = np.sqrt(np.maximum(np.diag(cov), 0))
    pred = X @ b
    r2 = 1 - np.sum((y-pred)**2)/np.sum((y-y.mean())**2)
    return b,se,r2

def logistic(X, y, maxit=100):
    b=np.zeros(X.shape[1])
    for _ in range(maxit):
        eta=np.clip(X@b,-30,30); p=1/(1+np.exp(-eta)); w=np.maximum(p*(1-p),1e-8)
        z=eta+(y-p)/w
        info=X.T@(w[:,None]*X)
        nb=np.linalg.pinv(info)@(X.T@(w*z))
        if np.max(np.abs(nb-b))<1e-8: b=nb; break
        b=nb
    cov=np.linalg.pinv(X.T@(w[:,None]*X))
    return b,np.sqrt(np.maximum(np.diag(cov),0))

def alpha_omega(a):
    R=np.corrcoef(a,rowvar=False); k=R.shape[0]
    alpha=k/(k-1)*(1-np.trace(R)/R.sum())
    h2=1-1/np.diag(np.linalg.pinv(R)); Rw=R.copy()
    for _ in range(200):
        np.fill_diagonal(Rw,h2); vals,vec=np.linalg.eigh(Rw)
        lam=vec[:,-1]*math.sqrt(max(vals[-1],1e-12))
        nh=np.clip(lam*lam,0,.999)
        if np.max(np.abs(nh-h2))<1e-8: break
        h2=nh
    if lam.sum()<0: lam=-lam
    omega=lam.sum()**2/(lam.sum()**2+np.sum(1-lam*lam))
    return alpha,omega

raw=pd.read_excel(SRC)
d=pd.DataFrame(index=raw.index)
for n,c in COMP.items(): d[n]=raw[c].map(MAP[n])
d["age"]=raw["age_group.q1"].map(AGE)
d["woman"]=np.where(raw["gender.q2"].eq("Woman"),1,np.where(raw["gender.q2"].eq("Man"),0,np.nan))
d["knowledge"]=raw["ai_knowledge.q17"].map(KNOW)
d["required"]=raw["ai_required_likelihood.q16"].map(REQUIRED)
d["training"]=raw["ai_training.q18"].map(TRAIN)
d["experience"]=raw["ai_experience.q11"].map(YNU)
d["current"]=raw["curr_use_ai_tools.q37"].map(YNU)
d["role"]=raw["pro_role.q4"]
d=d[d[list(COMP)].notna().sum(axis=1)>0].copy()

# Predictor-component rank correlations with pairwise N.
preds={"Self-assessed AI knowledge":"knowledge","Prior AI training":"training",
       "Prior AI experience":"experience","Current AI use":"current",
       "Perceived likelihood AI will be required":"required"}
rows=[]
for pl,pc in preds.items():
    for cl in COMP:
        z=d[[pc,cl]].dropna()
        rows.append({"Predictor":pl,"ClAIR component":cl,"N":len(z),
                     "Spearman rho":z[pc].rank().corr(z[cl].rank())})
pd.DataFrame(rows).round(3).to_csv(OUT/"T_predictor_component_correlations.csv",index=False)

# Bootstrap uncertainty for alpha and omega.
A=d[list(COMP)].dropna().to_numpy(float)
a0,o0=alpha_omega(A); rng=np.random.default_rng(20260905); vals=[]
for _ in range(10000): vals.append(alpha_omega(A[rng.integers(0,len(A),len(A))]))
vals=np.array(vals)
pd.DataFrame([
 {"Estimate":"Standardized Cronbach alpha","Value":a0,"Bootstrap 95% CI lower":np.quantile(vals[:,0],.025),"Bootstrap 95% CI upper":np.quantile(vals[:,0],.975)},
 {"Estimate":"Approximate McDonald omega","Value":o0,"Bootstrap 95% CI lower":np.quantile(vals[:,1],.025),"Bootstrap 95% CI upper":np.quantile(vals[:,1],.975)}]).round(3).to_csv(OUT/"T_reliability_uncertainty.csv",index=False)

# Domain-balanced alternative: familiarity, attitudes, confidence each receive one third.
cc=d.dropna(subset=list(COMP)+["age","woman","knowledge","required","training","experience","current","role"]).copy()
cc["Equal item weighting"]=cc[list(COMP)].mean(axis=1)
cc["Domain-balanced weighting"]=(cc["Familiarity"]/3 +(cc["Willingness"]+cc["General opinion"])/6 +
                                  (cc["Confidence in use"]+cc["Confidence in discussion"])/6)
X,names=design(cc); out=[]
for score in ["Equal item weighting","Domain-balanced weighting"]:
    b,se,r2=ols_hc3(X,cc[score].to_numpy(float))
    for i,n in enumerate(names):
        if n in ["Woman","AI knowledge","AI required likelihood"]:
            out.append({"Scoring":score,"N":len(cc),"R-squared":r2,"Predictor":n,
                        "Beta":b[i],"HC3 SE":se[i],"95% CI lower":b[i]-1.96*se[i],
                        "95% CI upper":b[i]+1.96*se[i],"P value":normal_p(b[i]/se[i])})
pd.DataFrame(out).round(6).to_csv(OUT/"T_domain_weighting_sensitivity.csv",index=False)

# Proportional-odds diagnostic: threshold-specific cumulative binary logits.
po=[]
for outcome in COMP:
    z=d.dropna(subset=[outcome,"age","woman","knowledge","required","training","experience","current","role"]).copy()
    X,names=design(z)
    for cut in [1,2,3,4]:
        y=(z[outcome].to_numpy(float)>cut).astype(float)
        if y.min()==y.max(): continue
        b,se=logistic(X,y)
        for focal in ["Woman","AI knowledge","AI required likelihood"]:
            i=names.index(focal)
            po.append({"Outcome":outcome,"Threshold":f"> {cut}","N":len(z),"Predictor":focal,
                       "Log-odds":b[i],"SE":se[i],"95% CI lower":b[i]-1.96*se[i],
                       "95% CI upper":b[i]+1.96*se[i]})
pd.DataFrame(po).round(3).to_csv(OUT/"T_proportional_odds_diagnostic.csv",index=False)

summary={"complete_five_n":len(A),"bootstrap_replicates":10000,
         "domain_weighting_n":len(cc),"note":"Ordinal assumption assessed with threshold-specific cumulative logits."}
(OUT/"enhancement_log.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
print(json.dumps(summary,indent=2))
