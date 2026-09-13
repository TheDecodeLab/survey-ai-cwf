#!/usr/bin/env python3
"""
Regenerate Figure 1 (participant flow) and Figure 3 (confidence by prior AI
training) for PONE-D-26-19588.

Fixes carried over from the audit:
  Fig 1 - box text no longer overflows; the exclusion box is a side branch
          rather than a step in the main chain; the cleaning note no longer
          sits under the arrow.
  Fig 3 - the literal backslash in "Cramer\\'s V" is gone; both panels carry
          x-axis ticks and a label; the third training level is named
          consistently; each row shows its n; the reported p is the
          Monte-Carlo p, since four of fifteen expected cells are below five.

Figure 3 deliberately reuses the original manuscript's five-step confidence
palette so revised figures remain visually consistent with the submitted
figures: coral -> orange -> light blue -> medium blue -> blue.
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1a1a1a"
MUTED = "#555555"
# Original manuscript palette used in fig1.py and fig5.py.
RAMP = ["#FF8A65", "#FFB74D", "#90CAF9", "#64B5F6", "#42A5F5"]
ORDER = ["Not at all confident", "Slightly confident", "Moderately confident",
         "Very confident", "Extremely confident"]
TRAIN_ORDER = ["No", "Yes, but very limited", "Yes"]
TRAIN_LABEL = {"No": "No training",
               "Yes, but very limited": "Very limited training",
               "Yes": "Training received"}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.edgecolor": "#999999", "axes.linewidth": 0.8,
    "text.color": INK, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": INK,
    "figure.facecolor": "white", "savefig.facecolor": "white",
})


def figure1(out, counts):
    fig, ax = plt.subplots(figsize=(8.2, 5.8), dpi=400)
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

    main_x, main_w = 4, 52          # main chain, left column
    side_x, side_w = 60, 38         # exclusion branch, right column

    def box(x, y, w, h, title, sub, weight="bold", fs=10.5):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.6,rounding_size=1.4",
                                    linewidth=1.1, edgecolor=INK, facecolor="white"))
        ax.text(x + w / 2, y + h * 0.66, title, ha="center", va="center",
                fontsize=fs, fontweight=weight, color=INK)
        ax.text(x + w / 2, y + h * 0.26, sub, ha="center", va="center",
                fontsize=fs - 0.8, color=INK, linespacing=1.4)

    def arrow(x1, y1, x2, y2):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                     mutation_scale=13, linewidth=1.2, color=INK,
                                     shrinkA=0, shrinkB=0))

    cx = main_x + main_w / 2
    box(main_x, 80, main_w, 15, "Email invitations sent", f"n = {counts['invited']:,}")
    arrow(cx, 80, cx, 62)

    box(main_x, 46, main_w, 16,
        "Records in analysis workbook\nafter original cleaning", f"n = {counts['workbook']}")

    arrow(cx, 46, cx, 28)
    ax.plot([cx, side_x], [37, 37], color=INK, linewidth=1.2)
    arrow(side_x - 0.1, 37, side_x, 37)
    box(side_x, 29.5, side_w, 15, "Excluded",
        f"No response to any of the five\nClAIR components: n = {counts['excluded']}",
        weight="normal", fs=10)

    box(main_x, 12, main_w, 16, "Final ClAIR analytic sample",
        f"n = {counts['analytic']}\nPrimary complete-case regression: n = {counts['primary']}")

    ax.text(main_x, 6.5,
            "Original cleaning criteria: \u226541 missing questions; demographics only; or outside the target\n"
            "population. Counts by reason were not retained in the available analytic record, so per-criterion\n"
            "exclusions cannot be reconstructed and 314 is not the number who opened or began the survey.",
            ha="left", va="top", fontsize=8.4, color=MUTED, linespacing=1.5)

    fig.savefig(out, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def figure3(out, tabs, stats_):
    fig, axes = plt.subplots(2, 1, figsize=(8.4, 6.6), dpi=400, sharex=True)
    for ax, (key, ct) in zip(axes, tabs.items()):
        st = stats_[key]
        pct = ct.div(ct.sum(axis=1), axis=0) * 100
        ypos = np.arange(len(TRAIN_ORDER))[::-1]
        left = np.zeros(len(TRAIN_ORDER))
        for j, lvl in enumerate(ORDER):
            vals = pct[lvl].reindex(TRAIN_ORDER).values
            ax.barh(ypos, vals, left=left, height=0.58, color=RAMP[j],
                    edgecolor="white", linewidth=1.4,
                    label=lvl if ax is axes[0] else None)
            for y, v, l in zip(ypos, vals, left):
                if v >= 7:
                    ax.text(l + v / 2, y, f"{v:.0f}%", ha="center", va="center",
                            fontsize=9, color=INK,
                            fontweight="semibold")
            left = left + vals
        ax.set_yticks(ypos)
        ax.set_yticklabels([f"{TRAIN_LABEL[t]}\n(n = {int(ct.loc[t].sum())})"
                            for t in TRAIN_ORDER], fontsize=10)
        ax.set_xlim(0, 100)
        ax.set_xticks(range(0, 101, 20))
        ax.tick_params(axis="x", labelbottom=True, labelsize=9.5)
        ax.set_xlabel("Percentage within training category (%)", fontsize=10)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.set_axisbelow(True)
        ax.xaxis.grid(True, color="#e6e6e6", linewidth=0.7)
        ax.set_title(st["title"], fontsize=11.5, fontweight="bold", pad=16, loc="left")
        ax.text(0, 1.02,
                f"$\\chi^2$ = {st['chi2']:.2f}, df = {st['df']}, "
                f"Monte-Carlo p {st['p']}, Cramer's V = {st['V']:.3f}  "
                f"(N = {st['n']}; 4 of 15 expected counts < 5)",
                transform=ax.transAxes, fontsize=9, color=MUTED, va="bottom")

    axes[0].legend(loc="lower center", bbox_to_anchor=(0.5, 1.22), ncol=5,
                   frameon=False, fontsize=9.5, handlelength=1.1, columnspacing=1.4)
    fig.tight_layout(h_pad=3.2)
    fig.savefig(out, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--tables", required=True, help="reanalysis outputs directory")
    a = ap.parse_args()
    outdir = Path(a.outdir); outdir.mkdir(parents=True, exist_ok=True)
    T = Path(a.tables)

    figure1(outdir / "Figure1.png",
            {"invited": 3563, "workbook": 314, "excluded": 7,
             "analytic": 307, "primary": 284})

    tests = pd.read_csv(T / "T_training_confidence_tests.csv")
    tabs, stats_ = {}, {}
    for key, title in [("use", "Confidence in using AI, by prior AI training"),
                       ("discussion", "Confidence in discussing AI, by prior AI training")]:
        ct = pd.read_csv(T / f"T_training_by_{key}_confidence.csv", index_col=0)
        # the runner writes numerically coded confidence columns (1..5)
        if not set(ORDER) & set(map(str, ct.columns)):
            ct.columns = [ORDER[int(float(c)) - 1] for c in ct.columns]
        tabs[key] = ct.reindex(index=TRAIN_ORDER, columns=ORDER).fillna(0)
        r = tests[tests["outcome"] == f"{key} confidence"].iloc[0]
        pv = r["monte_carlo_p_20000"]
        stats_[key] = {"title": title, "chi2": r["chi2"], "df": int(r["df"]),
                       "p": "< 0.001" if pv < 0.001 else f"= {pv:.4f}",
                       "V": r["cramers_V"], "n": int(r["n"])}
    figure3(outdir / "Figure3.png", tabs, stats_)
    print("wrote", outdir / "Figure1.png")
    print("wrote", outdir / "Figure3.png")


if __name__ == "__main__":
    main()
