#!/usr/bin/env python3
"""Corrected reviewer-response reanalysis for PLOS ONE revision."""
from pathlib import Path
import argparse, json, math, re, shutil
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
from statsmodels.miscmodels.ordinal_model import OrderedModel
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import OLSInfluence, variance_inflation_factor
from sklearn.decomposition import FactorAnalysis
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[1]; DEFAULT_DATA=ROOT/'data'/'S2_Survey_Data.xlsx'; OUT=Path(__file__).resolve().parent/'output'
COL={'age':'age_group.q1','gender':'gender.q2','race':'race_ethnicity.q3','role':'pro_role.q4','academic_center':'at_academic_center.q5','region':'med_prac_region.q6','specialty':'med_specialty.q8','years_specialty':'yrs_experience_speciality.q9','familiarity':'ai_familiar.q10','ai_experience':'ai_experience.q11','willingness':'ai_willing_to_use.q12','general_opinion':'ai_use_gen_opinion.q13','ai_required_likelihood':'ai_required_likelihood.q16','ai_knowledge':'ai_knowledge.q17','ai_training':'ai_training.q18','use_confidence':'ai_use_confidence.q19','discuss_confidence':'ai_discuss_confidence.q20','current_ai_use':'curr_use_ai_tools.q37'}
COMP=['familiarity','willingness','general_opinion','use_confidence','discuss_confidence']
MAP={'familiarity':{'Not at all familiar':1,'Slightly familiar':2,'Moderately familiar':3,'Very familiar':4,'Extremely familiar':5},'willingness':{'Not at all willing':1,'Slightly willing':2,'Moderately willing':3,'Very willing':4,'Extremely willing':5},'general_opinion':{'Very unfavorable':1,'Unfavorable':2,'Neither favorable nor unfavorable':3,'Favorable':4,'Very favorable':5},'use_confidence':{'Not at all confident':1,'Slightly confident':2,'Moderately confident':3,'Very confident':4,'Extremely confident':5},'discuss_confidence':{'Not at all confident':1,'Slightly confident':2,'Moderately confident':3,'Very confident':4,'Extremely confident':5},'ai_required_likelihood':{'Extremely unlikely':1,'Unlikely':2,'Likely':3,'Extremely likely':4},'ai_knowledge':{'Very low':1,'Low':2,'Moderate':3,'High':4,'Very high':5},'ai_training':{'No':0,'Yes, but very limited':1,'Yes':2},'ai_experience':{'No':0,'Unsure':1,'Yes':2},'current_ai_use':{'No':0,'Unsure':1,'Yes':2}}
def clean(x): return np.nan if pd.isna(x) else str(x).strip()
def ordered(s,m):
 n=pd.to_numeric(s,errors='coerce'); return n.astype(float) if n.notna().sum()>=max(1,int(.8*s.notna().sum())) else s.map(clean).map(m).astype(float)
def midpoint(v):
 if pd.isna(v): return np.nan
 a=[float(x) for x in re.findall(r'\d+(?:\.\d+)?',str(v))]; return np.mean(a[:2]) if len(a)>=2 else (a[0] if a else np.nan)
def save(d,n,index=False): d.to_csv(OUT/n,index=index)
def alpha(x):
 z=x.dropna(); k=z.shape[1]; tv=z.sum(1).var(ddof=1); return (k/(k-1))*(1-z.var(0,ddof=1).sum()/tv)
def omega1(x):
 z=x.dropna(); Z=StandardScaler().fit_transform(z); f=FactorAnalysis(1,random_state=0).fit(Z); l=f.components_[0]; u=f.noise_variance_; return float((l.sum()**2)/((l.sum()**2)+u.sum())),pd.DataFrame({'item':z.columns,'loading_1factor':l,'uniqueness':u})
def wilson(k,n):
 z=stats.norm.ppf(.975); p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d; return c-h,c+h
