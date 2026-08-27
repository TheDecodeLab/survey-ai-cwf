# PLOS ONE reviewer reanalysis

This folder contains a reproducible analysis runner created for the PLOS ONE major revision of the clinician AI-readiness survey manuscript.

## Scientific position

ClAIR is treated as an **exploratory descriptive composite score constructed from five existing survey items for this analysis**. The analyses below characterize and stress-test the score; they do **not** claim psychometric validation or an exhaustive measure of clinician AI readiness.

## What the runner produces

The script audits denominators and missingness; reconstructs the five-item ClAIR score; reports distribution, floor/ceiling behavior, correlations, Cronbach alpha and a one-factor omega approximation as descriptive diagnostics; performs leave-one-component-out robustness checks; quantifies the respondent-level willingness-confidence gap; tests training-confidence association; audits predictor/component overlap; and attempts a complete-case multiple linear regression with OLS diagnostics, HC3 robust standard errors, VIF, standardized coefficients, a model excluding AI knowledge, and leave-one-component-out outcome models.

The regression variable resolver is intentionally auditable. It writes `01_variable_mapping.csv`. **Check this file before interpreting regression results.** The five ClAIR component columns are fixed from the existing repository figure scripts; demographic columns are resolved from column-name patterns because those variable names were not available in the public GitHub branch.

## Run

From the repository root after pulling the `reviewer-reanalysis` branch:

```bash
git fetch origin
git checkout reviewer-reanalysis
git pull
python -m venv .venv
source .venv/bin/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r reviewer_reanalysis/requirements.txt
python reviewer_reanalysis/run_reviewer_reanalysis.py
```

If your workbook is elsewhere:

```bash
python reviewer_reanalysis/run_reviewer_reanalysis.py --data /path/to/S2_Survey_Data.xlsx --sheet "Sheet 1"
```

## What to upload back

Upload only:

`reviewer_reanalysis/reviewer_reanalysis_results.zip`

The ZIP deliberately excludes `02_clair_scored_rows.csv` because it contains row-level derived values. The source workbook is never copied into the ZIP.

## First checks after execution

1. Open `01_variable_mapping.csv` and confirm the demographic/predictor mappings.
2. Check `03_missingness.csv` to reconcile why the manuscript reported ClAIR N=307 while component Ns were smaller.
3. Check `23_role_counts.csv` and `23_sample_count_checks.csv` against manuscript denominators.
4. Do not interpret alpha/omega as validation. They are descriptive diagnostics only.
5. If mappings are unresolved or wrong, upload the ZIP anyway; the column inventory is included so the mapping can be corrected without sharing the source dataset.
