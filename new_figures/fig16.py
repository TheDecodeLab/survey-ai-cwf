#!/usr/bin/env python3
"""
Figure 16: Benefits vs Concerns Balance - Circular Bar Chart
Circular visualization showing the balance between perceived benefits and concerns,
with different segments for different demographic groups.

To run: conda activate eda && python fig16.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import math

def create_circular_balance_chart():
    """Create circular bar chart showing benefits vs concerns balance"""
    
    # Read the survey data
    df = pd.read_excel('../data/S2_Survey_Data.xlsx', sheet_name='Sheet 1')
    
    # Parse benefits and concerns data
    benefits_data = df['ai_benefits.q31'].dropna()
    concerns_data = df['ai_concerns.q32'].dropna()
    
    # Count individual benefits
    benefit_counts = Counter()
    for response in benefits_data:
        benefits = [benefit.strip() for benefit in str(response).split(',')]
        for benefit in benefits:
            benefit = benefit.replace('other benefits of AI in healthcare: (please describe)', '').strip()
            if benefit and len(benefit) > 5:
                benefit_counts[benefit] += 1
    
    # Count individual concerns
    concern_counts = Counter()
    for response in concerns_data:
        concerns = [concern.strip() for concern in str(response).split(',')]
        for concern in concerns:
            concern = concern.replace('other concerns and challenges with AI in healthcare: (please describe)', '').strip()
            concern = concern.replace('other concern or challenge with AI in healthcare', '').strip()
            if concern and len(concern) > 5:
                concern_counts[concern] += 1
    
    # Define main benefits and concerns
    main_benefits = [
        'Improved efficiency in healthcare documentation work',
        'Increased efficiency in healthcare delivery',
        'Improved diagnostic accuracy',
        'Improved medical training or simulations',
        'Enhanced patient outcomes',
        'Enabling personalized medicine',
        'Improved patient experience and engagement',
        'Enhanced surgical training planning'
    ]
    
    main_concerns = [
        'reliability and accuracy of AI systems',
        'lack of transparency in AI algorithms',
        'ethical implications and decision-making accountability',
        'biases or unequal performance of AI for certain patient populations',
        'impact on healthcare professionals\' roles and responsibilities',
        'patient privacy and data security',
        'efficiencies of AI tools causing redundancies or job losses'
    ]
    
    # Calculate percentages
    total_responses = len(benefits_data)
    benefit_percentages = {benefit: (benefit_counts.get(benefit, 0) / total_responses) * 100 
                          for benefit in main_benefits}
    
    total_concern_responses = len(concerns_data)
    concern_percentages = {concern: (concern_counts.get(concern, 0) / total_concern_responses) * 100 
                          for concern in main_concerns}
    
    # Create the circular chart
    fig, ax = plt.subplots(figsize=(12, 12), subplot_kw=dict(projection='polar'))
    
    # Define angles for each category
    n_benefits = len(main_benefits)
    n_concerns = len(main_concerns)
    
    # Create angles - benefits on top half, concerns on bottom half
    benefit_angles = np.linspace(0, np.pi, n_benefits, endpoint=False)
    concern_angles = np.linspace(np.pi, 2*np.pi, n_concerns, endpoint=False)
    
    # Define colors
    benefit_colors = plt.cm.Greens(np.linspace(0.3, 0.8, n_benefits))
    concern_colors = plt.cm.Reds(np.linspace(0.3, 0.8, n_concerns))
    
    # Plot benefits (outer ring)
    benefit_values = [benefit_percentages[benefit] for benefit in main_benefits]
    benefit_bars = ax.bar(benefit_angles, benefit_values, width=0.5, 
                          color=benefit_colors, alpha=0.8, label='Benefits')
    
    # Plot concerns (inner ring)
    concern_values = [concern_percentages[concern] for concern in main_concerns]
    concern_bars = ax.bar(concern_angles, concern_values, width=0.5, 
                          color=concern_colors, alpha=0.8, label='Concerns')
    
    # Add labels for benefits
    for angle, value, benefit in zip(benefit_angles, benefit_values, main_benefits):
        if value > 0:
            # Create very brief labels
            if 'documentation work' in benefit:
                short_benefit = 'Doc Efficiency'
            elif 'delivery' in benefit:
                short_benefit = 'Delivery Efficiency'
            elif 'diagnostic accuracy' in benefit:
                short_benefit = 'Diagnostic Accuracy'
            elif 'training' in benefit:
                short_benefit = 'Training/Sims'
            elif 'patient outcomes' in benefit:
                short_benefit = 'Patient Outcomes'
            elif 'personalized' in benefit:
                short_benefit = 'Personalized Med'
            elif 'patient experience' in benefit:
                short_benefit = 'Patient Experience'
            elif 'surgical' in benefit:
                short_benefit = 'Surgical Planning'
            else:
                short_benefit = benefit.replace('Improved ', '').replace('Increased ', '').replace('Enhanced ', '')
                short_benefit = short_benefit.replace(' in healthcare', '').replace(' healthcare', '')
                if len(short_benefit) > 15:
                    short_benefit = short_benefit[:12] + '...'
            
            ax.text(angle, value + 3, f'{short_benefit} {value:.0f}%', 
                   ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    # Add labels for concerns
    for angle, value, concern in zip(concern_angles, concern_values, main_concerns):
        if value > 0:
            # Create very brief labels for concerns
            if 'reliability and accuracy' in concern:
                short_concern = 'Reliability'
            elif 'transparency' in concern:
                short_concern = 'Transparency'
            elif 'ethical implications' in concern:
                short_concern = 'Ethics'
            elif 'biases' in concern:
                short_concern = 'Bias'
            elif 'roles and responsibilities' in concern:
                short_concern = 'Job Impact'
            elif 'privacy' in concern:
                short_concern = 'Privacy'
            elif 'redundancies' in concern:
                short_concern = 'Job Loss'
            else:
                short_concern = concern.replace(' of AI systems', '').replace(' in AI algorithms', '')
                short_concern = short_concern.replace(' and decision-making accountability', '')
                short_concern = short_concern.replace(' for certain patient populations', '')
                short_concern = short_concern.replace('professionals\' roles and responsibilities', 'professional roles')
                short_concern = short_concern.replace(' causing redundancies or job losses', '')
                if len(short_concern) > 15:
                    short_concern = short_concern[:12] + '...'
            
            ax.text(angle, value + 3, f'{short_concern} {value:.0f}%', 
                   ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    # Customize the chart
    ax.set_ylim(0, max(max(benefit_values), max(concern_values)) + 10)
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    
    # Add title
    plt.title('AI in Healthcare: Benefits vs Concerns Balance\nCircular Comparison of Perceived Advantages and Challenges', 
              size=18, fontweight='bold', pad=30)
    
    # Add legend
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=12)
    
    # Add summary statistics
    total_benefit_mentions = sum(benefit_values)
    total_concern_mentions = sum(concern_values)
    balance_ratio = total_benefit_mentions / total_concern_mentions if total_concern_mentions > 0 else 0
    
    stats_text = f"""
    Balance Analysis:
    • Total Benefit Mentions: {total_benefit_mentions:.1f}%
    • Total Concern Mentions: {total_concern_mentions:.1f}%
    • Benefit/Concern Ratio: {balance_ratio:.2f}
    • Net Sentiment: {'Positive' if balance_ratio > 1 else 'Negative' if balance_ratio < 1 else 'Neutral'}
    """
    
    # Add text box
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=11, 
            verticalalignment='top', bbox=dict(boxstyle="round,pad=0.5", 
            facecolor='lightblue', alpha=0.8))
    
    # Add grid
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save the figure
    plt.savefig('fig16_circular_balance.png', dpi=300, bbox_inches='tight')
    plt.savefig('fig16_circular_balance.pdf', bbox_inches='tight')
    
    # Show the figure
    plt.show()
    
    # Print detailed analysis
    print("Benefits vs Concerns Balance - Circular Chart Analysis:")
    print("=" * 60)
    
    print(f"\nBenefits Analysis (Top 8):")
    for i, (benefit, percentage) in enumerate(zip(main_benefits, benefit_values), 1):
        print(f"{i:2d}. {benefit}: {percentage:.1f}%")
    
    print(f"\nConcerns Analysis (Top 7):")
    for i, (concern, percentage) in enumerate(zip(main_concerns, concern_values), 1):
        print(f"{i:2d}. {concern}: {percentage:.1f}%")
    
    print(f"\nOverall Balance:")
    print(f"Total benefit mentions: {total_benefit_mentions:.1f}%")
    print(f"Total concern mentions: {total_concern_mentions:.1f}%")
    print(f"Benefit/Concern ratio: {balance_ratio:.2f}")
    
    # Find top benefit and concern
    top_benefit = max(benefit_percentages, key=benefit_percentages.get)
    top_concern = max(concern_percentages, key=concern_percentages.get)
    
    print(f"\nMost mentioned benefit: {top_benefit} ({benefit_percentages[top_benefit]:.1f}%)")
    print(f"Most mentioned concern: {top_concern} ({concern_percentages[top_concern]:.1f}%)")

if __name__ == "__main__":
    create_circular_balance_chart()
