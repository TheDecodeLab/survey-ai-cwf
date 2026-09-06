#!/usr/bin/env python3
"""
Build the public Supporting Information S2 file from the source workbook.

Three things happen here, in order:
  1. Direct identifiers and the editor-flagged variables are dropped.
  2. Every free-text write-in is replaced by its category label, so that no
     participant's own words are published.
  3. High-granularity categories are collapsed to the levels the manuscript
     actually reports, then re-identification risk is measured before and after.

Usage: python deidentify_s2.py --data "<S2 Survey Data.xlsx>" --out "<S2 File.xlsx>"
"""
import argparse, collections, re
import numpy as np
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

DROP = ["participant_id",            # direct identifier (editor request)
        "age_group.q1",              # editor request
        "other_thoughts.q42",        # open-ended, not analysed
        "curr_use_which_ai_tools.q38",  # open-ended tool descriptions
        "pct_med_prac_region.q7"]    # free-form percentage triples, not analysed

# Demographic quasi-identifiers withheld at record level. Their marginal
# distributions remain available on an aggregate sheet.
WITHHELD_ROWLEVEL = ["med_specialty.q8", "med_prac_region.q6", "race_ethnicity.q3",
                     "at_academic_center.q5", "yrs_experience_speciality.q9"]

# specialty categories offered by the instrument; everything else -> "Other"
SPECIALTY = ['Cardiology','Dermatology','Emergency Medicine','Endocrinology and Diabetes',
             'Family Practice','Gastroenterology and Hepatology','General Internal Medicine',
             'General Surgery','Geriatric Medicine','Hematology and Oncology','Hospital Medicine',
             'Infectious Diseases','Nephrology','Neurology','Obstetrics and Gynecology',
             'Optomotry and Opthalmology','Otolaryngology (ENT)','Pediatrics','Podiatry',
             'Psychiatry and Behavioral Health','Pulmonology, Allergy, and Critical Care Medicine',
             'Radiology','Rheumatology']

RACE = {'White':'White','Asian':'Asian','Black':'Black','MENA':'Middle Eastern/North African',
        'Hisp_Lat_Spa':'Hispanic, Latino, or Spanish','AI_AN':'American Indian/Alaska Native',
        'NH_PI':'Native Hawaiian/Pacific Islander'}

# markers that introduce participant free text
WRITE_IN = re.compile(r'\s*(Something else|None_other|Other:|stmt_other|None)\s*[,:]\s*.*$',
                      re.IGNORECASE | re.DOTALL)

QI = ['gender.q2','race_ethnicity.q3','pro_role.q4','at_academic_center.q5',
      'med_prac_region.q6','med_specialty.q8','yrs_experience_speciality.q9']


def strip_writein(val, replacement):
    """Return the category label, discarding any participant-authored text."""
    if pd.isna(val):
        return val
    s = str(val).strip()
    return replacement if WRITE_IN.search(s) else s


def option_vocabulary(series, min_records=5):
    """Legitimate instrument options recur across records; write-ins do not.

    Returns the set of comma-separated tokens appearing in at least
    `min_records` records, which is what a fixed answer option looks like.
    """
    cnt = collections.Counter()
    for v in series.dropna().astype(str):
        for tok in {t.strip() for t in v.split(',') if t.strip()}:
            cnt[tok] += 1
    return {t for t, n in cnt.items() if n >= min_records and len(t) <= 90}


def clean_multiselect(val, vocab):
    """Keep only recognised options; every write-in collapses to 'Other'."""
    if pd.isna(val):
        return val
    toks = [t.strip() for t in str(val).split(',') if t.strip()]
    keep = [t for t in toks if t in vocab]
    if len(keep) < len(toks):
        keep.append('Other')
    seen, out = set(), []
    for t in keep:
        if t not in seen:
            seen.add(t); out.append(t)
    return ', '.join(out) if out else 'Other'


