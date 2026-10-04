# Manuscript figures

The five manuscript figures are generated from code and are intentionally not committed as PNG binaries.

From the repository root:

```bash
python analysis/make_figures.py --tables analysis/outputs --outdir figures/final
python analysis/make_descriptive_figures.py --data "/authorized/path/S2 Survey Data.xlsx" --outdir figures/final
```

This writes `Figure1.png` through `Figure5.png` into `figures/final/`.

Figures 1 and 3 use the audited machine-readable outputs in `analysis/outputs/`. Figures 2, 4, and 5 are regenerated directly from the supplied survey workbook. Figure 4 uses raw percentages for bar widths and one-decimal displayed values; the final displayed category is the rounding residual so each displayed row totals exactly 100.0%.