def export_model(m,p):
 ci=m.conf_int(); save(pd.DataFrame({'term':m.params.index,'beta':m.params.values,'se':m.bse.values,'p_value':m.pvalues.values,'ci95_low':ci[0].values,'ci95_high':ci[1].values}),p+'_coefficients.csv'); save(pd.DataFrame([{'n':int(m.nobs),'r2':m.rsquared,'adj_r2':m.rsquared_adj,'f':m.fvalue,'f_p':m.f_pvalue,'df_model':m.df_model,'df_resid':m.df_resid}]),p+'_fit.csv')
 h=m.get_robustcov_results(cov_type='HC3'); save(pd.DataFrame({'term':m.params.index,'beta':h.params,'hc3_se':h.bse,'hc3_p_value':h.pvalues}),p+'_hc3.csv')
 infl=OLSInfluence(m); cooks=infl.cooks_distance[0]; bp=het_breuschpagan(m.resid,m.model.exog); save(pd.DataFrame([{'breusch_pagan_p':bp[1],'max_cooks_d':float(np.nanmax(cooks)),'n_cooks_gt_4_over_n':int(np.sum(cooks>4/m.nobs)),'shapiro_p':stats.shapiro(m.resid).pvalue}]),p+'_diagnostics.csv')
 ex=pd.DataFrame(m.model.exog,columns=m.model.exog_names); vv=[]
 for i,c in enumerate(ex.columns):
  if c!='Intercept':
   try:v=variance_inflation_factor(ex.values,i)
   except Exception:v=np.nan
   vv.append([c,v])
 save(pd.DataFrame(vv,columns=['term','vif']),p+'_vif.csv')
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--data',default=str(DEFAULT_DATA)); ap.add_argument('--sheet',default='Sheet 1'); a=ap.parse_args(); OUT.mkdir(parents=True,exist_ok=True)
 for p in OUT.iterdir():
  if p.is_file(): p.unlink()
 raw=pd.read_excel(a.data,sheet_name=a.sheet)
 miss=[c for c in COL.values() if c not in raw.columns]
 if miss: raise KeyError('Missing expected columns: '+', '.join(miss))
 save(pd.DataFrame({'column':raw.columns}),'00_column_inventory.csv'); save(pd.DataFrame([{'analytic_name':k,'source_column':v} for k,v in COL.items()]),'01_variable_mapping.csv')
 sc=pd.DataFrame(index=raw.index)
 for k in COMP: sc[k]=ordered(raw[COL[k]],MAP[k])
 ncomp=sc[COMP].notna().sum(1); mask=ncomp>=1; df=raw.loc[mask].copy(); sc=sc.loc[mask].copy(); ncomp=ncomp.loc[mask]
 save(pd.DataFrame([['rows in supplied workbook',len(raw)],['rows with no ClAIR component',int((~mask).sum())],['analytic rows used',len(df)]],columns=['stage','n']),'02_analytic_sample_audit.csv'); save(ncomp.value_counts().sort_index().rename_axis('n_components_nonmissing').reset_index(name='n'),'02b_clair_component_completion.csv')
 sc['clair_available_mean']=sc[COMP].mean(1,skipna=True); sc['clair_complete5']=sc[COMP].mean(1,skipna=False)
 rows=[]
 for k,c in COL.items():
  s=sc[k] if k in COMP else df[c]; rows.append([k,c,s.notna().sum(),s.isna().sum(),s.isna().mean()])
 for k in ['clair_available_mean','clair_complete5']:
  s=sc[k]; rows.append([k,'derived',s.notna().sum(),s.isna().sum(),s.isna().mean()])
 save(pd.DataFrame(rows,columns=['variable','source_column','n_nonmissing','n_missing','missing_fraction']),'03_missingness.csv')
 desc=[]
 for c in COMP+['clair_available_mean','clair_complete5']:
  s=sc[c].dropna(); desc.append([c,len(s),s.mean(),s.std(ddof=1),s.median(),s.quantile(.25),s.quantile(.75),s.min(),s.max()])
 save(pd.DataFrame(desc,columns=['variable','n','mean','sd','median','q1','q3','min','max']),'04_clair_descriptives.csv'); cc=sc[COMP].dropna(); cc.corr('spearman').to_csv(OUT/'05_component_spearman_correlations.csv'); cc.corr('pearson').to_csv(OUT/'06_component_pearson_correlations.csv'); om,load=omega1(cc); save(pd.DataFrame([{'complete_case_n':len(cc),'cronbach_alpha':alpha(cc),'mcdonald_omega_1factor_approx':om}]),'07_reliability_descriptive.csv'); save(load,'08_one_factor_loadings_descriptive.csv'); eig=np.linalg.eigvalsh(cc.corr().values)[::-1]; save(pd.DataFrame({'component_number':range(1,6),'eigenvalue':eig}),'09_correlation_eigenvalues.csv')
 loo=[]
 for omit in COMP:
  s=sc[[x for x in COMP if x!=omit]].mean(1,skipna=False); z=pd.concat([sc.clair_complete5,s],axis=1).dropna(); loo.append([omit,len(z),z.corr().iloc[0,1],s.mean(),s.std(ddof=1)])
 save(pd.DataFrame(loo,columns=['omitted_component','n_pairwise_complete','pearson_r_with_full_clair','loo_mean','loo_sd']),'10_leave_one_out_scores.csv')
 gap=[]
 for conf in ['use_confidence','discuss_confidence']:
  z=sc[['willingness',conf]].dropna(); b=(z.willingness>=4)&(z[conf]<=2); k=int(b.sum()); lo,hi=wilson(k,len(z)); gap.append([conf,len(z),k,k/len(z),lo,hi]); pd.crosstab(pd.cut(z.willingness,[0,2,3,5],labels=['low_1_2','moderate_3','high_4_5']),pd.cut(z[conf],[0,2,3,5],labels=['low_1_2','moderate_3','high_4_5'])).to_csv(OUT/f'11_gap_crosstab_{conf}.csv')
 save(pd.DataFrame(gap,columns=['confidence_outcome','paired_n','high_willing_low_conf_n','proportion','ci95_low','ci95_high']),'11_gap_summary.csv')
 tr=df[COL['ai_training']].map(clean); trr=[]
 for conf in ['use_confidence','discuss_confidence']:
  z=pd.DataFrame({'training':tr,'confidence':sc[conf]}).dropna(); ct=pd.crosstab(z.training,z.confidence); ct.to_csv(OUT/f'12_training_{conf}_crosstab.csv'); chi,p,dof,_=stats.chi2_contingency(ct); v=math.sqrt(chi/(ct.values.sum()*min(ct.shape[0]-1,ct.shape[1]-1))); trr.append([conf,len(z),chi,dof,p,v])
 save(pd.DataFrame(trr,columns=['confidence_outcome','n','chi2','df','p_value','cramers_v']),'12_training_confidence_tests.csv')
 cd=pd.DataFrame(index=df.index)
 for k in ['ai_required_likelihood','ai_knowledge','ai_training','ai_experience','current_ai_use']: cd[k]=ordered(df[COL[k]],MAP[k])
 cd['age']=df[COL['age']].map(midpoint); cd['years_specialty']=df[COL['years_specialty']].map(midpoint); cd['woman']=df[COL['gender']].map(clean).map(lambda x:1.0 if x=='Woman' else (0.0 if x=='Man' else np.nan)); cd['role']=df[COL['role']].map(clean); cd['academic_center']=df[COL['academic_center']].map(clean).map({'Yes':1.0,'No':0.0}); cd['clair']=sc.clair_available_mean
 for k in COMP: cd[k]=sc[k]
 save(pd.DataFrame([{'variable':k,'coding':str(MAP.get(k,'midpoint/binary; see script'))} for k in ['ai_required_likelihood','ai_knowledge','ai_training','ai_experience','current_ai_use','age','years_specialty','woman']]),'13_coding_specification.csv'); cd[COMP+['ai_required_likelihood','ai_knowledge','ai_training','ai_experience','current_ai_use']].corr('spearman').to_csv(OUT/'13b_predictor_component_spearman.csv')
 base=['clair','ai_knowledge','ai_required_likelihood','ai_training','ai_experience','current_ai_use','age','woman','role']; md=cd[base].dropna().copy(); md['role']=pd.Categorical(md.role,categories=['Medical Student','Advanced Practitioner (Nurse Practitioner or Physician Assistant)','Physician','Resident or Fellow']); formula='clair ~ ai_knowledge + ai_required_likelihood + ai_training + ai_experience + current_ai_use + age + woman + C(role, Treatment(reference="Medical Student"))'; m=smf.ols(formula,data=md).fit(); export_model(m,'14_primary_fullsample_ols')
 std=md.copy()
 for c in ['clair','ai_knowledge','ai_required_likelihood','ai_training','ai_experience','current_ai_use','age','woman']:
  sd=std[c].std(ddof=1); std[c]=(std[c]-std[c].mean())/sd if sd>0 else std[c]
 sm=smf.ols(formula,data=std).fit(); ci=sm.conf_int(); save(pd.DataFrame({'term':sm.params.index,'standardized_beta':sm.params.values,'se':sm.bse.values,'p_value':sm.pvalues.values,'ci95_low':ci[0].values,'ci95_high':ci[1].values}),'15_primary_fullsample_standardized.csv')
 m2=smf.ols('clair ~ ai_required_likelihood + ai_training + ai_experience + current_ai_use + age + woman + C(role, Treatment(reference="Medical Student"))',data=md).fit(); export_model(m2,'16_sensitivity_without_ai_knowledge')
 z=cd.copy(); z['clair']=sc.clair_complete5; z=z[base].dropna(); z['role']=pd.Categorical(z.role,categories=['Medical Student','Advanced Practitioner (Nurse Practitioner or Physician Assistant)','Physician','Resident or Fellow']); export_model(smf.ols(formula,data=z).fit(),'17_sensitivity_complete5_clair')
 fit=[]
 for omit in COMP:
  t=cd.copy(); t['clair']=sc[[x for x in COMP if x!=omit]].mean(1,skipna=False); zz=t[base].dropna(); zz['role']=pd.Categorical(zz.role,categories=['Medical Student','Advanced Practitioner (Nurse Practitioner or Physician Assistant)','Physician','Resident or Fellow']); mm=smf.ols(formula,data=zz).fit(); fit.append([omit,int(mm.nobs),mm.rsquared,mm.rsquared_adj,mm.params.get('woman',np.nan),mm.pvalues.get('woman',np.nan),mm.params.get('ai_knowledge',np.nan),mm.pvalues.get('ai_knowledge',np.nan),mm.params.get('ai_required_likelihood',np.nan),mm.pvalues.get('ai_required_likelihood',np.nan)])
 save(pd.DataFrame(fit,columns=['omitted_component','n','r2','adj_r2','woman_beta','woman_p','ai_knowledge_beta','ai_knowledge_p','ai_required_beta','ai_required_p']),'18_leave_one_out_model_fit.csv')
 sec=[]; ore=[]; rhs='ai_knowledge + ai_required_likelihood + ai_training + ai_experience + current_ai_use + age + woman + C(role, Treatment(reference="Medical Student"))'
 for out in COMP:
  zz=cd[[out,'ai_knowledge','ai_required_likelihood','ai_training','ai_experience','current_ai_use','age','woman','role']].dropna().copy(); zz['role']=pd.Categorical(zz.role,categories=['Medical Student','Advanced Practitioner (Nurse Practitioner or Physician Assistant)','Physician','Resident or Fellow']); mm=smf.ols(f'{out} ~ {rhs}',data=zz).fit(); sec.append([out,int(mm.nobs),mm.rsquared,mm.rsquared_adj,mm.params.get('woman',np.nan),mm.pvalues.get('woman',np.nan),mm.params.get('ai_knowledge',np.nan),mm.pvalues.get('ai_knowledge',np.nan),mm.params.get('ai_required_likelihood',np.nan),mm.pvalues.get('ai_required_likelihood',np.nan)]); ex=zz[['ai_knowledge','ai_required_likelihood','ai_training','ai_experience','current_ai_use','age','woman']]; ex=pd.concat([ex,pd.get_dummies(zz.role,drop_first=True,dtype=float)],axis=1)
  try:
   o=OrderedModel(zz[out].astype(int),ex,distr='logit').fit(method='bfgs',disp=False,maxiter=1000)
   for term in ['ai_knowledge','ai_required_likelihood','woman']: ore.append([out,term,o.params.get(term,np.nan),o.bse.get(term,np.nan),o.pvalues.get(term,np.nan)])
  except Exception: ore.append([out,'MODEL_ERROR',np.nan,np.nan,np.nan])
 save(pd.DataFrame(sec,columns=['outcome','n','r2','adj_r2','woman_beta','woman_p','ai_knowledge_beta','ai_knowledge_p','ai_required_beta','ai_required_p']),'19_secondary_component_ols_summary.csv'); save(pd.DataFrame(ore,columns=['outcome','term','log_odds_beta','se','p_value']),'20_secondary_component_ordinal_sensitivity.csv')
 sub=cd[cd.role.isin(['Physician','Advanced Practitioner (Nurse Practitioner or Physician Assistant)'])][['clair','ai_knowledge','ai_required_likelihood','ai_training','ai_experience','current_ai_use','age','woman','role','academic_center','years_specialty']].dropna(); sub['role']=pd.Categorical(sub.role,categories=['Advanced Practitioner (Nurse Practitioner or Physician Assistant)','Physician']);
 if len(sub)>=30: export_model(smf.ols('clair ~ ai_knowledge + ai_required_likelihood + ai_training + ai_experience + current_ai_use + age + woman + C(role) + academic_center + years_specialty',data=sub).fit(),'21_practice_subset_ols')
 rc=df[COL['role']].value_counts(dropna=False).rename_axis('role_value').reset_index(name='n'); save(rc,'22_role_counts.csv'); checks=[['analytic_n',len(df)],['medical_students',int((df[COL['role']]=='Medical Student').sum())],['non_students',int((df[COL['role']]!='Medical Student').sum())],['physicians',int((df[COL['role']]=='Physician').sum())],['advanced_practitioners',int(df[COL['role']].astype(str).str.startswith('Advanced Practitioner').sum())]]; save(pd.DataFrame(checks,columns=['check','value']),'22_sample_count_checks.csv')
 summary={'workbook_rows':len(raw),'analytic_n':len(df),'excluded_no_clair_component':int((~mask).sum()),'complete_5_n':int(sc.clair_complete5.notna().sum()),'available_mean_n':int(sc.clair_available_mean.notna().sum()),'cronbach_alpha_descriptive':alpha(cc),'omega_1factor_approx_descriptive':om,'primary_model_n':int(m.nobs),'primary_r2':m.rsquared,'primary_adj_r2':m.rsquared_adj}; (OUT/'summary.json').write_text(json.dumps(summary,indent=2)); (OUT/'RUN_SUMMARY.md').write_text('# Reviewer reanalysis v2 summary\n\n'+''.join(f'- {k}: {v}\n' for k,v in summary.items())+'\nClAIR is exploratory/descriptive. Seven workbook rows with no ClAIR component are excluded to reproduce N=307; verify against historical exclusion logic. Practice-specific covariates are analyzed only in the physician/advanced-practitioner subset to avoid structural missingness.\n'); zbase=Path(__file__).resolve().parent/'reviewer_reanalysis_results';
 if zbase.with_suffix('.zip').exists(): zbase.with_suffix('.zip').unlink()
 shutil.make_archive(str(zbase),'zip',OUT); print('Wrote',zbase.with_suffix('.zip'))
if __name__=='__main__': main()
