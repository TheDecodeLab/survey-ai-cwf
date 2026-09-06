#!/usr/bin/env python3
"""Generate manuscript Figures 2, 4, and 5 directly from the source workbook."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

COLORS5 = ["#287FB5", "#FF7F0E", "#2CA02C", "#D92525", "#9467BD"]
INK = "#111111"


def save(fig, path):
    fig.savefig(path, dpi=400, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)


def figure2(df, out):
    panels = [
        ("(a) Familiarity with AI in healthcare", "ai_familiar.q10",
         ["Not at all familiar", "Slightly familiar", "Moderately familiar", "Very familiar", "Extremely familiar"]),
        ("(b) Willingness to use AI in healthcare", "ai_willing_to_use.q12",
         ["Not at all willing", "Slightly willing", "Moderately willing", "Very willing", "Extremely willing"]),
        ("(c) General opinion of AI in healthcare", "ai_use_gen_opinion.q13",
         ["Very unfavorable", "Unfavorable", "Neither favorable nor unfavorable", "Favorable", "Very favorable"]),
        ("(d) Self-rated knowledge of AI in healthcare", "ai_knowledge.q17",
         ["Very low", "Low", "Moderate", "High", "Very high"]),
        ("(e) Perceived likelihood that AI will be required in healthcare in the future", "ai_required_likelihood.q16",
         ["Extremely unlikely", "Unlikely", "Likely", "Extremely likely"]),
    ]
    fig, axes = plt.subplots(5, 1, figsize=(13.0, 10.4), sharex=True)
    for ax, (title, col, levels) in zip(axes, panels):
        counts = df[col].value_counts().reindex(levels, fill_value=0)
        pct = counts / counts.sum() * 100
        left = 0.0
        handles = []
        for i, (level, value) in enumerate(pct.items()):
            bar = ax.barh([0], [value], left=left, height=.62, color=COLORS5[i], edgecolor="white")
            handles.append(bar[0])
            rotation = 90 if value < 4.5 else 0
            ax.text(left + value / 2, 0, f"{value:.1f}%", ha="center", va="center",
                    fontsize=10, fontweight="bold", rotation=rotation, color=INK)
            left += value
        ax.set_xlim(0, 100); ax.set_yticks([]); ax.set_title(title, loc="left", fontsize=13, fontweight="bold")
        ax.grid(axis="x", alpha=.25); ax.set_axisbelow(True)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.legend(handles, levels, loc="upper center", bbox_to_anchor=(.5, 1.04), ncol=len(levels),
                  frameon=False, fontsize=8.6)
    axes[-1].set_xlabel("Percentage (%)", fontsize=12)
    fig.tight_layout(h_pad=1.35)
    save(fig, out)


def workflow_percentages(df, col):
    s = df[col].dropna().astype(str)
    counts = [s.eq("Decrease").sum(), s.eq("No_impact").sum(), s.eq("Increase").sum(), s.str.contains(",", regex=False).sum()]
    return np.array(counts) / len(s) * 100


def option_count(series, phrase):
    return series.dropna().astype(str).str.contains(phrase, case=False, regex=False).sum()


def figure4(df, out):
    workflows = [
        ("Number of alerts", "ai_num_alerts.q25"), ("Frequency of alerts", "ai_freq_alerts.q26"),
        ("Alarm fatigue", "ai_alarm_fatigue.q27"), ("Cognitive fatigue", "ai_cognitive_fatgigue.q28"),
        ("Cognitive overload", "ai_cognitive_overload.q29"), ("Information paralysis", "ai_info_paralysis.q30")]
    cats = ["Decrease", "No impact", "Increase", "More than one answer"]
    colors = ["#E88759", "#F2B34B", "#8BC5E8", "#3278B9"]
    concerns = [
        ("Reliability\nand accuracy\nof AI systems", "reliability and accuracy of AI systems"),
        ("Lack of transparency\nin AI algorithms", "lack of transparency in AI algorithms"),
        ("Ethical implications\nand decision-making\naccountability", "ethical implications and decision-making accountability"),
        ("Biases or unequal\nperformance of AI\nfor certain patient\npopulations", "biases or unequal performance of AI for certain patient populations"),
        ("Impact on healthcare\nprofessionals' roles\nand responsibilities", "impact on healthcare professionals' roles and responsibilities"),
        ("Patient privacy\nand data security", "patient privacy and data security"),
        ("Efficiencies of AI\ntools causing\nredundancies or\njob losses", "redundancies or job losses")]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11.5, 9.7), gridspec_kw={"height_ratios":[1.2, 1]})
    y = np.arange(len(workflows)); left = np.zeros(len(workflows))
    vals = np.vstack([workflow_percentages(df, c) for _, c in workflows])
    for j, cat in enumerate(cats):
        ax1.barh(y, vals[:, j], left=left, color=colors[j], edgecolor="white", label=cat)
        for i, v in enumerate(vals[:, j]):
            if v > 0:
                ax1.text(left[i] + v/2, i, f"{v:.1f}%", ha="center", va="center",
                         fontsize=7.2 if v < 4 else 8.5, rotation=90 if v < 4 else 0,
                         fontweight="bold" if v < 4 else "normal")
        left += vals[:, j]
    ax1.set_yticks(y, [x[0] for x in workflows]); ax1.set_xlim(0,100); ax1.set_xlabel("Percentage (%)")
    ax1.set_title("(a) Clinical workflow", loc="left", fontweight="bold"); ax1.legend(ncol=4, frameon=False, loc="upper center", bbox_to_anchor=(.5,1.12))
    ax1.grid(axis="x", alpha=.25); ax1.set_axisbelow(True); ax1.spines[["top","right"]].set_visible(False)
    s = df["ai_concerns.q32"]; n = s.notna().sum(); counts = [option_count(s,p) for _,p in concerns]; pct=np.array(counts)/n*100
    x=np.arange(len(concerns)); bars=ax2.bar(x,pct,color="#5AA6D6")
    for b,p,c in zip(bars,pct,counts): ax2.text(b.get_x()+b.get_width()/2,p+1,f"{p:.1f}% ({c})",ha="center",fontsize=8.5,fontweight="bold")
    ax2.set_ylim(0,100); ax2.set_xticks(x,[x[0] for x in concerns],fontsize=7.2); ax2.set_ylabel("Percent")
    ax2.set_title("(b) Potential concerns with AI in healthcare",loc="left",fontweight="bold"); ax2.grid(axis="y",alpha=.25); ax2.set_axisbelow(True); ax2.spines[["top","right"]].set_visible(False)
    fig.tight_layout(h_pad=2.2); save(fig,out)


def figure5(df, out):
    items = [
        ("Other benefits of AI in healthcare", "other benefits of AI in healthcare"),
        ("Enhanced surgical training/planning", "Enhanced surgical training planning"),
        ("Improved patient experience and engagement", "Improved patient experience and engagement"),
        ("Enabling personalized medicine", "Enabling personalized medicine"),
        ("Enhanced patient outcomes", "Enhanced patient outcomes"),
        ("Improved medical training or simulations", "Improved medical training or simulations"),
        ("Improved diagnostic accuracy", "Improved diagnostic accuracy"),
        ("Increased efficiency in healthcare delivery", "Increased efficiency in healthcare delivery"),
        ("Improved efficiency in healthcare documentation work", "Improved efficiency in healthcare documentation work")]
    s=df["ai_benefits.q31"]; n=s.notna().sum(); counts=[option_count(s,p) for _,p in items]; pct=np.array(counts)/n*100
    fig,ax=plt.subplots(figsize=(9.3,5.0)); y=np.arange(len(items)); bars=ax.barh(y,pct,color="#5AA6D6")
    for b,p,c in zip(bars,pct,counts): ax.text(p+1,b.get_y()+b.get_height()/2,f"{p:.1f}% ({c})",va="center",fontsize=9,fontweight="bold")
    ax.set_xlim(0,85); ax.set_yticks(y,[x[0] for x in items],fontsize=9); ax.set_xlabel("Percent")
    ax.set_title("Potential benefits with using AI in healthcare",fontweight="bold"); ax.grid(axis="x",alpha=.25); ax.set_axisbelow(True); ax.spines[["top","right"]].set_visible(False)
    fig.tight_layout(); save(fig,out)


def main():
    p=argparse.ArgumentParser(); p.add_argument("--data",required=True); p.add_argument("--outdir",default="figures/final"); a=p.parse_args()
    out=Path(a.outdir); out.mkdir(parents=True,exist_ok=True); df=pd.read_excel(a.data)
    figure2(df,out/"Figure2.png"); figure4(df,out/"Figure4.png"); figure5(df,out/"Figure5.png")
    print("wrote", out/"Figure2.png", out/"Figure4.png", out/"Figure5.png", sep="\n")


if __name__ == "__main__": main()
