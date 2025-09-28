#!/usr/bin/env python3
"""
Figure 13: AI Perceptions by Specialty - Radar Chart
Multi-dimensional radar chart comparing different specialties across key dimensions
(benefits, concerns, confidence, willingness) to show specialty-specific AI attitudes.

To run: conda activate eda && python fig13.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from math import pi
import seaborn as sns

def create_radar_chart():
    """Create radar chart comparing AI perceptions across medical specialties"""
    
    # Read the survey data
    df = pd.read_excel('../data/S2_Survey_Data.xlsx', sheet_name='Sheet 1')
    
    # Get top specialties with sufficient data
    specialty_counts = df['med_specialty.q8'].value_counts()
    top_specialties = specialty_counts[specialty_counts >= 10].index.tolist()
    
    # Remove NaN and 'Something else' categories
    top_specialties = [spec for spec in top_specialties if pd.notna(spec) and 'Something else' not in str(spec)]
    
    # Define dimensions for radar chart
    dimensions = [
        'AI Familiarity',
        'AI Training', 
        'AI Experience',
        'AI Confidence',
        'AI Willingness',
        'Positive Opinion',
        'Perceived Benefits',
        'AI Concerns'
    ]
    
    # Calculate scores for each specialty and dimension
    specialty_scores = {}
    
    for specialty in top_specialties[:6]:  # Limit to top 6 for readability
        spec_data = df[df['med_specialty.q8'] == specialty]
        scores = []
        
        # 1. AI Familiarity (0-100 scale)
        familiarity = spec_data['ai_familiar.q10'].value_counts(normalize=True)
        familiarity_score = (
            familiarity.get('Not at all familiar', 0) * 0 +
            familiarity.get('Slightly familiar', 0) * 25 +
            familiarity.get('Moderately familiar', 0) * 50 +
            familiarity.get('Very familiar', 0) * 75 +
            familiarity.get('Extremely familiar', 0) * 100
        )
        scores.append(familiarity_score)
        
        # 2. AI Training (0-100 scale)
        training = spec_data['ai_training.q18'].value_counts(normalize=True)
        training_score = (
            training.get('No', 0) * 0 +
            training.get('Yes, but very limited', 0) * 50 +
            training.get('Yes', 0) * 100
        )
        scores.append(training_score)
        
        # 3. AI Experience (0-100 scale)
        experience = spec_data['ai_experience.q11'].value_counts(normalize=True)
        experience_score = (
            experience.get('No', 0) * 0 +
            experience.get('Unsure', 0) * 25 +
            experience.get('Yes', 0) * 100
        )
        scores.append(experience_score)
        
        # 4. AI Confidence (0-100 scale)
        confidence = spec_data['ai_use_confidence.q19'].value_counts(normalize=True)
        confidence_score = (
            confidence.get('Not at all confident', 0) * 0 +
            confidence.get('Slightly confident', 0) * 25 +
            confidence.get('Moderately confident', 0) * 50 +
            confidence.get('Very confident', 0) * 75 +
            confidence.get('Extremely confident', 0) * 100
        )
        scores.append(confidence_score)
        
        # 5. AI Willingness (0-100 scale)
        willingness = spec_data['ai_willing_to_use.q12'].value_counts(normalize=True)
        willingness_score = (
            willingness.get('Not at all willing', 0) * 0 +
            willingness.get('Slightly willing', 0) * 25 +
            willingness.get('Moderately willing', 0) * 50 +
            willingness.get('Very willing', 0) * 75 +
            willingness.get('Extremely willing', 0) * 100
        )
        scores.append(willingness_score)
        
        # 6. Positive Opinion (0-100 scale)
        opinion = spec_data['ai_use_gen_opinion.q13'].value_counts(normalize=True)
        opinion_score = (
            opinion.get('Very unfavorable', 0) * 0 +
            opinion.get('Unfavorable', 0) * 25 +
            opinion.get('Neither favorable nor unfavorable', 0) * 50 +
            opinion.get('Favorable', 0) * 75 +
            opinion.get('Very favorable', 0) * 100
        )
        scores.append(opinion_score)
        
        # 7. Perceived Benefits (0-100 scale based on benefit mentions)
        benefits_data = spec_data['ai_benefits.q31'].dropna()
        if len(benefits_data) > 0:
            all_benefits = []
            for response in benefits_data:
                benefits = [b.strip() for b in str(response).split(',')]
                all_benefits.extend(benefits)
            # Calculate percentage of participants who mentioned benefits
            benefits_score = (len(benefits_data) / len(spec_data)) * 100
        else:
            benefits_score = 0
        scores.append(benefits_score)
        
        # 8. AI Concerns (inverted scale - higher concerns = lower score)
        concerns_data = spec_data['ai_concerns.q32'].dropna()
        if len(concerns_data) > 0:
            # Calculate percentage of participants who mentioned concerns
            concerns_score = (len(concerns_data) / len(spec_data)) * 100
            concerns_score = 100 - concerns_score  # Invert so higher concerns = lower score
        else:
            concerns_score = 100
        scores.append(concerns_score)
        
        specialty_scores[specialty] = scores
    
    # Create the radar chart
    fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(projection='polar'))
    
    # Set up angles for each dimension
    angles = [n / float(len(dimensions)) * 2 * pi for n in range(len(dimensions))]
    angles += angles[:1]  # Complete the circle
    
    # Define colors for each specialty
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
    
    # Plot each specialty
    for i, (specialty, scores) in enumerate(specialty_scores.items()):
        scores += scores[:1]  # Complete the circle
        ax.plot(angles, scores, 'o-', linewidth=2, label=specialty, color=colors[i])
        ax.fill(angles, scores, alpha=0.25, color=colors[i])
    
    # Customize the chart
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dimensions, fontsize=10)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=8)
    ax.grid(True)
    
    # Add title
    plt.title('AI Perceptions by Medical Specialty\nMulti-dimensional Comparison', 
              size=16, fontweight='bold', pad=20)
    
    # Add legend
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=10)
    
    # Add grid lines
    ax.set_rlabel_position(0)
    
    # Save the figure
    plt.tight_layout()
    plt.savefig('fig13_radar_specialty_perceptions.png', dpi=300, bbox_inches='tight')
    plt.savefig('fig13_radar_specialty_perceptions.pdf', bbox_inches='tight')
    
    # Show the figure
    plt.show()
    
    # Print detailed analysis
    print("AI Perceptions by Specialty - Radar Chart Analysis:")
    print("=" * 60)
    
    for specialty, scores in specialty_scores.items():
        print(f"\n{specialty} (n={len(df[df['med_specialty.q8'] == specialty])}):")
        for i, (dimension, score) in enumerate(zip(dimensions, scores)):
            print(f"  {dimension}: {score:.1f}")
        
        # Calculate overall AI readiness score (average of first 5 dimensions)
        readiness_score = np.mean(scores[:5])
        print(f"  Overall AI Readiness: {readiness_score:.1f}")
    
    # Find specialty with highest AI readiness
    readiness_scores = {spec: np.mean(scores[:5]) for spec, scores in specialty_scores.items()}
    best_specialty = max(readiness_scores, key=readiness_scores.get)
    print(f"\nHighest AI Readiness: {best_specialty} ({readiness_scores[best_specialty]:.1f})")
    
    # Find specialty with most concerns
    concern_scores = {spec: scores[7] for spec, scores in specialty_scores.items()}
    most_concerns = min(concern_scores, key=concern_scores.get)
    print(f"Most AI Concerns: {most_concerns} ({100 - concern_scores[most_concerns]:.1f})")

if __name__ == "__main__":
    create_radar_chart()
