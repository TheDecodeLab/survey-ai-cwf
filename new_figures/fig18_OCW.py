#!/usr/bin/env python3
"""
Figure 18_OCW: Overall AI Confidence vs Willingness - Bubble Chart
Bubble chart showing confidence on x-axis, willingness on y-axis, with bubble size 
representing number of participants and numerical labels.

To run: conda activate eda && python fig18_OCW.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

def create_overall_confidence_willingness_bubble(fig_size=(8, 7)):
    """Create bubble chart showing overall confidence vs willingness with numbers
    
    Parameters:
    fig_size (tuple): Figure size as (width, height) in inches. Default is (14, 12)
    """
    
    # Read the survey data
    df = pd.read_excel('../data/S2_Survey_Data.xlsx', sheet_name='Sheet 1')
    
    # Convert categorical responses to numerical scores
    def convert_confidence_to_score(confidence):
        if pd.isna(confidence):
            return 0
        confidence_str = str(confidence).lower()
        if 'not at all' in confidence_str:
            return 1
        elif 'slightly' in confidence_str:
            return 2
        elif 'moderately' in confidence_str:
            return 3
        elif 'very' in confidence_str:
            return 4
        elif 'extremely' in confidence_str:
            return 5
        else:
            return 0
    
    def convert_willingness_to_score(willingness):
        if pd.isna(willingness):
            return 0
        willingness_str = str(willingness).lower()
        if 'not at all' in willingness_str:
            return 1
        elif 'slightly' in willingness_str:
            return 2
        elif 'moderately' in willingness_str:
            return 3
        elif 'very' in willingness_str:
            return 4
        elif 'extremely' in willingness_str:
            return 5
        else:
            return 0
    
    # Add numerical scores
    df['confidence_score'] = df['ai_use_confidence.q19'].apply(convert_confidence_to_score)
    df['willingness_score'] = df['ai_willing_to_use.q12'].apply(convert_willingness_to_score)
    
    # Clean professional role data
    df['role_clean'] = df['pro_role.q4'].fillna('Unknown')
    
    # Filter out invalid responses (score = 0)
    valid_data = df[(df['confidence_score'] > 0) & (df['willingness_score'] > 0)]
    
    print("Overall Confidence vs Willingness Analysis:")
    print("=" * 50)
    print(f"Total valid responses: {len(valid_data)}")
    print(f"Confidence range: {valid_data['confidence_score'].min()} - {valid_data['confidence_score'].max()}")
    print(f"Willingness range: {valid_data['willingness_score'].min()} - {valid_data['willingness_score'].max()}")
    
    # Group by confidence and willingness scores with role breakdown
    bubble_data = valid_data.groupby(['confidence_score', 'willingness_score', 'role_clean']).size().reset_index(name='count')
    
    # Get unique confidence-willingness combinations
    combinations = valid_data.groupby(['confidence_score', 'willingness_score']).size().reset_index(name='total_count')
    
    print(f"\nNumber of unique confidence-willingness combinations: {len(combinations)}")
    print(f"Total participants represented: {combinations['total_count'].sum()}")
    print(f"Figure size: {fig_size[0]} x {fig_size[1]} inches")
    
    # Create the bubble chart with pie charts
    fig, ax = plt.subplots(figsize=fig_size)
    
    # Define colors for professional roles
    role_colors = {
        'Physician': '#FF6B6B',
        'Nurse': '#4ECDC4', 
        'Medical Student': '#45B7D1',
        'Resident/Fellow': '#96CEB4',
        'Advanced Practice Provider': '#FFEAA7',
        'Other': '#DDA0DD',
        'Unknown': '#A0A0A0'
    }
    
    # Get all unique roles in the data
    all_roles = valid_data['role_clean'].unique()
    available_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#A0A0A0', '#FFB347', '#87CEEB']
    role_color_map = {role: available_colors[i % len(available_colors)] for i, role in enumerate(all_roles)}
    
    # Create pie charts for each combination
    for _, combo in combinations.iterrows():
        conf = combo['confidence_score']
        will = combo['willingness_score']
        total_count = combo['total_count']
        
        # Get role breakdown for this combination
        role_data = bubble_data[(bubble_data['confidence_score'] == conf) & 
                               (bubble_data['willingness_score'] == will)]
        
        if len(role_data) > 0:
            # Calculate pie chart size (bubble size)
            bubble_size = max(50, min(500, total_count * 8))  # Scale bubble size
            
            # Create pie chart data
            roles = role_data['role_clean'].tolist()
            counts = role_data['count'].tolist()
            colors = [role_color_map[role] for role in roles]
            
            # Calculate pie chart position
            pie_x = conf
            pie_y = will
            
            # Create pie chart
            wedges, texts = ax.pie(counts, center=(pie_x, pie_y), radius=bubble_size/1000, 
                                  colors=colors, startangle=90)
            
            # Set alpha for wedges
            for wedge in wedges:
                wedge.set_alpha(0.8)
            
            # Add count label in the center
            ax.text(pie_x, pie_y, f'{total_count}', ha='center', va='center', 
                   fontsize=16, fontweight='normal', color='black')
    
    # Add role legend on the right side
    # Clean up role names by removing parentheses content
    clean_role_names = {}
    for role in all_roles:
        if '(' in role and ')' in role:
            clean_name = role.split('(')[0].strip()
        else:
            clean_name = role
        clean_role_names[role] = clean_name
    
    legend_elements = [plt.Rectangle((0,0),1,1, facecolor=role_color_map[role], alpha=0.8, label=clean_role_names[role]) 
                      for role in all_roles]
    role_legend = ax.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(0.95, 0.7), fontsize=13, title='Professional Roles', title_fontsize=16, frameon=False)
    ax.add_artist(role_legend)
    
    # Customize the plot
    ax.set_xlabel('Confidence', fontsize=16, fontweight='bold')
    ax.set_ylabel('Willingness', fontsize=16, fontweight='bold')
    # ax.set_title('AI Confidence vs Willingness by Professional Role\nBubble Size = Number of Participants, Colors = Professional Roles', 
                # fontsize=18, fontweight='bold', pad=20)
    
    # Set axis limits and ticks
    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(0.5, 5.5)
    ax.set_xticks(range(1, 6))
    ax.set_yticks(range(1, 6))
    
    # Add axis labels
    confidence_labels = ['Not at all', 'Slightly', 'Moderately', 'Very', 'Extremely']
    willingness_labels = ['Not at all', 'Slightly', 'Moderately', 'Very', 'Extremely']
    
    ax.set_xticklabels(confidence_labels, fontsize=15, rotation=45)
    ax.set_yticklabels(willingness_labels, fontsize=15)
    
    # Add grid
    ax.grid(True, alpha=0.3)
    
    # Add diagonal reference line
    ax.plot([1, 5], [1, 5], 'r--', alpha=0.7, linewidth=2, label='Confidence = Willingness')
    ax.legend(loc='center left', bbox_to_anchor=(0.93, 0.9), fontsize=12, frameon=False)
    
    # Calculate and display statistics
    correlation = valid_data['confidence_score'].corr(valid_data['willingness_score'])
    
    # Count participants in different quadrants
    high_conf_high_will = len(valid_data[(valid_data['confidence_score'] >= 4) & (valid_data['willingness_score'] >= 4)])
    high_conf_low_will = len(valid_data[(valid_data['confidence_score'] >= 4) & (valid_data['willingness_score'] <= 2)])
    low_conf_high_will = len(valid_data[(valid_data['confidence_score'] <= 2) & (valid_data['willingness_score'] >= 4)])
    low_conf_low_will = len(valid_data[(valid_data['confidence_score'] <= 2) & (valid_data['willingness_score'] <= 2)])
    
    # Print detailed statistics
    print(f"\nCorrelation between confidence and willingness: {correlation:.3f}")
    print(f"\nQuadrant Analysis:")
    print(f"  High Confidence + High Willingness: {high_conf_high_will} participants ({high_conf_high_will/len(valid_data)*100:.1f}%)")
    print(f"  High Confidence + Low Willingness: {high_conf_low_will} participants ({high_conf_low_will/len(valid_data)*100:.1f}%)")
    print(f"  Low Confidence + High Willingness: {low_conf_high_will} participants ({low_conf_high_will/len(valid_data)*100:.1f}%)")
    print(f"  Low Confidence + Low Willingness: {low_conf_low_will} participants ({low_conf_low_will/len(valid_data)*100:.1f}%)")
    
    # Show distribution by confidence level
    print(f"\nDistribution by Confidence Level:")
    conf_dist = valid_data['confidence_score'].value_counts().sort_index()
    for level, count in conf_dist.items():
        print(f"  Level {level}: {count} participants ({count/len(valid_data)*100:.1f}%)")
    
    # Show distribution by willingness level
    print(f"\nDistribution by Willingness Level:")
    will_dist = valid_data['willingness_score'].value_counts().sort_index()
    for level, count in will_dist.items():
        print(f"  Level {level}: {count} participants ({count/len(valid_data)*100:.1f}%)")
    
    # Show distribution by professional role
    print(f"\nDistribution by Professional Role:")
    role_dist = valid_data['role_clean'].value_counts()
    for role, count in role_dist.items():
        print(f"  {role}: {count} participants ({count/len(valid_data)*100:.1f}%)")
    
    # plt.tight_layout()
    # plt.subplots_adjust(right=0.8)
    # Save the figure
    plt.savefig('fig18_OCW_overall_confidence_willingness.png', dpi=300, bbox_inches='tight')
    plt.savefig('fig18_OCW_overall_confidence_willingness.pdf', bbox_inches='tight')
    
    # Show the figure
    plt.show()

if __name__ == "__main__":
    # You can customize the figure size here
    # Examples:
    # create_overall_confidence_willingness_bubble(fig_size=(12, 10))  # Smaller
    # create_overall_confidence_willingness_bubble(fig_size=(16, 14))  # Larger
    # create_overall_confidence_willingness_bubble(fig_size=(20, 16))  # Much larger
    
    create_overall_confidence_willingness_bubble()  # Uses default (14, 12)