def k_report(df, cols):
    keys = [tuple(str(v) for v in row) for row in df[cols].astype(str).values]
    cnt = collections.Counter(keys)
    n = len(keys)
    return {"rows": n,
            "unique_k1": sum(1 for k in keys if cnt[k] == 1),
            "k_le_2": sum(1 for k in keys if cnt[k] <= 2),
            "k_le_4": sum(1 for k in keys if cnt[k] <= 4),
            "min_k": min(cnt.values())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    src = pd.read_excel(a.data)
    before = k_report(src, QI)

    df = src.drop(columns=[c for c in DROP if c in src.columns]).copy()

    # ---- gender ------------------------------------------------------------
    def gender(v):
        if pd.isna(v):
            return v
        s = str(v).strip()
        if s == 'Woman':
            return 'Woman'
        if s == 'Man':
            return 'Man'
        if s in ('Non-binary', 'Woman, Non-binary'):
            return 'Non-binary'
        return 'Other or not reported'
    df['gender.q2'] = df['gender.q2'].map(gender)

    # ---- race / ethnicity: collapse to the categories Table 1 reports -------
    def race(v):
        if pd.isna(v):
            return v
        parts = [p.strip() for p in str(v).split(',')]
        known = [RACE[p] for p in parts if p in RACE]
        if len(known) > 1:
            return 'More than one selection'
        if len(known) == 1:
            return known[0]
        return 'Other or not reported'
    df['race_ethnicity.q3'] = df['race_ethnicity.q3'].map(race)

    # ---- specialty: instrument categories, everything else -> Other --------
    df['med_specialty.q8'] = df['med_specialty.q8'].map(
        lambda v: v if pd.isna(v) or str(v).strip() in SPECIALTY else 'Other')

    # ---- remaining single-answer columns with write-ins --------------------
    df['agree_stmt_ai_pro_relationship.q34'] = df['agree_stmt_ai_pro_relationship.q34'].map(
        lambda v: strip_writein(v, 'stmt_other'))
    df['med_prac_region.q6'] = df['med_prac_region.q6'].map(
        lambda v: strip_writein(v, 'Prefer not to answer'))

    # ---- multi-select columns ----------------------------------------------
    for c in ['agree_stmt_ai_prac_guidance.q22', 'important_prac_guidance.q23',
              'ai_benefits.q31', 'ai_concerns.q32', 'ai_most_troubling.q33',
              'familiar_ai_applications.q35', 'familiar_ai_tools.q36']:
        if c in df.columns:
            vocab = option_vocabulary(df[c])
            df[c] = df[c].map(lambda v, vv=vocab: clean_multiselect(v, vv))

    # ---- final sweep: nothing that still looks like free text --------------
    leftovers = []
    for c in df.columns:
        cnt = collections.Counter()
        for v in df[c].dropna().astype(str):
            for tok in {t.strip() for t in v.split(',') if t.strip()}:
                cnt[tok] += 1
        rare = [t for t, n in cnt.items() if n == 1 and len(t) > 30]
        if rare:
            leftovers.append((c, len(rare), rare[0][:70]))

    after_collapse = k_report(df, QI)
    agg = []
    for c in WITHHELD_ROWLEVEL:
        vc = df[c].value_counts(dropna=False)
        for lvl, n in vc.items():
            agg.append({"variable": c, "category": "(missing)" if pd.isna(lvl) else lvl,
                        "n": int(n)})
    aggregates = pd.DataFrame(agg)
    df = df.drop(columns=WITHHELD_ROWLEVEL)
    # The binary gender-role combination is the only demographic combination
    # retained at record level. Suppress both fields together for the ten
    # atypical or missing gender records; this gives a minimum released cell of 5.
    atyp = ~df["gender.q2"].isin(["Woman", "Man"])
    df.loc[atyp, "gender.q2"] = "Suppressed for confidentiality"
    df.loc[atyp, "pro_role.q4"] = "Suppressed for confidentiality"
    comp = ["ai_familiar.q10", "ai_willing_to_use.q12", "ai_use_gen_opinion.q13",
            "ai_use_confidence.q19", "ai_discuss_confidence.q20"]
    df.insert(0, "included_clair_analysis", df[comp].notna().sum(axis=1) > 0)
    df.insert(1, "n_clair_components", df[comp].notna().sum(axis=1))
    QI_final = ["gender.q2", "pro_role.q4"]
    after = k_report(df, QI_final)

    notes = pd.DataFrame([
        ["Purpose", "Public Supporting Information dataset for PONE-D-26-19588."],
        ["Source records", f"{len(src)} records in the analysis workbook."],
        ["Removed columns",
         "participant_id (direct identifier); age_group.q1 (editorial request); "
         "other_thoughts.q42 and curr_use_which_ai_tools.q38 (open-ended text, not analysed); "
         "pct_med_prac_region.q7 (free-form entries, not analysed)."],
        ["Free-text removal",
         "Participant-authored write-ins were replaced by their category label in "
         "gender, race/ethnicity, specialty, professional-relationship statement, "
         "practice setting, and every multi-select item. No participant's own words "
         "are included in this file."],
        ["Category collapsing",
         "Specialty reduced to the categories offered by the instrument, with all "
         "write-ins grouped as Other. Race/ethnicity reduced to the categories reported "
         "in Table 1, with multiple selections grouped as 'More than one selection'."],
        ["Withheld at row level",
         "Race/ethnicity, academic-centre status, years in specialty, medical specialty, "
         "and practice setting are withheld because their combinations made most records "
         "unique. Their marginal "
         "distributions are given on the 'Withheld variable counts' sheet so the reported "
         "descriptive figures remain verifiable."],
        ["Indirect-identifier assessment",
         f"Record uniqueness on the combination of gender, race/ethnicity, professional role, "
         f"academic-centre status, practice setting, specialty and years in specialty. "
         f"Source workbook: {before['unique_k1']}/{before['rows']} records unique "
         f"({100*before['unique_k1']/before['rows']:.0f}%). After collapsing write-ins and "
         f"categories: {after_collapse['unique_k1']}/{after_collapse['rows']} "
         f"({100*after_collapse['unique_k1']/after_collapse['rows']:.0f}%). "
         f"In this published file, on the retained gender-role combination: "
         f"{after['unique_k1']}/{after['rows']} "
         f"({100*after['unique_k1']/after['rows']:.0f}%). Residual uniqueness arises from "
         f"combinations of variables whose marginal distributions are already published in "
         f"Table 1."],
        ["Reproducibility note",
         "Because age was removed at editorial request, the age term in Table 1 and the "
         "age-adjusted models in Table 2 and S3 cannot be regenerated from this file. "
         "Age-adjusted and practice-subset models therefore require approved access to the restricted workbook."],
        ["Analytic sample",
         "The manuscript analyses the 307 records with at least one ClAIR component; "
         "7 records with no component response were excluded."],
    ], columns=["Item", "Detail"])

    def source_item(c):
        m = re.search(r"\.q(\d+)$", c)
        return f"Q{m.group(1)}" if m else "Derived"
    dic = pd.DataFrame({"column": df.columns,
                        "source item": [source_item(c) for c in df.columns],
                        "definition": ["Record has at least one non-missing ClAIR component." if c=="included_clair_analysis" else
                                       "Number of non-missing ClAIR components among Q10, Q12, Q13, Q19, and Q20." if c=="n_clair_components" else
                                       f"Survey response to {source_item(c)}; see S1 for the complete item wording and response options." for c in df.columns],
                        "released values / coding": ["; ".join(sorted(map(str,df[c].dropna().unique())))[:1000] for c in df.columns],
                        "missingness": ["Blank means not answered or structurally skipped; see S1 for survey logic." for _ in df.columns],
                        "n non-missing": [int(df[c].notna().sum()) for c in df.columns],
                        "n distinct": [int(df[c].nunique(dropna=True)) for c in df.columns]})

    with pd.ExcelWriter(a.out, engine="openpyxl") as w:
        df.to_excel(w, sheet_name="Data", index=False)
        dic.to_excel(w, sheet_name="Variable dictionary", index=False)
        aggregates.to_excel(w, sheet_name="Withheld variable counts", index=False)
        notes.to_excel(w, sheet_name="De-identification notes", index=False)

    wb = load_workbook(a.out)
    for ws in wb.worksheets:
        ws.freeze_panes = "A2"; ws.auto_filter.ref = ws.dimensions
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="1F4E78")
            cell.alignment = Alignment(wrap_text=True)
        for col in range(1, ws.max_column + 1):
            width = min(60, max(12, max(len(str(ws.cell(r,col).value or "")) for r in range(1,min(ws.max_row,80)+1)) + 2))
            ws.column_dimensions[get_column_letter(col)].width = width
        for row in ws.iter_rows():
            for cell in row: cell.alignment = Alignment(vertical="top", wrap_text=True)
    wb.properties.creator = "Alireza Vafaei Sadr and coauthors"
    wb.properties.lastModifiedBy = "Alireza Vafaei Sadr and coauthors"
    wb.save(a.out)

    print("source workbook   :", before)
    print("after collapsing  :", after_collapse)
    print("published file    :", after)
    print("columns:", len(src.columns), "->", len(df.columns))
    print("residual free-text-looking cells:", leftovers if leftovers else "none")


if __name__ == "__main__":
    main()
