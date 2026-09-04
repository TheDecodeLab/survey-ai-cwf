# Reviewer reanalysis v2 additions

This branch extends the reviewer reanalysis to close the remaining statistical and reproducibility items identified in the second revision audit.

Planned outputs:

- Wilcoxon signed-rank paired comparisons for willingness vs. use confidence and willingness vs. discussion confidence, with matched-pairs rank-biserial effect sizes.
- Gender accounting audit reconciling raw response categories, descriptive Table 1 categories, and regression inclusion/exclusion.
- VIF range verification from the final primary-model design matrix.
- Participant-flow reconstruction from the raw/source survey export when available, including counts by exclusion criterion and sensitivity to the >=41-missing-question threshold.
- Reproducibility manifest for final manuscript tables/figures and S3 outputs.

The script is designed to fail loudly when participant-level source data needed for a requested analysis are unavailable rather than infer counts from aggregate outputs.
