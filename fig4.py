#!/usr/bin/env python3
"""
Figure 4: Knowledge of AI in healthcare
Horizontal stacked bar chart showing knowledge levels about AI in healthcare

To run: conda activate eda && python fig4.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def create_ai_knowledge_chart():
    """Create horizontal stacked bar chart for AI knowledge levels"""
    
    # Read the survey data
    df = pd.read_excel('data/S2_Survey_Data.xlsx', sheet_name='Sheet 1')
    
    # Get AI knowledge counts and percentages (excluding missing data)
    knowledge_counts = df['ai_knowledge.q17'].value_counts(dropna=True)
    total = df['ai_knowledge.q17'].notna().sum()  # Only count non-missing responses
    knowledge_pct = (knowledge_counts / total * 100).round(1)
    
    # Define the order and colors for the chart (matching the reference image)
    categories = [
        'Very low',
        'Low', 
        'Moderate',
        'High',
        'Very high'
    ]
    
    # Create color palette (orange to blue gradient)
    colors = [
        '#FF8A65',  # Dark orange
        '#FFB74D',  # Light orange
        '#90CAF9',  # Light blue
        '#64B5F6',  # Medium blue
        '#42A5F5'   # Dark blue
    ]
    
    # Get percentages in the correct order
    percentages = [knowledge_pct.get(cat, 0) for cat in categories]
    
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
            # Rotate text for very small segments (like "Very high" at 1.7%)
            rotation = 90 if percentage < 5 else 0
            ax.text(left + percentage/2, 0, f'{percentage}%', 
                   ha='center', va='center', fontsize=10, fontweight='bold',
                   rotation=rotation)
        
        left += percentage
    
    # Customize the chart
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.5, 0.5)
    ax.set_xlabel('Percentage (%)', fontsize=12, fontweight='bold')
    ax.set_title('Knowledge of AI in healthcare', 
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
                      bbox_to_anchor=(0.5, 0.97), ncol=5, fontsize=10, 
                      frameon=False)
    
    # Adjust layout to make room for legend below
    plt.tight_layout()
    # plt.subplots_adjust(top=0.9)  # Make room for legend below
    
    # Save the figure
    plt.savefig('fig4_ai_knowledge.png', dpi=300, bbox_inches='tight')
    plt.savefig('fig4_ai_knowledge.pdf', bbox_inches='tight')
    
    # Show the figure
    plt.show()
    
    # Print summary statistics
    print("AI Knowledge Distribution:")
    print("=" * 40)
    for category, percentage in zip(categories, percentages):
        print(f"{category}: {percentage}%")
    
    print(f"\nTotal participants: {total}")
    print(f"Sum of percentages: {sum(percentages):.1f}%")

if __name__ == "__main__":
    create_ai_knowledge_chart()
