# AI readiness among healthcare professionals survey

This repository contains the reproducible analysis for the PLOS ONE manuscript, “Self-reported artificial intelligence readiness among healthcare professionals and medical trainees: A cross-sectional survey” (PONE-D-26-19588).

## Data access and privacy

The complete participant-level workbook is restricted because combinations of demographic and professional variables and participant-authored text can identify respondents. Do not commit that workbook to this public repository. The manuscript Supporting Information provides a de-identified dataset. Variables withheld at row level remain available as aggregate counts.

Authorized investigators can run the complete analysis with the restricted workbook. Access requests require Penn State institutional review and a data-use agreement. Approval is not guaranteed.

## Reproduce the revision

The archived revision used Python 3.11.9. The complete pipeline was independently rerun on Python 3.9.18 with identical reported primary results. `requirements-lock.txt` records the verified package versions.

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python analysis/run_all.py --data "/authorized/path/S2 Survey Data.xlsx" --out build
```

The command creates:

- `build/tables/`: primary, sensitivity, diagnostic, and supplementary statistical outputs.
- `build/figures/Figure1.png` through `Figure5.png`.
- `build/S2 File.xlsx`: public de-identified dataset with dictionary and disclosure notes.
- `build/S3 File.docx`: supplementary statistical tables.

Random procedures use fixed seeds. The reliability bootstrap uses seed `20260905`. The chi-square Monte Carlo tests use the seed recorded in `analysis/reanalysis.py` and 20,000 permutations.

## Analysis map

`analysis/reanalysis.py` creates the primary ClAIR regression, internally consistent HC3 confidence intervals, sensitivity models, residual diagnostics, ordinal models, sparse-cell permutation tests, descriptive tables, and robustness outputs. `analysis/enhance_analysis.py` creates predictor-component correlations, bootstrap uncertainty for alpha and omega, the domain-balanced score sensitivity model, and threshold-specific ordinal diagnostics.

`analysis/make_figures.py` generates Figures 1 and 3 from the analysis outputs. `analysis/make_descriptive_figures.py` generates Figures 2, 4, and 5 directly from the source workbook. It identifies fixed multi-select options by exact phrase matching and does not split participant text at commas.

`analysis/deidentify_s2.py` creates the public workbook. `analysis/make_s3.py` creates all supplementary tables from machine-readable outputs. `analysis/run_all.py` executes the complete sequence and stops if any stage fails.

Validate a completed build against the committed machine-readable results:

```bash
python analysis/validate_reproducibility.py --build build --expected analysis/outputs
```

The committed CSV and JSON files in `analysis/outputs/` are the values used in the revision. The committed images in `figures/final/` are the regenerated manuscript figures. `docs/variable_dictionary.csv` documents the fields in the de-identified dataset.
