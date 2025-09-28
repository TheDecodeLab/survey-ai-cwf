#!/usr/bin/env python3
"""
Build a Sankey diagram similar to the provided mockup:

Columns:
  - Training: Yes / Unsure / No
  - Confidence to use AI tools: Not at all, Slightly, Moderately, Very, Extremely
  - Confidence to discuss AI tools: Not at all, Slightly, Moderately, Very, Extremely

Input data: CSV at data/sankey/flows.csv with columns [source,target,value]
  - Example rows map flows from a left column node to a middle column node,
    and from a middle column node to a right column node.

Outputs:
  - outputs/figures/sankey_ai.png
  - outputs/figures/sankey_ai.pdf
  - outputs/figures/sankey_ai.html (interactive)

Requires: plotly
"""

import os
import csv
from typing import Dict, List, Tuple

import plotly.graph_objects as go


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(REPO_ROOT, "data", "sankey", "flows.csv")
OUTPUT_DIR = os.path.join(REPO_ROOT, "outputs", "figures")


def ensure_output_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def read_flows(csv_path: str) -> List[Tuple[str, str, float]]:
    flows: List[Tuple[str, str, float]] = []
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            source = row["source"].strip()
            target = row["target"].strip()
            value = float(row["value"])  # value can be counts or percentages
            flows.append((source, target, value))
    return flows


def write_default_flows(csv_path: str) -> None:
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    rows = [
        ("source", "target", "value"),
        ("Yes", "Extremely confident (use)", 3),
        ("Yes", "Very confident (use)", 8),
        ("Yes", "Moderately confident (use)", 12),
        ("Yes", "Slightly confident (use)", 6),
        ("Yes", "Not at all confident (use)", 3),
        ("Unsure", "Extremely confident (use)", 1),
        ("Unsure", "Very confident (use)", 6),
        ("Unsure", "Moderately confident (use)", 20),
        ("Unsure", "Slightly confident (use)", 12),
        ("Unsure", "Not at all confident (use)", 6),
        ("No", "Extremely confident (use)", 1),
        ("No", "Very confident (use)", 7),
        ("No", "Moderately confident (use)", 25),
        ("No", "Slightly confident (use)", 24),
        ("No", "Not at all confident (use)", 32),
        ("Extremely confident (use)", "Extremely confident (discuss)", 4),
        ("Very confident (use)", "Extremely confident (discuss)", 3),
        ("Moderately confident (use)", "Extremely confident (discuss)", 1),
        ("Slightly confident (use)", "Extremely confident (discuss)", 1),
        ("Not at all confident (use)", "Extremely confident (discuss)", 1),
        ("Extremely confident (use)", "Very confident (discuss)", 6),
        ("Very confident (use)", "Very confident (discuss)", 13),
        ("Moderately confident (use)", "Very confident (discuss)", 8),
        ("Slightly confident (use)", "Very confident (discuss)", 5),
        ("Not at all confident (use)", "Very confident (discuss)", 3),
        ("Extremely confident (use)", "Moderately confident (discuss)", 4),
        ("Very confident (use)", "Moderately confident (discuss)", 14),
        ("Moderately confident (use)", "Moderately confident (discuss)", 22),
        ("Slightly confident (use)", "Moderately confident (discuss)", 11),
        ("Not at all confident (use)", "Moderately confident (discuss)", 7),
        ("Extremely confident (use)", "Slightly confident (discuss)", 2),
        ("Very confident (use)", "Slightly confident (discuss)", 7),
        ("Moderately confident (use)", "Slightly confident (discuss)", 14),
        ("Slightly confident (use)", "Slightly confident (discuss)", 16),
        ("Not at all confident (use)", "Slightly confident (discuss)", 18),
        ("Extremely confident (use)", "Not at all confident (discuss)", 1),
        ("Very confident (use)", "Not at all confident (discuss)", 2),
        ("Moderately confident (use)", "Not at all confident (discuss)", 7),
        ("Slightly confident (use)", "Not at all confident (discuss)", 9),
        ("Not at all confident (use)", "Not at all confident (discuss)", 12),
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)
    print(f"Created default flows CSV at {csv_path}")

