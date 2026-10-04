#!/usr/bin/env python3
"""Regenerate manuscript Figures 1 and 3 for PONE-D-26-19588.

The visual layout is intentionally synchronized to the figures embedded in the
revised manuscript. Figure 3 is generated from machine-readable reanalysis
outputs; Figure 1 uses the audited participant-flow counts.
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#222222"
MUTED = "#555555"
RAMP = ["#FF8A65", "#FFB74D", "#90CAF9", "#64B5F6", "#42A5F5"]
ORDER = ["Not at all confident", "Slightly confident", "Moderately confident",
         "Very confident", "Extremely confident"]
TRAIN_ORDER = ["No", "Yes, but very limited", "Yes"]
TRAIN_LABEL = {"No": "No training",
               "Yes, but very limited": "Very limited training",
               "Yes": "Training received"}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.edgecolor": "#777777",
    "axes.linewidth": 0.8,
    "text.color": INK,
    "axes.labelcolor": INK,
    "xtick.color": MUTED,
    "ytick.color": INK,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
})


def figure1(out, counts):
    """Participant flow matching the clean manuscript figure."""
    fig, ax = plt.subplots(figsize=(8.3333, 5.3867), dpi=300)
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    main_x, main_w = 1.0, 55.2
    side_x, side_w = 58.3, 40.7

    def box(x, y, w, h, title, sub, weight="bold", title_fs=15.5, sub_fs=14.0):
        ax.add_patch(FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.72,rounding_size=2.0",
            linewidth=1.65, edgecolor=INK, facecolor="white"
        ))
        ax.text(x + w / 2, y + h * 0.64, title,
                ha="center", va="center", fontsize=title_fs,
                fontweight=weight, color=INK, linespacing=1.10)
        ax.text(x + w / 2, y + h * 0.28, sub,
                ha="center", va="center", fontsize=sub_fs,
                fontweight="normal", color=INK, linespacing=1.10)

    def arrow(x1, y1, x2, y2):
        ax.add_patch(FancyArrowPatch(
            (x1, y1), (x2, y2), arrowstyle="->",
            mutation_scale=23, linewidth=3.0, color=INK,
            shrinkA=0, shrinkB=0
        ))

    cx = main_x + main_w / 2
    box(main_x, 77.0, main_w, 22.0,
        "Email invitations sent", f"n = {counts['invited']:,}")
    arrow(cx, 76.1, cx, 63.0)

    box(main_x, 43.0, main_w, 24.0,
        "Records in analysis workbook\nafter original cleaning",
        f"n = {counts['workbook']}")

    ax.plot([cx, cx], [42.2, 35.1], color=INK, linewidth=3.0)
    ax.plot([cx, side_x], [35.1, 35.1], color=INK, linewidth=3.0)
    arrow(side_x - 0.2, 35.1, side_x, 35.1)
    arrow(cx, 35.1, cx, 28.0)

    box(side_x, 24.2, side_w, 21.5,
        "Excluded",
        f"No response to any of the five\nClAIR components: n = {counts['excluded']}",
        weight="normal", title_fs=14.5, sub_fs=13.6)

    box(main_x, 1.0, main_w, 23.0,
        "Final ClAIR analytic sample",
        f"n = {counts['analytic']}\nPrimary complete-case regression: n = {counts['primary']}",
        title_fs=15.0, sub_fs=13.3)

    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    fig.savefig(out, dpi=300, transparent=True)
    plt.close(fig)


def _label_segment(ax, x_center, y, value):
    if value <= 0:
        return
    rotation = 90 if value < 4.5 else 0
    fontsize = 7.0 if value < 4.5 else (7.8 if value < 7 else 9.0)
    label = f"{value:.0f}%" if value >= 1 else f"{value:.1f}%"
    ax.text(x_center, y, label,
            ha="center", va="center", fontsize=fontsize,
            color=INK, fontweight="bold", rotation=rotation,
            rotation_mode="anchor", clip_on=True, zorder=5)


def figure3(out, tabs, stats_):
    """Training-confidence figure synchronized to the revised manuscript."""
    fig, axes = plt.subplots(2, 1, figsize=(8.55, 6.32), dpi=300, sharex=True)
    for ax, (key, ct) in zip(axes, tabs.items()):
        st = stats_[key]
        pct = ct.div(ct.sum(axis=1), axis=0) * 100
        ypos = np.arange(len(TRAIN_ORDER))[::-1]
        left = np.zeros(len(TRAIN_ORDER))

        for j, lvl in enumerate(ORDER):
            vals = pct[lvl].reindex(TRAIN_ORDER).values
            ax.barh(ypos, vals, left=left, height=0.58,
                    color=RAMP[j], edgecolor="white", linewidth=1.25,
                    label=lvl if ax is axes[0] else None)
            for y, v, l in zip(ypos, vals, left):
                _label_segment(ax, l + v / 2, y, v)
            left += vals

        ax.set_yticks(ypos)
        ax.set_yticklabels([
            f"{TRAIN_LABEL[t]}\n(n = {int(ct.loc[t].sum())})" for t in TRAIN_ORDER
        ], fontsize=10)
        ax.set_xlim(0, 100)
        ax.set_xticks(range(0, 101, 20))
        ax.tick_params(axis="x", labelbottom=True, labelsize=9.5)
        ax.set_xlabel("Percentage within training category (%)", fontsize=10)
        for spine in ("top", "right", "left"):
            ax.spines[spine].set_visible(False)
        ax.set_axisbelow(True)
        ax.xaxis.grid(True, color="#e6e6e6", linewidth=0.7)
        ax.set_title(st["title"], fontsize=11.5, fontweight="bold",
                     pad=16, loc="left")
        ax.text(0, 1.02,
                f"$\\chi^2$ = {st['chi2']:.2f}, df = {st['df']}, "
                f"Monte-Carlo p {st['p']}, Cramer's V = {st['V']:.3f}  "
                f"(N = {st['n']}; 4 of 15 expected counts < 5)",
                transform=ax.transAxes, fontsize=9, color=MUTED, va="bottom")

    axes[0].legend(loc="lower center", bbox_to_anchor=(0.5, 1.22), ncol=5,
                   frameon=False, fontsize=9.5, handlelength=1.1,
                   columnspacing=1.4)
    fig.tight_layout(h_pad=3.1)
    fig.savefig(out, dpi=300, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--tables", required=True,
                    help="reanalysis outputs directory")
    a = ap.parse_args()
    outdir = Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    T = Path(a.tables)

    figure1(outdir / "Figure1.png",
            {"invited": 3563, "workbook": 314, "excluded": 7,
             "analytic": 307, "primary": 284})

    tests = pd.read_csv(T / "T_training_confidence_tests.csv")
    tabs, stats_ = {}, {}
    for key, title in [
        ("use", "Confidence in using AI, by prior AI training"),
        ("discussion", "Confidence in discussing AI, by prior AI training"),
    ]:
        ct = pd.read_csv(T / f"T_training_by_{key}_confidence.csv", index_col=0)
        if not set(ORDER) & set(map(str, ct.columns)):
            ct.columns = [ORDER[int(float(c)) - 1] for c in ct.columns]
        tabs[key] = ct.reindex(index=TRAIN_ORDER, columns=ORDER).fillna(0)
        r = tests[tests["outcome"] == f"{key} confidence"].iloc[0]
        pv = r["monte_carlo_p_20000"]
        stats_[key] = {
            "title": title,
            "chi2": r["chi2"],
            "df": int(r["df"]),
            "p": "< 0.001" if pv < 0.001 else f"= {pv:.4f}",
            "V": r["cramers_V"],
            "n": int(r["n"]),
        }
    figure3(outdir / "Figure3.png", tabs, stats_)
    print("wrote", outdir / "Figure1.png")
    print("wrote", outdir / "Figure3.png")


if __name__ == "__main__":
    main()
