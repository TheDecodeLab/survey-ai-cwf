#!/usr/bin/env python3
"""Validate a completed revision build against the committed numeric outputs."""
import argparse
from pathlib import Path
import pandas as pd
from docx import Document
from PIL import Image


def main():
    p=argparse.ArgumentParser(); p.add_argument("--build",default="build_revision"); p.add_argument("--expected",default="analysis/outputs"); a=p.parse_args()
    build=Path(a.build); expected=Path(a.expected); tables=build/"tables"
    failures=[]; checked=0
    for source in sorted(expected.glob("*.csv")):
        produced=tables/source.name
        if not produced.exists(): failures.append(f"missing table: {produced}"); continue
        try:
            pd.testing.assert_frame_equal(pd.read_csv(source),pd.read_csv(produced),check_dtype=False,rtol=1e-8,atol=1e-10)
            checked += 1
        except AssertionError as exc: failures.append(f"table mismatch: {source.name}: {str(exc).splitlines()[0]}")
    for n in range(1,6):
        path=build/"figures"/f"Figure{n}.png"
        if not path.exists(): failures.append(f"missing figure: {path}"); continue
        with Image.open(path) as im:
            if im.width < 900 or im.height < 350: failures.append(f"figure resolution too low: {path} {im.size}")
    s2=pd.read_excel(build/"S2 File.xlsx",sheet_name="Data")
    if s2.shape != (314,35): failures.append(f"S2 dimensions {s2.shape}, expected (314, 35)")
    forbidden={"participant_id","age_group.q1","race_ethnicity.q3","at_academic_center.q5","yrs_experience_speciality.q9","med_specialty.q8","med_prac_region.q6","other_thoughts.q42","curr_use_which_ai_tools.q38"}
    if forbidden & set(s2.columns): failures.append(f"S2 contains protected fields: {sorted(forbidden & set(s2.columns))}")
    k=s2.groupby(["gender.q2","pro_role.q4"],dropna=False).size().min()
    if k < 5: failures.append(f"S2 minimum gender-role cell is {k}")
    table_count=len(Document(build/"S3 File.docx").tables)
    if table_count != 27: failures.append(f"S3 has {table_count} tables, expected 27")
    if failures: raise SystemExit("VALIDATION FAILED\n"+"\n".join(failures))
    print(f"VALIDATION PASSED: {checked} CSV outputs; 5 figures; S2 314x35 with minimum k={k}; S3 has 27 tables")


if __name__ == "__main__": main()
