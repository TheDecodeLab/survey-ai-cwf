#!/usr/bin/env python3
"""Generate manuscript Figures 2, 4, and 5 directly from the survey workbook.

The layout, order, wording, and color palette are synchronized to the figures
embedded in the revised manuscript. Percentages and counts are always computed
from the supplied data rather than hard-coded.
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

COLORS5 = ["#FF8A65", "#FFB74D", "#90CAF9", "#64B5F6", "#42A5F5"]
COLORS4 = ["#FF8A65", "#FFB74D", "#90CAF9", "#42A5F5"]
BLUE = "#42A5F5"
INK = "#111111"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "text.color": INK,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
})


def save(fig, path):
    fig.savefig(path, dpi=300, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


def _stacked_panel(ax, title, panel_letter, series, levels, colors):
    counts = series.value_counts().reindex(levels, fill_value=0)
    pct = counts / counts.sum() * 100
    left = 0.0
    handles = []
    for level, value, color in zip(levels, pct.values, colors):
        bar = ax.barh([0], [value], left=left, height=0.62,
                      color=color, edgecolor="white", linewidth=0.6)
        handles.append(bar[0])
        if value > 0:
            ax.text(left + value / 2, 0, f"{value:.1f}%",
                    ha="center", va="center", fontsize=9.6,
                    fontweight="bold", rotation=90 if value < 5 else 0)
        left += value

    ax.set_xlim(0, 100)
    ax.set_ylim(-0.52, 0.52)
    ax.set_yticks([])
    ax.set_title(title, fontsize=13.8, fontweight="bold", pad=24, loc="center")
    ax.grid(axis="x", alpha=0.25, linestyle="-", linewidth=0.6)
    ax.set_axisbelow(True)
    ax.set_xticks(range(0, 101, 10))
    for spine in ("top", "left", "right"):
        ax.spines[spine].set_visible(False)
    ax.legend(handles, levels, loc="center",
              bbox_to_anchor=(0.5, 1.03), ncol=len(levels),
              frameon=False, fontsize=8.6, handlelength=1.6,
              columnspacing=1.8)
    ax.text(0.006, 1.06, f"({panel_letter})",
            transform=ax.transAxes, ha="left", va="center",
            fontsize=13.5, fontweight="bold", clip_on=False)
    return counts, pct


def figure2(df, out):
    panels = [
        ("Familiar with the use of AI in healthcare", "a", "ai_familiar.q10",
         ["Not at all familiar", "Slightly familiar", "Moderately familiar", "Very familiar", "Extremely familiar"], COLORS5),
        ("Willingness to use AI in healthcare", "b", "ai_willing_to_use.q12",
         ["Not at all willing", "Slightly willing", "Moderately willing", "Very willing", "Extremely willing"], COLORS5),
        ("General opinion of AI in healthcare", "c", "ai_use_gen_opinion.q13",
         ["Very unfavorable", "Unfavorable", "Neither favorable nor unfavorable", "Favorable", "Very favorable"], COLORS5),
        ("Knowledge of AI in healthcare", "d", "ai_knowledge.q17",
         ["Very low", "Low", "Moderate", "High", "Very high"], COLORS5),
        ("Perceived likelihood that AI use will be required in healthcare in the future", "e", "ai_required_likelihood.q16",
         ["Extremely unlikely", "Unlikely", "Likely", "Extremely likely"],
         [COLORS5[0], COLORS5[1], COLORS5[2], COLORS5[4]]),
    ]

    fig, axes = plt.subplots(5, 1, figsize=(11.0, 7.15), sharex=True)
    for ax, (title, letter, col, levels, colors) in zip(axes, panels):
        _stacked_panel(ax, title, letter, df[col].dropna(), levels, colors)
        if ax is not axes[-1]:
            ax.tick_params(axis="x", labelbottom=False, length=0)
            ax.spines["bottom"].set_visible(False)

    axes[-1].set_xlabel("Percentage (%)", fontsize=12, fontweight="bold")
    axes[-1].spines["bottom"].set_visible(True)

    fig.subplots_adjust(left=0.055, right=0.988, top=0.968, bottom=0.075, hspace=0.95)

    fig.canvas.draw()
    left = axes[-1].get_position().x0
    right = axes[-1].get_position().x1
    bottom = axes[-1].get_position().y0
    top = axes[0].get_position().y1
    for x in (left, right):
        fig.add_artist(plt.Line2D([x, x], [bottom, top], transform=fig.transFigure,
                                  color="black", linestyle=(0, (4, 4)), linewidth=1.2))
    save(fig, out)


def workflow_percentages(df, col):
    s = df[col].dropna().astype(str)
    counts = [
        s.eq("Decrease").sum(),
        s.eq("No_impact").sum(),
        s.eq("Increase").sum(),
        s.str.contains(",", regex=False).sum(),
    ]
    return np.array(counts, dtype=float) / len(s) * 100


def option_count(series, phrase):
    return series.dropna().astype(str).str.contains(phrase, case=False, regex=False).sum()


def figure4(df, out):
    workflow_data = [
        ("Number of alerts", "ai_num_alerts.q25"),
        ("Frequency of alerts", "ai_freq_alerts.q26"),
        ("Alarm fatigue", "ai_alarm_fatigue.q27"),
        ("Cognitive fatigue", "ai_cognitive_fatgigue.q28"),
        ("Cognitive overload", "ai_cognitive_overload.q29"),
        ("Information paralysis", "ai_info_paralysis.q30"),
    ]
    cats = ["Decrease", "No impact", "Increase", "More than one answer"]
    concerns = [
        ("Reliability\nand accuracy\nof AI systems", "reliability and accuracy of AI systems"),
        ("Lack of transparency\nin AI algorithms", "lack of transparency in AI algorithms"),
        ("Ethical implications\nand decision-making\naccountability", "ethical implications and decision-making accountability"),
        ("Biases or unequal\nperformance of AI\nfor certain patient\npopulations", "biases or unequal performance of AI for certain patient populations"),
        ("Impact on healthcare\nprofessionals' roles\nand responsibilities", "impact on healthcare professionals' roles and responsibilities"),
        ("Patient privacy\nand data security", "patient privacy and data security"),
        ("Efficiencies of AI\ntools causing\nredundancies or\njob losses", "redundancies or job losses"),
    ]

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(11.0, 7.75),
        gridspec_kw={"height_ratios": [1.32, 0.92]}
    )

    y = np.arange(len(workflow_data))
    vals = np.vstack([workflow_percentages(df, col) for _, col in workflow_data])
    left = np.zeros(len(workflow_data))
    for j, (cat, color) in enumerate(zip(cats, COLORS4)):
        ax1.barh(y, vals[:, j], left=left, height=0.60,
                 color=color, edgecolor="white", linewidth=0.6, label=cat)
        for i, v in enumerate(vals[:, j]):
            if v > 0:
                ax1.text(left[i] + v / 2, i, f"{v:.1f}%",
                         ha="center", va="center", fontsize=8.8,
                         fontweight="bold", rotation=90 if v < 3 else 0)
        left += vals[:, j]

    ax1.set_xlim(0, 100)
    ax1.set_xticks(range(0, 101, 10))
    ax1.set_yticks(y, [label for label, _ in workflow_data], fontsize=10)
    ax1.set_xlabel("Percentage (%)", fontsize=12, fontweight="bold")
    ax1.set_ylabel("Clinical workflow", fontsize=12, fontweight="bold")
    ax1.set_title("Clinical workflow", fontsize=16, fontweight="bold", pad=20)
    ax1.grid(axis="x", alpha=0.30, linestyle="-", linewidth=0.5)
    ax1.set_axisbelow(True)
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.legend(loc="upper center", bbox_to_anchor=(0.5, 1.06), ncol=4,
               fontsize=11, frameon=False)
    ax1.text(-0.14, 1.07, "(a)", transform=ax1.transAxes,
             fontsize=16, fontweight="bold", va="top")

    s = df["ai_concerns.q32"]
    n = s.notna().sum()
    counts = [option_count(s, phrase) for _, phrase in concerns]
    pct = np.asarray(counts, dtype=float) / n * 100
    x = 1.3 * np.arange(len(concerns))
    bars = ax2.bar(x, pct, color=BLUE, alpha=0.80)
    for bar, p, c in zip(bars, pct, counts):
        ax2.text(bar.get_x() + bar.get_width() / 2, p + 1,
                 f"{p:.1f}% ({c})", ha="center", va="bottom",
                 fontsize=9.6, fontweight="bold")
    ax2.set_ylim(0, 100)
    ax2.set_yticks(range(0, 101, 20))
    ax2.set_ylabel("Percent", fontsize=12, fontweight="bold")
    ax2.set_xticks(x, [label for label, _ in concerns], fontsize=8.4)
    ax2.set_title("Potential concerns with AI in healthcare",
                  fontsize=16, fontweight="bold", pad=10)
    ax2.grid(axis="y", alpha=0.30, linestyle="-", linewidth=0.5)
    ax2.set_axisbelow(True)
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.text(-0.14, 1.05, "(b)", transform=ax2.transAxes,
             fontsize=16, fontweight="bold", va="top")

    fig.subplots_adjust(left=0.16, right=0.985, top=0.96, bottom=0.09, hspace=0.30)
    save(fig, out)


def figure5(df, out):
    items = [
        ("Improved efficiency in\nhealthcare documentation work", "Improved efficiency in healthcare documentation work"),
        ("Increased efficiency\nin healthcare delivery", "Increased efficiency in healthcare delivery"),
        ("Improved diagnostic accuracy", "Improved diagnostic accuracy"),
        ("Improved medical\ntraining or simulations", "Improved medical training or simulations"),
        ("Enhanced patient outcomes", "Enhanced patient outcomes"),
        ("Enabling personalized medicine", "Enabling personalized medicine"),
        ("Improved patient\nexperience and engagement", "Improved patient experience and engagement"),
        ("Enhanced surgical\ntraining planning", "Enhanced surgical training planning"),
        ("Other benefits of AI\nin healthcare", "other benefits of AI in healthcare"),
    ]
    s = df["ai_benefits.q31"]
    n = s.notna().sum()
    counts = [option_count(s, phrase) for _, phrase in items]
    pct = np.asarray(counts, dtype=float) / n * 100

    fig, ax = plt.subplots(figsize=(12.0, 5.0))
    y = np.arange(len(items))
    bars = ax.barh(y, pct, color=BLUE, alpha=0.80)
    for bar, p, c in zip(bars, pct, counts):
        ax.text(p + 1, bar.get_y() + bar.get_height() / 2,
                f"{p:.1f}% ({c})", ha="left", va="center",
                fontsize=10, fontweight="bold")

    ax.set_xlim(0, 85)
    ax.set_xticks(range(0, 81, 20))
    ax.set_xlabel("Percent", fontsize=12, fontweight="bold")
    ax.set_yticks(y, [label for label, _ in items], fontsize=10)
    ax.set_title("Potential benefits with using AI in healthcare",
                 fontsize=16, fontweight="bold", pad=10)
    ax.grid(axis="x", alpha=0.30, linestyle="-", linewidth=0.5)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    save(fig, out)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True)
    p.add_argument("--outdir", default="figures/final")
    a = p.parse_args()
    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    df = pd.read_excel(a.data)

    figure2(df, out / "Figure2.png")
    figure4(df, out / "Figure4.png")
    figure5(df, out / "Figure5.png")
    print("wrote", out / "Figure2.png", out / "Figure4.png", out / "Figure5.png", sep="\n")


if __name__ == "__main__":
    main()
