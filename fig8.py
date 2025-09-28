#!/usr/bin/env python3
"""
Figure 8: Clinical workflow
Horizontal stacked bar chart showing 6 aspects of clinical workflow impact

To run: conda activate eda && python fig8.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def create_clinical_workflow_chart():
    """Create horizontal stacked bar chart for clinical workflow aspects"""
    
    # Read the survey data
    df = pd.read_excel('data/S2_Survey_Data.xlsx', sheet_name='Sheet 1')
    
    # Define workflow aspects and their corresponding columns
    workflow_data = [
        ('Number of alerts', 'ai_num_alerts.q25'),
        ('Frequency of alerts', 'ai_freq_alerts.q26'),
        ('Alarm fatigue', 'ai_alarm_fatigue.q27'),
        ('Cognitive fatigue', 'ai_cognitive_fatgigue.q28'),
        ('Cognitive overload', 'ai_cognitive_overload.q29'),
        ('Information paralysis', 'ai_info_paralysis.q30')
    ]
    
    # Define response categories and colors (matching reference)
    categories = ['Decrease', 'No impact', 'Increase', 'More than one answer']
    colors = ['#FF8A65', '#FFB74D', '#90CAF9', '#42A5F5']  # Dark orange, Light orange, Light blue, Dark blue
    
    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(11, 5))
    
    # Process each workflow aspect
    y_positions = []
    y_labels = []
    
    for i, (label, column) in enumerate(workflow_data):
        # Get data for this aspect
        counts = df[column].value_counts(dropna=True)
        total = df[column].notna().sum()
        pct = (counts / total * 100).round(1)
        
        # Map responses to standard categories
        decrease_pct = 0
        no_impact_pct = 0
        increase_pct = 0
        multiple_pct = 0
        
        for response, percentage in pct.items():
            if response == 'Decrease':
                decrease_pct = round(percentage, 1)
            elif response == 'No_impact':
                no_impact_pct = round(percentage, 1)
            elif response == 'Increase':
                increase_pct = round(percentage, 1)
            else:  # Multiple answers
                multiple_pct += round(percentage, 1)
        
        # Create horizontal stacked bar for this aspect
        y_pos = i
        y_positions.append(y_pos)
        y_labels.append(label)
        
        left = 0
        percentages = [decrease_pct, no_impact_pct, increase_pct, multiple_pct]
        
        for j, (category, percentage, color) in enumerate(zip(categories, percentages, colors)):
            if percentage > 0:
                bar = ax.barh(y_pos, percentage, left=left, height=0.6, 
                             color=color, edgecolor='white', linewidth=0.5)
                
                # Add percentage label
                if percentage > 0:
                    rotation = 90 if percentage < 3 else 0
                    ax.text(left + percentage/2, y_pos, f'{percentage:.1f}%', 
                           ha='center', va='center', fontsize=9, fontweight='bold',
                           rotation=rotation)
                
                left += percentage
    
    # Customize the chart
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.5, len(workflow_data) - 0.5)
    ax.set_xlabel('Percentage (%)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Clinical workflow', fontsize=12, fontweight='bold')
    ax.set_title('Clinical workflow', fontsize=16, fontweight='bold', pad=20)
    
    # Set y-axis labels
    ax.set_yticks(y_positions)
    ax.set_yticklabels(y_labels)
    
    # Remove unnecessary spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(True)
    
    # Add x-axis grid
    ax.grid(axis='x', alpha=0.3, linestyle='-', linewidth=0.5)
    ax.set_xticks(range(0, 101, 10))
    
    # Create legend (centered, no box)
    legend_elements = [plt.Rectangle((0,0),1,1, facecolor=color, edgecolor='white') 
                      for color in colors]
    ax.legend(legend_elements, categories, loc='upper center', 
             bbox_to_anchor=(0.5, 1.06), ncol=4, fontsize=12, 
             frameon=False)
    
    # Adjust layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)  # Make room for legend above
    
    # Save the figure
    plt.savefig('fig8_clinical_workflow.png', dpi=300, bbox_inches='tight')
    plt.savefig('fig8_clinical_workflow.pdf', bbox_inches='tight')
    
    # Show the figure
    plt.show()
    
    # Print summary statistics
    print("Clinical Workflow Analysis:")
    print("=" * 50)
    
    for i, (label, column) in enumerate(workflow_data):
        counts = df[column].value_counts(dropna=True)
        total = df[column].notna().sum()
        pct = (counts / total * 100).round(1)
        
        print(f"\n{label}:")
        print(f"  Total responses: {total}")
        
        # Map responses to standard categories
        decrease_pct = pct.get('Decrease', 0)
        no_impact_pct = pct.get('No_impact', 0)
        increase_pct = pct.get('Increase', 0)
        multiple_pct = sum(pct[pct.index.str.contains(',')].values) if any(pct.index.str.contains(',')) else 0
        
        print(f"  Decrease: {decrease_pct:.1f}%")
        print(f"  No impact: {no_impact_pct:.1f}%")
        print(f"  Increase: {increase_pct:.1f}%")
        print(f"  More than one answer: {multiple_pct:.1f}%")

if __name__ == "__main__":
    create_clinical_workflow_chart()
