#!/usr/bin/env python3
"""Run the complete revision analysis and regenerate tables, figures, S2, and S3."""
import argparse, subprocess, sys
from pathlib import Path


def run(*args):
    print("+", " ".join(map(str,args)))
    subprocess.run([sys.executable, *map(str,args)], check=True)


def main():
    p=argparse.ArgumentParser(); p.add_argument("--data",required=True); p.add_argument("--out",default="build"); a=p.parse_args()
    here=Path(__file__).resolve().parent; out=Path(a.out); tables=out/"tables"; figures=out/"figures"
    tables.mkdir(parents=True,exist_ok=True); figures.mkdir(parents=True,exist_ok=True)
    run(here/"reanalysis.py","--data",a.data,"--out",tables)
    run(here/"enhance_analysis.py","--data",a.data,"--out",tables)
    run(here/"make_figures.py","--tables",tables,"--outdir",figures)
    run(here/"make_descriptive_figures.py","--data",a.data,"--outdir",figures)
    run(here/"deidentify_s2.py","--data",a.data,"--out",out/"S2 File.xlsx")
    run(here/"make_s3.py","--tables",tables,"--out",out/"S3 File.docx")
    print("Complete reproducibility build:", out.resolve())


if __name__ == "__main__": main()
