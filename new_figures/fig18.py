#!/usr/bin/env python3
"""
Figure 18: AI Confidence vs Willingness Matrix - Bubble Chart
Bubble chart with confidence on x-axis, willingness on y-axis, bubble size representing
number of participants, colored by demographic groups.

To run: conda activate eda && python fig18.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

def create_confidence_willingness_bubble():
    """Create bubble chart showing confidence vs willingness matrix"""
    
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
    
    # Clean demographic data
    df['age_group_clean'] = df['age_group.q1'].fillna('Unknown')
    df['role_clean'] = df['pro_role.q4'].fillna('Unknown')
    
    # Categorize specialties
    def categorize_specialty(specialty):
        if pd.isna(specialty) or 'Something else' in str(specialty):
            return 'Other/Unknown'
        specialty_str = str(specialty).lower()
        if any(term in specialty_str for term in ['pediatric', 'pediatrics']):
            return 'Pediatrics'
        elif any(term in specialty_str for term in ['family', 'family practice']):
            return 'Family Medicine'
        elif any(term in specialty_str for term in ['neuro']):
            return 'Neurology'
        elif any(term in specialty_str for term in ['radio']):
            return 'Radiology'
        elif any(term in specialty_str for term in ['cardio']):
            return 'Cardiology'
        elif any(term in specialty_str for term in ['emergency']):
            return 'Emergency Medicine'
        elif any(term in specialty_str for term in ['internal']):
            return 'Internal Medicine'
        else:
            return 'Other/Unknown'
    
    df['specialty_category'] = df['med_specialty.q8'].apply(categorize_specialty)
    
    # Create the bubble chart
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('AI Confidence vs Willingness Matrix\nBubble Size = Number of Participants', 
                 fontsize=16, fontweight='bold')
    
    # 1. Overall confidence vs willingness
    ax1 = axes[0, 0]
    
    # Group by confidence and willingness scores
    bubble_data = df.groupby(['confidence_score', 'willingness_score']).size().reset_index(name='count')
    
    # Create scatter plot with better sizing
    scatter = ax1.scatter(bubble_data['confidence_score'], bubble_data['willingness_score'], 
                         s=bubble_data['count'] * 100, alpha=0.7, c=bubble_data['count'], 
                         cmap='viridis', edgecolors='black', linewidth=0.5)
    
    # Add colorbar
    cbar1 = plt.colorbar(scatter, ax=ax1)
    cbar1.set_label('Number of Participants', fontsize=10)
    
    # Customize axes
    ax1.set_xlabel('AI Confidence Score', fontsize=12, fontweight='bold')
    ax1.set_ylabel('AI Willingness Score', fontsize=12, fontweight='bold')
    ax1.set_title('Overall Confidence vs Willingness', fontsize=14, fontweight='bold')
    ax1.set_xlim(0.5, 5.5)
    ax1.set_ylim(0.5, 5.5)
    ax1.set_xticks(range(1, 6))
    ax1.set_yticks(range(1, 6))
    ax1.grid(True, alpha=0.3)
    
    # Add labels for each bubble
    for _, row in bubble_data.iterrows():
        if row['count'] >= 3:  # Label bubbles with 3+ participants
            ax1.annotate(f'{int(row["count"])}', 
                        (row['confidence_score'], row['willingness_score']),
                        ha='center', va='center', fontsize=9, fontweight='bold', color='white')
    
    # 2. By Age Group
    ax2 = axes[0, 1]
    
    age_groups = ['18 to 25 years old', '26 to 35 years old', '36 to 45 years old', 
                  '46 to 55 years old', '56 to 65 years old', '66 to 75 years old']
    age_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
    
    for i, age_group in enumerate(age_groups):
        age_data = df[df['age_group_clean'] == age_group]
        if len(age_data) > 5:  # Only include groups with sufficient data
            age_bubble_data = age_data.groupby(['confidence_score', 'willingness_score']).size().reset_index(name='count')
            
            ax2.scatter(age_bubble_data['confidence_score'], age_bubble_data['willingness_score'], 
                       s=age_bubble_data['count'] * 30, alpha=0.7, c=age_colors[i], 
                       label=age_group, edgecolors='black', linewidth=0.5)
    
    ax2.set_xlabel('AI Confidence Score', fontsize=12, fontweight='bold')
    ax2.set_ylabel('AI Willingness Score', fontsize=12, fontweight='bold')
    ax2.set_title('By Age Group', fontsize=14, fontweight='bold')
    ax2.set_xlim(0.5, 5.5)
    ax2.set_ylim(0.5, 5.5)
    ax2.set_xticks(range(1, 6))
    ax2.set_yticks(range(1, 6))
    ax2.grid(True, alpha=0.3)
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    
    # 3. By Professional Role
    ax3 = axes[1, 0]
    
    roles = ['Physician', 'Advanced Practitioner (Nurse Practitioner or Physician Assistant)', 
             'Medical Student', 'Resident or Fellow']
    role_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    
    for i, role in enumerate(roles):
        role_data = df[df['role_clean'] == role]
        if len(role_data) > 5:
            role_bubble_data = role_data.groupby(['confidence_score', 'willingness_score']).size().reset_index(name='count')
            
            ax3.scatter(role_bubble_data['confidence_score'], role_bubble_data['willingness_score'], 
                       s=role_bubble_data['count'] * 40, alpha=0.7, c=role_colors[i], 
                       label=role, edgecolors='black', linewidth=0.5)
    
    ax3.set_xlabel('AI Confidence Score', fontsize=12, fontweight='bold')
    ax3.set_ylabel('AI Willingness Score', fontsize=12, fontweight='bold')
    ax3.set_title('By Professional Role', fontsize=14, fontweight='bold')
    ax3.set_xlim(0.5, 5.5)
    ax3.set_ylim(0.5, 5.5)
    ax3.set_xticks(range(1, 6))
    ax3.set_yticks(range(1, 6))
    ax3.grid(True, alpha=0.3)
    ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    
    # 4. By Medical Specialty
    ax4 = axes[1, 1]
    
    specialties = ['Pediatrics', 'Family Medicine', 'Neurology', 'Radiology', 
                   'Cardiology', 'Emergency Medicine', 'Internal Medicine']
    specialty_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
    
    for i, specialty in enumerate(specialties):
        spec_data = df[df['specialty_category'] == specialty]
        if len(spec_data) > 5:
            spec_bubble_data = spec_data.groupby(['confidence_score', 'willingness_score']).size().reset_index(name='count')
            
            ax4.scatter(spec_bubble_data['confidence_score'], spec_bubble_data['willingness_score'], 
                       s=spec_bubble_data['count'] * 50, alpha=0.7, c=specialty_colors[i], 
                       label=specialty, edgecolors='black', linewidth=0.5)
    
    ax4.set_xlabel('AI Confidence Score', fontsize=12, fontweight='bold')
    ax4.set_ylabel('AI Willingness Score', fontsize=12, fontweight='bold')
    ax4.set_title('By Medical Specialty', fontsize=14, fontweight='bold')
    ax4.set_xlim(0.5, 5.5)
    ax4.set_ylim(0.5, 5.5)
    ax4.set_xticks(range(1, 6))
    ax4.set_yticks(range(1, 6))
    ax4.grid(True, alpha=0.3)
    ax4.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    
    # Add diagonal line for reference (confidence = willingness)
    for ax in axes.flat:
        ax.plot([1, 5], [1, 5], 'k--', alpha=0.5, linewidth=1)
        ax.text(3, 3.5, 'Confidence = Willingness', rotation=45, ha='center', va='center', 
                fontsize=8, alpha=0.7, bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    # Save the figure
    plt.savefig('fig18_confidence_willingness_bubble.png', dpi=300, bbox_inches='tight')
    plt.savefig('fig18_confidence_willingness_bubble.pdf', bbox_inches='tight')
    
    # Show the figure
    plt.show()
    
    # Print detailed analysis
    print("AI Confidence vs Willingness Matrix - Bubble Chart Analysis:")
    print("=" * 70)
    
    # Overall statistics
    print(f"\nOverall Statistics:")
    print(f"Total participants: {len(df)}")
    print(f"Average confidence score: {df['confidence_score'].mean():.2f}")
    print(f"Average willingness score: {df['willingness_score'].mean():.2f}")
    print(f"Confidence-Willingness correlation: {df['confidence_score'].corr(df['willingness_score']):.3f}")
    
    # Quadrant analysis
    print(f"\nQuadrant Analysis:")
    high_conf_high_will = len(df[(df['confidence_score'] >= 4) & (df['willingness_score'] >= 4)])
    high_conf_low_will = len(df[(df['confidence_score'] >= 4) & (df['willingness_score'] < 3)])
    low_conf_high_will = len(df[(df['confidence_score'] < 3) & (df['willingness_score'] >= 4)])
    low_conf_low_will = len(df[(df['confidence_score'] < 3) & (df['willingness_score'] < 3)])
    
    print(f"High Confidence + High Willingness: {high_conf_high_will} ({high_conf_high_will/len(df)*100:.1f}%)")
    print(f"High Confidence + Low Willingness: {high_conf_low_will} ({high_conf_low_will/len(df)*100:.1f}%)")
    print(f"Low Confidence + High Willingness: {low_conf_high_will} ({low_conf_high_will/len(df)*100:.1f}%)")
    print(f"Low Confidence + Low Willingness: {low_conf_low_will} ({low_conf_low_will/len(df)*100:.1f}%)")
    
    # Age group analysis
    print(f"\nAge Group Analysis:")
    for age_group in age_groups:
        age_data = df[df['age_group_clean'] == age_group]
        if len(age_data) > 5:
            avg_conf = age_data['confidence_score'].mean()
            avg_will = age_data['willingness_score'].mean()
            print(f"{age_group}: Confidence={avg_conf:.2f}, Willingness={avg_will:.2f}")
    
    # Role analysis
    print(f"\nProfessional Role Analysis:")
    for role in roles:
        role_data = df[df['role_clean'] == role]
        if len(role_data) > 5:
            avg_conf = role_data['confidence_score'].mean()
            avg_will = role_data['willingness_score'].mean()
            print(f"{role}: Confidence={avg_conf:.2f}, Willingness={avg_will:.2f}")
    
    # Specialty analysis
    print(f"\nMedical Specialty Analysis:")
    for specialty in specialties:
        spec_data = df[df['specialty_category'] == specialty]
        if len(spec_data) > 5:
            avg_conf = spec_data['confidence_score'].mean()
            avg_will = spec_data['willingness_score'].mean()
            print(f"{specialty}: Confidence={avg_conf:.2f}, Willingness={avg_will:.2f}")

if __name__ == "__main__":
    create_confidence_willingness_bubble()