def build_nodes_and_links(flows: List[Tuple[str, str, float]]):
    # Define ordered columns and desired node order within each column
    col_left = ["Yes", "Unsure", "No"]
    col_mid = [
        "Extremely confident (use)",
        "Very confident (use)",
        "Moderately confident (use)",
        "Slightly confident (use)",
        "Not at all confident (use)",
    ]
    col_right = [
        "Extremely confident (discuss)",
        "Very confident (discuss)",
        "Moderately confident (discuss)",
        "Slightly confident (discuss)",
        "Not at all confident (discuss)",
    ]

    all_nodes_ordered = col_left + col_mid + col_right

    # Create clean display labels (remove parenthetical additions)
    def clean_label(label: str) -> str:
        if " (use)" in label:
            return label.replace(" (use)", "")
        elif " (discuss)" in label:
            return label.replace(" (discuss)", "")
        return label
    
    display_labels = [clean_label(name) for name in all_nodes_ordered]

    node_to_index: Dict[str, int] = {name: i for i, name in enumerate(all_nodes_ordered)}

    # Assign node positions by column
    x_positions: List[float] = []
    y_positions: List[float] = []
    palette_nodes = [
        "#5b2a86",  # left col dark purple variants
        "#3a66a3",
        "#6a4c93",
        "#b8d1ea",  # mid and right use teal/green/blue gradients
        "#a7dba0",
        "#6ec0bf",
        "#6b8ec1",
        "#4b5e9a",
        "#e5f2bf",
        "#bfe6a8",
        "#94cfc6",
        "#7aa1cf",
        "#5a6dab",
    ]
    # Expand/cycle palette to length of nodes
    while len(palette_nodes) < len(all_nodes_ordered):
        palette_nodes += palette_nodes
    node_colors = palette_nodes[: len(all_nodes_ordered)]

    # y spacing helper for each column
    def positions_for_column(n: int) -> List[float]:
        if n == 1:
            return [0.5]
        step = 1.0 / (n + 1)
        return [step * (i + 1) for i in range(n)]

    y_left = positions_for_column(len(col_left))
    y_mid = positions_for_column(len(col_mid))
    y_right = positions_for_column(len(col_right))

    for name in all_nodes_ordered:
        if name in col_left:
            x_positions.append(0.02)
            y_positions.append(y_left[col_left.index(name)])
        elif name in col_mid:
            x_positions.append(0.48)
            y_positions.append(y_mid[col_mid.index(name)])
        else:
            # Position right column nodes to allow text on the right side
            x_positions.append(0.85)
            y_positions.append(y_right[col_right.index(name)])

    # Build link lists
    link_source: List[int] = []
    link_target: List[int] = []
    link_value: List[float] = []
    link_color: List[str] = []

    for s, t, v in flows:
        link_source.append(node_to_index[s])
        link_target.append(node_to_index[t])
        link_value.append(v)
        link_color.append("rgba(107, 109, 171, 0.45)")

    nodes = {
        "labels": display_labels,
        "colors": node_colors,
        "x": x_positions,
        "y": y_positions,
    }
    links = {
        "source": link_source,
        "target": link_target,
        "value": link_value,
        "color": link_color,
    }
    return nodes, links


def make_figure(nodes, links) -> go.Figure:
    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="snap",
                node=dict(
                    pad=12,
                    thickness=16,
                    label=nodes["labels"],
                    color=nodes["colors"],
                    x=nodes["x"],
                    y=nodes["y"],
                ),
                link=dict(
                    source=links["source"],
                    target=links["target"],
                    value=links["value"],
                    color=links["color"],
                ),
            )
        ]
    )
    fig.update_layout(
        font=dict(size=14, color="black"),
        width=1400,  # Increased width to accommodate right column text
        height=700,
        margin=dict(l=120, r=120, t=60, b=40),  # Increased left and right margins for text space
        title=dict(
            text="Training and confidence with AI tools",
            font=dict(size=16, color="black")
        ),
    )
    
    # Add annotations for left column labels positioned to the left of their nodes
    left_column_indices = list(range(0, 3))  # Left column nodes (indices 0-2)
    for node_idx in left_column_indices:
        if node_idx < len(nodes["labels"]):
            # Calculate the exact position to the left of the node
            node_x = nodes["x"][node_idx]
            node_y = nodes["y"][node_idx]
            
            # Add annotation positioned to the left of the node
            fig.add_annotation(
                x=node_x - 0.06,  # Offset to position text to the left of the node
                y=node_y,
                text=nodes["labels"][node_idx],
                showarrow=False,
                font=dict(size=14, color="black"),
                xanchor="right",
                yanchor="middle",
                bgcolor="rgba(255,255,255,0.95)",
                bordercolor="rgba(0,0,0,0)",
                borderwidth=0,
                borderpad=6
            )
    
    # Add annotations for right column labels positioned to the right of their nodes
    right_column_indices = list(range(8, 13))  # Right column nodes (indices 8-12)
    for node_idx in right_column_indices:
        if node_idx < len(nodes["labels"]):
            # Calculate the exact position to the right of the node
            node_x = nodes["x"][node_idx]
            node_y = nodes["y"][node_idx]
            
            # Add annotation positioned to the right of the node with proper spacing
            fig.add_annotation(
                x=node_x + 0.06,  # Offset to position text to the right of the node
                y=node_y,
                text=nodes["labels"][node_idx],
                showarrow=False,
                font=dict(size=14, color="black"),
                xanchor="left",
                yanchor="middle",
                bgcolor="rgba(255,255,255,0.95)",
                bordercolor="rgba(0,0,0,0)",
                borderwidth=0,
                borderpad=6
            )
    
    # Hide the original labels for left and right column nodes to avoid duplication
    updated_labels = nodes["labels"].copy()
    for i in left_column_indices + right_column_indices:
        if i < len(updated_labels):
            updated_labels[i] = ""  # Hide original label
    
    # Update the figure with hidden labels for right column
    fig.data[0].node.label = updated_labels
    return fig


def main() -> None:
    ensure_output_dir(OUTPUT_DIR)
    if not os.path.exists(DATA_PATH):
        write_default_flows(DATA_PATH)

    flows = read_flows(DATA_PATH)
    nodes, links = build_nodes_and_links(flows)
    fig = make_figure(nodes, links)

    out_png = os.path.join(OUTPUT_DIR, "sankey_ai.png")
    out_pdf = os.path.join(OUTPUT_DIR, "sankey_ai.pdf")
    out_html = os.path.join(OUTPUT_DIR, "sankey_ai.html")

    # Static image export requires kaleido; if unavailable, skip PNG/PDF silently.
    try:
        fig.write_image(out_png, scale=2)
        fig.write_image(out_pdf)
        print(f"Saved {out_png} and {out_pdf}")
    except Exception as e:
        print(f"Note: static export skipped ({e}). The interactive HTML is still saved.")

    fig.write_html(out_html, include_plotlyjs="cdn")
    print(f"Saved {out_html}")


if __name__ == "__main__":
    main()


