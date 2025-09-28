#!/usr/bin/env python3
"""
Figure 11: Views regarding the relevance of AI in healthcare on viable pre-med education options
Horizontal stacked bar chart showing agreement levels for encouraging non-biological disciplines as pre-med options

To run: conda activate eda && python fig11.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def create_premed_views_chart():
    """Create horizontal stacked bar chart for pre-med education views"""
    
    # Read the survey data
    df = pd.read_excel('data/S2_Survey_Data.xlsx', sheet_name='Sheet 1')
    
    # Get pre-med agreement counts and percentages (excluding missing data)
    agreement_counts = df['agree_stmt_encourage_nonbio.q39'].value_counts(dropna=True)
    total = df['agree_stmt_encourage_nonbio.q39'].notna().sum()  # Only count non-missing responses
    agreement_pct = (agreement_counts / total * 100).round(1)
    
    # Define the order and colors for the chart (matching the reference image)
    categories = [
        'Strongly Disagree',
        'Disagree', 
        'Agree',
        'Strongly Agree'
    ]
    
    # Create color palette (reddish-brown to blue gradient as shown in reference)
    colors = [
        '#C0504D',  # Reddish-brown (Strongly Disagree)
        '#F79646',  # Orange (Disagree)
        '#66B3FF',  # Light blue (Agree)
        '#4472C4'   # Darker blue (Strongly Agree)
    ]
    
    # Get percentages in the correct order
    percentages = [agreement_pct.get(cat, 0) for cat in categories]
    
    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(11, 2))
    
    # Create horizontal stacked bar
    left = 0
    bars = []
    
    for i, (category, percentage, color) in enumerate(zip(categories, percentages, colors)):
        bar = ax.barh(0, percentage, left=left, height=0.6, 
                     color=color, edgecolor='white', linewidth=0.5)
        bars.append(bar)
        
        # Add percentage label in the middle of each segment
        if percentage > 0:
            # Rotate text for very small segments (like "Strongly Disagree" at 2.4%)
            rotation = 90 if percentage < 5 else 0
            ax.text(left + percentage/2, 0, f'{percentage}%', 
                   ha='center', va='center', fontsize=10, fontweight='bold',
                   rotation=rotation)
        
        left += percentage
    
    # Customize the chart
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.5, 0.5)
    ax.set_xlabel('Percentage (%)', fontsize=12, fontweight='bold')
    ax.set_title('Views regarding the relevance of AI in healthcare on viable pre-med education options', 
                fontsize=14, fontweight='bold', pad=20)
    
    # Remove y-axis ticks and labels
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(True)
    
    # Add x-axis grid
    ax.grid(axis='x', alpha=0.3, linestyle='-', linewidth=0.5)
    ax.set_xticks(range(0, 101, 10))
    
    # Create legend (centered, no box)
    legend_elements = [plt.Rectangle((0,0),1,1, facecolor=color, edgecolor='white') 
                      for color in colors]
    # Position legend manually with specific coordinates
    legend = ax.legend(legend_elements, categories, loc='center', 
                      bbox_to_anchor=(0.5, 0.97), ncol=4, fontsize=10, 
                      frameon=False)
    
    # Adjust layout to make room for legend below
    plt.tight_layout()
    # plt.subplots_adjust(top=0.9)  # Make room for legend below
    
    # Save the figure
    plt.savefig('fig11_premed_views.png', dpi=300, bbox_inches='tight')
    plt.savefig('fig11_premed_views.pdf', bbox_inches='tight')
    
    # Show the figure
    plt.show()
    
    # Print summary statistics
    print("Pre-med Education Views Distribution:")
    print("=" * 50)
    for category, percentage in zip(categories, percentages):
        print(f"{category}: {percentage}%")
    
    print(f"\nTotal participants: {total}")
    print(f"Sum of percentages: {sum(percentages):.1f}%")
    
    # Additional insights
    agree_total = percentages[2] + percentages[3]  # Agree + Strongly Agree
    disagree_total = percentages[0] + percentages[1]  # Strongly Disagree + Disagree
    print(f"\nKey Insights:")
    print(f"Agree or Strongly Agree: {agree_total:.1f}%")
    print(f"Disagree or Strongly Disagree: {disagree_total:.1f}%")
    
    # Add the statement being evaluated
    print(f"\nStatement evaluated:")
    print(f"'The medical field should encourage non-biological disciplines")
    print(f"(such as math and computer science) as viable pre-med options'")

if __name__ == "__main__":
    create_premed_views_chart()
