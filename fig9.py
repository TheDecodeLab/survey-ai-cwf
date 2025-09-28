#!/usr/bin/env python3
"""
Figure 9: Potential concerns with AI in healthcare
Vertical bar chart showing the percentage of respondents who selected each concern

To run: conda activate eda && python fig9.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

def create_ai_concerns_chart():
    """Create vertical bar chart for AI concerns"""
    
    # Read the survey data
    df = pd.read_excel('data/S2_Survey_Data.xlsx', sheet_name='Sheet 1')
    
    # Parse the concerns data
    concerns_data = df['ai_concerns.q32'].dropna()
    total_responses = len(concerns_data)
    
    # Count individual concerns
    concern_counts = Counter()
    for response in concerns_data:
        # Split by comma and clean up each concern
        concerns = [concern.strip() for concern in str(response).split(',')]
        for concern in concerns:
            # Clean up the concern text
            concern = concern.replace('other concerns and challenges with AI in healthcare: (please describe)', '').strip()
            concern = concern.replace('other concern or challenge with AI in healthcare', '').strip()
            if concern and len(concern) > 5:  # Filter out empty or very short strings
                concern_counts[concern] += 1
    
    # Define the main concerns in order (matching reference chart)
    main_concerns_data = [
        'reliability and accuracy of AI systems',
        'lack of transparency in AI algorithms',
        'ethical implications and decision-making accountability',
        'biases or unequal performance of AI for certain patient populations',
        'impact on healthcare professionals\' roles and responsibilities',
        'patient privacy and data security',
        'efficiencies of AI tools causing redundancies or job losses'
    ]
    
    # Define display labels with line breaks
    main_concerns_labels = [
        'Reliability\nand accuracy\nof AI systems',
        'Lack of transparency\nin AI algorithms',
        'Ethical implications\nand decision-making\naccountability',
        'Biases or unequal\nperformanceof AI\nfor certain patient\npopulations',
        'Impact on healthcare\nprofessionals\' roles\nand responsibilities',
        'Patient privacy\nand data security',
        'Efficiencies of AI\ntools causing\nredundancies or\njob losses'
    ]
    
    # Get counts and percentages for main concerns
    counts = []
    percentages = []
    for concern in main_concerns_data:
        count = concern_counts.get(concern, 0)
        percentage = (count / total_responses) * 100
        counts.append(count)
        percentages.append(percentage)
    
    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(12, 3))
    
    # Create vertical bars
    x_positions = 1.3*np.arange(len(main_concerns_data))
    bars = ax.bar(x_positions, percentages, color='#42A5F5', alpha=0.8)
    
    # Add percentage and count labels on top of bars
    for i, (bar, percentage, count) in enumerate(zip(bars, percentages, counts)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{percentage:.1f}% ({count})',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Customize the chart
    ax.set_ylim(0, 100)
    ax.set_ylabel('Percent', fontsize=12, fontweight='bold')
    ax.set_title('Potential concerns with AI in healthcare', fontsize=16, fontweight='bold', pad=10)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(main_concerns_labels, ha='center', fontsize=10)
    
    # Add grid
    ax.grid(axis='y', alpha=0.3, linestyle='-', linewidth=0.5)
    ax.set_yticks(range(0, 101, 20))
    
    # Remove unnecessary spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(True)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure
    plt.savefig('fig9_ai_concerns.png', dpi=300, bbox_inches='tight')
    plt.savefig('fig9_ai_concerns.pdf', bbox_inches='tight')
    
    # Show the figure
    plt.show()
    
    # Print summary statistics
    print("AI Concerns Analysis:")
    print("=" * 60)
    print(f"Total responses: {total_responses}")
    print("\nMain concerns (in order of frequency):")
    for i, (concern, percentage, count) in enumerate(zip(main_concerns_data, percentages, counts)):
        print(f"{i+1}. {concern}: {percentage:.1f}% ({count})")

if __name__ == "__main__":
    create_ai_concerns_chart()
