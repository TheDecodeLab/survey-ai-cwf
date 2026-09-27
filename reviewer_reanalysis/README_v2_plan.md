# Reviewer reanalysis v2 additions

This branch extends the reviewer reanalysis to close the remaining statistical and reproducibility items identified in the second revision audit.

Implemented in `run_revision_audit_pass2.py`:

- Wilcoxon signed-rank paired comparisons for willingness vs. use confidence and willingness vs. discussion confidence, with matched-pairs rank-biserial effect sizes.
- Gender accounting audit that exports the exact raw response categories and shows which categories enter the woman-vs-man regression term.
- VIF verification from the final complete-case primary-model design matrix.
- Participant-flow diagnostics, including candidate eligibility/membership columns and a missing-threshold sensitivity probe. The script deliberately labels the threshold probe as diagnostic because skip logic can create structural missingness.
- A JSON manifest of all pass-2 outputs.

## Run

From the repository root:

```bash
git fetch origin
git checkout reviewer-reanalysis-v2
git pull
python -m venv .venv
source .venv/bin/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r reviewer_reanalysis/requirements.txt
```

First run the corrected main reanalysis if you want to regenerate the existing reviewer outputs:

```bash
python reviewer_reanalysis/run_reviewer_reanalysis_v2.py --data /path/to/S2_Survey_Data.xlsx --sheet "Sheet 1"
```

Then run the pass-2 audit:

```bash
python reviewer_reanalysis/run_revision_audit_pass2.py --data /path/to/S2_Survey_Data.xlsx --sheet "Sheet 1"
```

By default, pass-2 outputs are written to:

`reviewer_reanalysis/output_pass2/`

Please zip that folder and send it back. The most important files are:

- `30_paired_wilcoxon_readiness_gap.csv`
- `31_gender_raw_category_audit.csv`
- `31b_gender_regression_accounting.csv`
- `32_primary_model_vif_verified.csv`
- `32b_primary_model_vif_range.csv`
- `33_participant_flow_probe.csv`
- `33b_flow_candidate_eligibility_columns.csv`
- `33c_missing_threshold_sensitivity_probe.csv`
- `34_pass2_manifest.json`

The script does not export row-level participant data.

## Important limitation

The participant-flow section will not invent exclusion counts. If the workbook you supply is already the 314-row analysis workbook, it can verify the 314 -> 307 ClAIR step and identify candidate eligibility fields, but it cannot recover the number who originally opened the Qualtrics survey or the earlier per-criterion exclusions unless those pre-exclusion records are present in the supplied source export.
