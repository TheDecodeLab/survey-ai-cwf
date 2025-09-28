#!/usr/bin/env python3
"""
Figure 14: Demographic vs AI Attitudes - Heatmap
Color-coded heatmap showing how age groups, roles, and specialties correlate 
with different AI attitudes and confidence levels.

To run: conda activate eda && python fig14.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy.stats import chi2_contingency

def create_demographic_heatmap():
    """Create heatmap showing demographic correlations with AI attitudes"""
    
    # Read the survey data
    df = pd.read_excel('../data/S2_Survey_Data.xlsx', sheet_name='Sheet 1')
    
    # Clean and prepare demographic data
    df_clean = df.copy()
    
    # Clean age groups
    df_clean['age_group'] = df_clean['age_group.q1'].fillna('Unknown')
    
    # Clean professional roles
    df_clean['role'] = df_clean['pro_role.q4'].fillna('Unknown')
    
    # Clean specialties - group into major categories
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
    
    df_clean['specialty_category'] = df_clean['med_specialty.q8'].apply(categorize_specialty)
    
    # Define AI attitude measures
    attitude_measures = {
        'AI Familiarity': 'ai_familiar.q10',
        'AI Training': 'ai_training.q18', 
        'AI Experience': 'ai_experience.q11',
        'AI Confidence': 'ai_use_confidence.q19',
        'AI Willingness': 'ai_willing_to_use.q12',
        'AI Opinion': 'ai_use_gen_opinion.q13'
    }
    
    # Convert categorical responses to numerical scores
    def convert_to_score(series, scale_type):
        if scale_type == 'familiarity':
            mapping = {
                'Not at all familiar': 1,
                'Slightly familiar': 2,
                'Moderately familiar': 3,
                'Very familiar': 4,
                'Extremely familiar': 5
            }
        elif scale_type == 'training':
            mapping = {
                'No': 1,
                'Yes, but very limited': 2,
                'Yes': 3
            }
        elif scale_type == 'experience':
            mapping = {
                'No': 1,
                'Unsure': 2,
                'Yes': 3
            }
        elif scale_type == 'confidence':
            mapping = {
                'Not at all confident': 1,
                'Slightly confident': 2,
                'Moderately confident': 3,
                'Very confident': 4,
                'Extremely confident': 5
            }
        elif scale_type == 'willingness':
            mapping = {
                'Not at all willing': 1,
                'Slightly willing': 2,
                'Moderately willing': 3,
                'Very willing': 4,
                'Extremely willing': 5
            }
        elif scale_type == 'opinion':
            mapping = {
                'Very unfavorable': 1,
                'Unfavorable': 2,
                'Neither favorable nor unfavorable': 3,
                'Favorable': 4,
                'Very favorable': 5
            }
        
        return series.map(mapping).fillna(0)
    
    # Create correlation matrices for different demographic groups
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Demographic Correlations with AI Attitudes', fontsize=16, fontweight='bold')
    
    # 1. Age Group vs AI Attitudes
    ax1 = axes[0, 0]
    age_attitudes = []
    age_groups = ['18 to 25 years old', '26 to 35 years old', '36 to 45 years old', 
                  '46 to 55 years old', '56 to 65 years old', '66 to 75 years old']
    
    for age_group in age_groups:
        age_data = df_clean[df_clean['age_group'] == age_group]
        if len(age_data) > 5:  # Only include groups with sufficient data
            age_scores = []
            for measure, column in attitude_measures.items():
                if measure == 'AI Training':
                    scores = convert_to_score(age_data[column], 'training')
                elif measure == 'AI Experience':
                    scores = convert_to_score(age_data[column], 'experience')
                elif measure == 'AI Confidence':
                    scores = convert_to_score(age_data[column], 'confidence')
                elif measure == 'AI Willingness':
                    scores = convert_to_score(age_data[column], 'willingness')
                elif measure == 'AI Opinion':
                    scores = convert_to_score(age_data[column], 'opinion')
                else:  # AI Familiarity
                    scores = convert_to_score(age_data[column], 'familiarity')
                
                avg_score = scores.mean() if len(scores) > 0 else 0
                age_scores.append(avg_score)
            age_attitudes.append(age_scores)
        else:
            age_attitudes.append([0] * len(attitude_measures))
    
    age_attitudes = np.array(age_attitudes)
    sns.heatmap(age_attitudes, 
                xticklabels=list(attitude_measures.keys()),
                yticklabels=age_groups,
                annot=True, fmt='.2f', cmap='RdYlBu_r',
                ax=ax1, cbar_kws={'label': 'Average Score'})
    ax1.set_title('Age Group vs AI Attitudes')
    ax1.set_xlabel('AI Attitude Measures')
    ax1.set_ylabel('Age Groups')
    
    # 2. Professional Role vs AI Attitudes
    ax2 = axes[0, 1]
    role_attitudes = []
    roles = ['Physician', 'Advanced Practitioner (Nurse Practitioner or Physician Assistant)', 
             'Medical Student', 'Resident or Fellow']
    
    for role in roles:
        role_data = df_clean[df_clean['role'] == role]
        if len(role_data) > 5:
            role_scores = []
            for measure, column in attitude_measures.items():
                if measure == 'AI Training':
                    scores = convert_to_score(role_data[column], 'training')
                elif measure == 'AI Experience':
                    scores = convert_to_score(role_data[column], 'experience')
                elif measure == 'AI Confidence':
                    scores = convert_to_score(role_data[column], 'confidence')
                elif measure == 'AI Willingness':
                    scores = convert_to_score(role_data[column], 'willingness')
                elif measure == 'AI Opinion':
                    scores = convert_to_score(role_data[column], 'opinion')
                else:  # AI Familiarity
                    scores = convert_to_score(role_data[column], 'familiarity')
                
                avg_score = scores.mean() if len(scores) > 0 else 0
                role_scores.append(avg_score)
            role_attitudes.append(role_scores)
        else:
            role_attitudes.append([0] * len(attitude_measures))
    
    role_attitudes = np.array(role_attitudes)
    sns.heatmap(role_attitudes, 
                xticklabels=list(attitude_measures.keys()),
                yticklabels=roles,
                annot=True, fmt='.2f', cmap='RdYlBu_r',
                ax=ax2, cbar_kws={'label': 'Average Score'})
    ax2.set_title('Professional Role vs AI Attitudes')
    ax2.set_xlabel('AI Attitude Measures')
    ax2.set_ylabel('Professional Roles')
    
    # 3. Specialty vs AI Attitudes
    ax3 = axes[1, 0]
    specialty_attitudes = []
    specialties = ['Pediatrics', 'Family Medicine', 'Neurology', 'Radiology', 
                   'Cardiology', 'Emergency Medicine', 'Internal Medicine']
    
    for specialty in specialties:
        spec_data = df_clean[df_clean['specialty_category'] == specialty]
        if len(spec_data) > 5:
            spec_scores = []
            for measure, column in attitude_measures.items():
                if measure == 'AI Training':
                    scores = convert_to_score(spec_data[column], 'training')
                elif measure == 'AI Experience':
                    scores = convert_to_score(spec_data[column], 'experience')
                elif measure == 'AI Confidence':
                    scores = convert_to_score(spec_data[column], 'confidence')
                elif measure == 'AI Willingness':
                    scores = convert_to_score(spec_data[column], 'willingness')
                elif measure == 'AI Opinion':
                    scores = convert_to_score(spec_data[column], 'opinion')
                else:  # AI Familiarity
                    scores = convert_to_score(spec_data[column], 'familiarity')
                
                avg_score = scores.mean() if len(scores) > 0 else 0
                spec_scores.append(avg_score)
            specialty_attitudes.append(spec_scores)
        else:
            specialty_attitudes.append([0] * len(attitude_measures))
    
    specialty_attitudes = np.array(specialty_attitudes)
    sns.heatmap(specialty_attitudes, 
                xticklabels=list(attitude_measures.keys()),
                yticklabels=specialties,
                annot=True, fmt='.2f', cmap='RdYlBu_r',
                ax=ax3, cbar_kws={'label': 'Average Score'})
    ax3.set_title('Medical Specialty vs AI Attitudes')
    ax3.set_xlabel('AI Attitude Measures')
    ax3.set_ylabel('Medical Specialties')
    
    # 4. Overall AI Readiness Score by Demographics
    ax4 = axes[1, 1]
    
    # Calculate overall AI readiness score for each demographic group
    readiness_data = []
    
    # Age groups
    for age_group in age_groups:
        age_data = df_clean[df_clean['age_group'] == age_group]
        if len(age_data) > 5:
            scores = []
            for column in attitude_measures.values():
                if 'familiar' in column:
                    scores.extend(convert_to_score(age_data[column], 'familiarity'))
                elif 'training' in column:
                    scores.extend(convert_to_score(age_data[column], 'training'))
                elif 'experience' in column:
                    scores.extend(convert_to_score(age_data[column], 'experience'))
                elif 'confidence' in column:
                    scores.extend(convert_to_score(age_data[column], 'confidence'))
                elif 'willing' in column:
                    scores.extend(convert_to_score(age_data[column], 'willingness'))
                elif 'opinion' in column:
                    scores.extend(convert_to_score(age_data[column], 'opinion'))
            
            avg_readiness = np.mean(scores) if len(scores) > 0 else 0
            readiness_data.append(('Age', age_group, avg_readiness, len(age_data)))
    
    # Roles
    for role in roles:
        role_data = df_clean[df_clean['role'] == role]
        if len(role_data) > 5:
            scores = []
            for column in attitude_measures.values():
                if 'familiar' in column:
                    scores.extend(convert_to_score(role_data[column], 'familiarity'))
                elif 'training' in column:
                    scores.extend(convert_to_score(role_data[column], 'training'))
                elif 'experience' in column:
                    scores.extend(convert_to_score(role_data[column], 'experience'))
                elif 'confidence' in column:
                    scores.extend(convert_to_score(role_data[column], 'confidence'))
                elif 'willing' in column:
                    scores.extend(convert_to_score(role_data[column], 'willingness'))
                elif 'opinion' in column:
                    scores.extend(convert_to_score(role_data[column], 'opinion'))
            
            avg_readiness = np.mean(scores) if len(scores) > 0 else 0
            readiness_data.append(('Role', role, avg_readiness, len(role_data)))
    
    # Create readiness comparison
    readiness_df = pd.DataFrame(readiness_data, columns=['Category', 'Group', 'Readiness', 'Count'])
    
    # Create bar plot
    categories = readiness_df['Category'].unique()
    x_pos = np.arange(len(categories))
    colors = ['#FF6B6B', '#4ECDC4']
    
    for i, category in enumerate(categories):
        cat_data = readiness_df[readiness_df['Category'] == category]
        ax4.bar(x_pos[i], cat_data['Readiness'].mean(), color=colors[i], alpha=0.7, 
                label=f'{category} (n={cat_data["Count"].sum()})')
    
    ax4.set_title('Overall AI Readiness by Demographic Category')
    ax4.set_xlabel('Demographic Category')
    ax4.set_ylabel('Average AI Readiness Score')
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(categories)
    ax4.legend()
    ax4.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    # Save the figure
    plt.savefig('fig14_demographic_heatmap.png', dpi=300, bbox_inches='tight')
    plt.savefig('fig14_demographic_heatmap.pdf', bbox_inches='tight')
    
    # Show the figure
    plt.show()
    
    # Print detailed analysis
    print("Demographic vs AI Attitudes - Heatmap Analysis:")
    print("=" * 60)
    
    print("\nAge Group Analysis:")
    for i, age_group in enumerate(age_groups):
        if i < len(age_attitudes):
            scores = age_attitudes[i]
            print(f"{age_group}: {scores.mean():.2f} average score")
    
    print("\nProfessional Role Analysis:")
    for i, role in enumerate(roles):
        if i < len(role_attitudes):
            scores = role_attitudes[i]
            print(f"{role}: {scores.mean():.2f} average score")
    
    print("\nSpecialty Analysis:")
    for i, specialty in enumerate(specialties):
        if i < len(specialty_attitudes):
            scores = specialty_attitudes[i]
            print(f"{specialty}: {scores.mean():.2f} average score")
    
    print(f"\nOverall AI Readiness by Category:")
    for category in categories:
        cat_data = readiness_df[readiness_df['Category'] == category]
        print(f"{category}: {cat_data['Readiness'].mean():.2f} average readiness")

if __name__ == "__main__":
    create_demographic_heatmap()
