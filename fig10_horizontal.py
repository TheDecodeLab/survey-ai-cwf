#!/usr/bin/env python3
"""
Figure 10: Potential benefits with using AI in healthcare (Horizontal Version)
Horizontal bar chart showing the percentage of respondents who selected each benefit

To run: conda activate eda && python fig10_horizontal.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

def create_ai_benefits_horizontal_chart():
    """Create horizontal bar chart for AI benefits"""
    
    # Read the survey data
    df = pd.read_excel('data/S2_Survey_Data.xlsx', sheet_name='Sheet 1')
    
    # Parse the benefits data
    benefits_data = df['ai_benefits.q31'].dropna()
    total_responses = len(benefits_data)
    
    # Count individual benefits
    benefit_counts = Counter()
    for response in benefits_data:
        # Split by comma and clean up each benefit
        benefits = [benefit.strip() for benefit in str(response).split(',')]
        for benefit in benefits:
            # Clean up the benefit text
            benefit = benefit.replace('other benefits of AI in healthcare: (please describe)', '').strip()
            if benefit and len(benefit) > 5:  # Filter out empty or very short strings
                benefit_counts[benefit] += 1
    
    # Define the main benefits in order (matching reference chart)
    main_benefits_data = [
        'Improved efficiency in healthcare documentation work',
        'Increased efficiency in healthcare delivery',
        'Improved diagnostic accuracy',
        'Improved medical training or simulations',
        'Enhanced patient outcomes',
        'Enabling personalized medicine',
        'Improved patient experience and engagement',
        'Enhanced surgical training planning',
        'Other benefits of AI in healthcare: (please describe)'
    ]
    
    # Define display labels with line breaks
    main_benefits_labels = [
        'Improved efficiency in\nhealthcare documentation work',
        'Increased efficiency\nin healthcare delivery',
        'Improved diagnostic accuracy',
        'Improved medical\ntraining or simulations',
        'Enhanced patient outcomes',
        'Enabling personalized medicine',
        'Improved patient\nexperience and engagement',
        'Enhanced surgical\ntraining planning',
        'Other benefits of AI\nin healthcare'
    ]
    
    # Get counts and percentages for main benefits
    counts = []
    percentages = []
    for benefit in main_benefits_data:
        count = benefit_counts.get(benefit, 0)
        percentage = (count / total_responses) * 100
        counts.append(count)
        percentages.append(percentage)
    
    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(12, 5))
    
    # Create horizontal bars
    y_positions = np.arange(len(main_benefits_data))
    bars = ax.barh(y_positions, percentages, color='#42A5F5', alpha=0.8)
    
    # Add percentage and count labels on the right side of bars
    for i, (bar, percentage, count) in enumerate(zip(bars, percentages, counts)):
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height()/2.,
                f'{percentage:.1f}% ({count})',
                ha='left', va='center', fontsize=10, fontweight='bold')
    
    # Customize the chart
    ax.set_xlim(0, 85)
    ax.set_xlabel('Percent', fontsize=12, fontweight='bold')
    ax.set_title('Potential benefits with using AI in healthcare', fontsize=16, fontweight='bold', pad=10)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(main_benefits_labels, fontsize=10)
    
    # Add grid
    ax.grid(axis='x', alpha=0.3, linestyle='-', linewidth=0.5)
    ax.set_xticks(range(0, 81, 20))
    
    # Remove unnecessary spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(True)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure
    plt.savefig('fig10_ai_benefits_horizontal.png', dpi=300, bbox_inches='tight')
    plt.savefig('fig10_ai_benefits_horizontal.pdf', bbox_inches='tight')
    
    # Show the figure
    plt.show()
    
    # Print summary statistics
    print("AI Benefits Analysis (Horizontal Version):")
    print("=" * 60)
    print(f"Total responses: {total_responses}")
    print("\nMain benefits (in order of frequency):")
    for i, (benefit, percentage, count) in enumerate(zip(main_benefits_data, percentages, counts)):
        print(f"{i+1}. {benefit}: {percentage:.1f}% ({count})")

if __name__ == "__main__":
    create_ai_benefits_horizontal_chart()
