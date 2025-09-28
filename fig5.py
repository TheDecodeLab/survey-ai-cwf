#!/usr/bin/env python3
"""
Figure 5: Confidence using or discussing the use of AI in healthcare
Horizontal stacked bar chart showing confidence levels for AI use and discussion abilities

To run: conda activate eda && python fig5.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def create_ai_confidence_chart():
    """Create horizontal stacked bar chart for AI confidence levels"""
    
    # Read the survey data
    df = pd.read_excel('data/S2_Survey_Data.xlsx', sheet_name='Sheet 1')
    
    # Define confidence aspects and their corresponding columns
    confidence_data = [
        ('Ability to use \nAI in healthcare', 'ai_use_confidence.q19'),
        ('Ability to \ndiscuss AI', 'ai_discuss_confidence.q20')
    ]
    
    # Define confidence categories and colors (orange to blue gradient)
    categories = [
        'Not at all confident',
        'Slightly confident', 
        'Moderately confident',
        'Very confident',
        'Extremely confident'
    ]
    
    colors = [
        '#FF8A65',  # Dark orange
        '#FFB74D',  # Light orange
        '#90CAF9',  # Light blue
        '#64B5F6',  # Medium blue
        '#42A5F5'   # Dark blue
    ]
    
    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(14, 3))
    
    # Process each confidence aspect
    y_positions = []
    y_labels = []
    
    for i, (label, column) in enumerate(confidence_data):
        # Get data for this aspect
        counts = df[column].value_counts(dropna=True)
        total = df[column].notna().sum()
        pct = (counts / total * 100).round(1)
        
        # Map responses to standard categories
        percentages = [pct.get(cat, 0) for cat in categories]
        
        # Create horizontal stacked bar for this aspect
        y_pos = i
        y_positions.append(y_pos)
        y_labels.append(label)
        
        left = 0
        for j, (category, percentage, color) in enumerate(zip(categories, percentages, colors)):
            if percentage > 0:
                bar = ax.barh(y_pos, percentage, left=left, height=0.8, 
                             color=color, edgecolor='white', linewidth=0.5)
                
                # Add percentage label
                if percentage > 0:
                    rotation = 90 if percentage < 5 else 0
                    ax.text(left + percentage/2, y_pos, f'{percentage:.1f}%', 
                           ha='center', va='center', fontsize=10, fontweight='bold',
                           rotation=rotation)
                
                left += percentage
    
    # Customize the chart
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.4, len(confidence_data) - 0.6)
    ax.set_xlabel('Percentage (%)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Confidence Level', fontsize=14, fontweight='bold')
    ax.set_title('Confidence using or discussing the use of AI in healthcare', 
                fontsize=14, fontweight='bold', pad=30)
    
    # Set y-axis labels
    ax.set_yticks(y_positions)
    ax.set_yticklabels(y_labels, fontsize=14)
    
    # Remove unnecessary spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(True)
    
    # Add x-axis grid
    ax.grid(axis='x', alpha=0.3, linestyle='-', linewidth=0.5)
    ax.set_xticks(range(0, 101, 10))
    ax.tick_params(axis='x', labelsize=12)
    
    # Create legend (centered, no box)
    legend_elements = [plt.Rectangle((0,0),1,1, facecolor=color, edgecolor='white') 
                      for color in colors]
    ax.legend(legend_elements, categories, loc='upper center', 
             bbox_to_anchor=(0.45, 1.25), ncol=5, fontsize=13, 
             frameon=False)
    
    # Adjust layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.85)  # Make room for legend above
    
    # Save the figure
    plt.savefig('fig5_ai_confidence.png', dpi=300, bbox_inches='tight')
    plt.savefig('fig5_ai_confidence.pdf', bbox_inches='tight')
    
    # Show the figure
    plt.show()
    
    # Print summary statistics
    print("AI Confidence Analysis:")
    print("=" * 50)
    
    for i, (label, column) in enumerate(confidence_data):
        counts = df[column].value_counts(dropna=True)
        total = df[column].notna().sum()
        pct = (counts / total * 100).round(1)
        
        print(f"\n{label}:")
        print(f"  Total responses: {total}")
        
        for category in categories:
            percentage = pct.get(category, 0)
            print(f"  {category}: {percentage:.1f}%")
        
        print(f"  Sum of percentages: {sum(pct.values):.1f}%")

if __name__ == "__main__":
    create_ai_confidence_chart()