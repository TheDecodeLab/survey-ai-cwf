# Manuscript figures

The five manuscript figures are generated from code and are intentionally not committed as PNG or TIFF binaries.

From the repository root:

```bash
python analysis/make_figures.py --tables analysis/outputs --outdir figures/final
python analysis/make_descriptive_figures.py --data "/authorized/path/S2 Survey Data.xlsx" --outdir figures/final
```

This writes `Figure1.png` through `Figure5.png` for local preview and `Fig1.tif` through `Fig5.tif` for PLOS submission into `figures/final/`.

Figures 1 and 3 use the audited machine-readable outputs in `analysis/outputs/`. Figures 2, 4, and 5 are regenerated directly from the supplied survey workbook. Figure 4 uses raw percentages for bar widths and one-decimal displayed values; the final displayed category is the rounding residual so each displayed row totals exactly 100.0%.

`analysis/figure_export.py` converts each generated PNG to a flattened RGB TIFF with LZW compression at 300 dpi. If needed, it scales the TIFF down proportionally so that it does not exceed 2250 px in width or 2625 px in height, and it validates the 10 MB file-size limit. TIFF file names follow PLOS naming (`Fig1.tif`, `Fig2.tif`, etc.).
