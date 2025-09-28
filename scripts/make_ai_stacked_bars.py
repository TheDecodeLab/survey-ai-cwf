#!/usr/bin/env python3
"""
Recreate a 100% stacked horizontal bar chart for three AI-related survey items.

Outputs:
  - outputs/figures/q10_12_13_stacked_bars.png
  - outputs/figures/q10_12_13_stacked_bars.pdf

This script intentionally avoids heavy dependencies; it uses only matplotlib.
"""

import os
from typing import List, Dict

import matplotlib.pyplot as plt


def ensure_output_dirs(output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)


def compute_segment_centers(cumulative: List[float], widths: List[float]) -> List[float]:
    centers: List[float] = []
    for left, w in zip(cumulative, widths):
        centers.append(left + w / 2.0)
    return centers


def draw_stacked_bars(
    ax: plt.Axes,
    questions: List[str],
    data: Dict[str, List[float]],
    category_labels: List[str],
    colors: List[str],
) -> None:
    y_positions = list(range(len(questions)))

    # Draw bars
    for y, q in zip(y_positions, questions):
        shares = data[q]

        lefts: List[float] = []
        cumulative_left = 0.0
        for share in shares:
            lefts.append(cumulative_left)
            cumulative_left += share

        # Plot each segment
        for left, width, color in zip(lefts, shares, colors):
            ax.barh(y, width, left=left, color=color, edgecolor="white", height=0.6)

        # Add percentage labels for every segment.
        # If a segment is very narrow, place the label just above the bar.
        centers = compute_segment_centers(lefts, shares)
        for center, width, share in zip(centers, shares, shares):
            label = f"{share:.1f}%"
            if width >= 6.0:
                ax.text(
                    center,
                    y,
                    label,
                    va="center",
                    ha="center",
                    fontsize=9,
                    color="#0b214a",
                )
            else:
                ax.text(
                    center,
                    y + 0.00,
                    label,
                    va="center",
                    ha="center",
                    rotation=90,
                    fontsize=9,
                    color="#0b214a",
                )

    # Axes formatting
    ax.set_yticks(y_positions, questions)
    ax.set_xlim(0, 100)
    ax.set_xticks(range(0, 101, 10))
    ax.set_xlabel("Percent of respondents")
    ax.grid(axis="x", linestyle="-", linewidth=0.6, color="#e6e6e6")
    ax.set_axisbelow(True)
    # Reverse the y-axis so the last item (Familiarity) appears at the bottom
    ax.invert_yaxis()

    # Legend: use generic polarity labels in left-to-right order
    ax.legend(
        handles=[
            plt.Rectangle((0, 0), 1, 1, color=c) for c in colors
        ],
        labels=category_labels,
        loc="center left",
        bbox_to_anchor=(1.0, 0.5),  # anchor to the right edge of the axes
        frameon=False,
        title="Response scale",
        borderaxespad=0.5,
    )


def main() -> None:
    # Data read from the provided figure
    # Each list sums to ~100 and follows the order from negative to positive
    questions = [
        "General opinion of AI",
        "Willingness to use AI",
        "Familiarity with AI",
    ]

    data: Dict[str, List[float]] = {
        # Very unfavorable, Unfavorable, Neither, Favorable, Very favorable
        "General opinion of AI": [3.6, 8.2, 30.6, 47.0, 10.5],
        # Not at all willing, Slightly willing, Moderately willing, Very willing, Extremely willing
        "Willingness to use AI": [2.3, 13.4, 34.1, 33.1, 17.1],
        # Not at all familiar, Slightly familiar, Moderately familiar, Very familiar, Extremely familiar
        "Familiarity with AI": [13.0, 45.9, 28.7, 10.1, 2.3],
    }

    # Colors: light (negative) to dark (positive)
    colors = [
        "#d7e3f3",  # very negative / not at all
        "#aac4e6",
        "#7ea6d9",
        "#4f80c1",
        "#2b57a4",  # very positive / extremely
    ]

    # Generic labels for legend (wording varies by question, keep polarity consistent)
    category_labels = [
        "Most negative",
        "Negative",
        "Neutral",
        "Positive",
        "Most positive",
    ]

    # Figure
    plt.rcParams.update({"figure.dpi": 150})
    # Give the chart substantially more horizontal space
    fig, ax = plt.subplots(figsize=(10, 3), constrained_layout=True)
    draw_stacked_bars(ax, questions, data, category_labels, colors)
    fig.suptitle("Attitudes toward AI: opinion, willingness, and familiarity", y=0.98)

    # Save
    output_dir = os.path.join("outputs", "figures")
    ensure_output_dirs(output_dir)
    fig_out_png = os.path.join(output_dir, "q10_12_13_stacked_bars.png")
    fig_out_pdf = os.path.join(output_dir, "q10_12_13_stacked_bars.pdf")
    fig.savefig(fig_out_png)
    fig.savefig(fig_out_pdf)
    print(f"Saved figure to:\n  {fig_out_png}\n  {fig_out_pdf}")


if __name__ == "__main__":
    main()


