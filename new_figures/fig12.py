#!/usr/bin/env python3
"""
Figure 12: AI Adoption Journey - Circular Flow Diagram
Shows the progression from awareness → training → experience → confidence → adoption
with flow thickness representing participant counts at each stage.

To run: conda activate eda && python fig12.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Circle
import matplotlib.patches as mpatches

def create_ai_adoption_journey():
    """Create circular flow diagram showing AI adoption journey"""
    
    # Read the survey data
    df = pd.read_excel('../data/S2_Survey_Data.xlsx', sheet_name='Sheet 1')
    
    # Calculate flow data
    total_participants = len(df)
    
    # Stage 1: AI Familiarity (Awareness)
    familiarity_counts = df['ai_familiar.q10'].value_counts(dropna=True)
    familiarity_total = df['ai_familiar.q10'].notna().sum()
    
    # Stage 2: AI Training
    training_counts = df['ai_training.q18'].value_counts(dropna=True)
    training_total = df['ai_training.q18'].notna().sum()
    
    # Stage 3: AI Experience
    experience_counts = df['ai_experience.q11'].value_counts(dropna=True)
    experience_total = df['ai_experience.q11'].notna().sum()
    
    # Stage 4: AI Confidence
    confidence_counts = df['ai_use_confidence.q19'].value_counts(dropna=True)
    confidence_total = df['ai_use_confidence.q19'].notna().sum()
    
    # Stage 5: AI Willingness (Adoption)
    willingness_counts = df['ai_willing_to_use.q12'].value_counts(dropna=True)
    willingness_total = df['ai_willing_to_use.q12'].notna().sum()
    
    # Create the figure
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_xlim(-6, 6)
    ax.set_ylim(-6, 6)
    ax.set_aspect('equal')
    
    # Define stage positions in a circle
    stages = [
        ('Awareness\n(AI Familiarity)', 0, 4, '#FF6B6B'),
        ('Training\n(AI Education)', 3.5, 1.5, '#4ECDC4'),
        ('Experience\n(AI Usage)', 3.5, -1.5, '#45B7D1'),
        ('Confidence\n(AI Skills)', 0, -4, '#96CEB4'),
        ('Adoption\n(Willingness)', -3.5, 0, '#FFEAA7')
    ]
    
    # Draw stage circles
    stage_circles = []
    for i, (name, x, y, color) in enumerate(stages):
        # Calculate size based on positive responses
        if i == 0:  # Awareness - count "Moderately familiar" and above
            positive_count = sum(familiarity_counts.get(level, 0) for level in 
                               ['Moderately familiar', 'Very familiar', 'Extremely familiar'])
        elif i == 1:  # Training - count "Yes" responses
            positive_count = training_counts.get('Yes', 0) + training_counts.get('Yes, but very limited', 0)
        elif i == 2:  # Experience - count "Yes" responses
            positive_count = experience_counts.get('Yes', 0)
        elif i == 3:  # Confidence - count "Moderately confident" and above
            positive_count = sum(confidence_counts.get(level, 0) for level in 
                               ['Moderately confident', 'Very confident', 'Extremely confident'])
        else:  # Adoption - count "Moderately willing" and above
            positive_count = sum(willingness_counts.get(level, 0) for level in 
                               ['Moderately willing', 'Very willing', 'Extremely willing'])
        
        # Scale circle size (minimum 0.5, maximum 1.5)
        size = 0.5 + (positive_count / max(positive_count, 1)) * 1.0
        
        circle = Circle((x, y), size, facecolor=color, alpha=0.7, edgecolor='black', linewidth=2)
        ax.add_patch(circle)
        stage_circles.append(circle)
        
        # Add stage labels
        ax.text(x, y, f'{name}\n({positive_count})', ha='center', va='center', 
                fontsize=10, fontweight='bold', color='white')
    
    # Draw flow arrows between stages
    arrow_props = dict(arrowstyle='->', lw=3, alpha=0.8)
    
    # Define flow paths (clockwise)
    flows = [
        (0, 1, 0.8),  # Awareness → Training
        (1, 2, 0.6),  # Training → Experience  
        (2, 3, 0.7),  # Experience → Confidence
        (3, 4, 0.9),  # Confidence → Adoption
        (4, 0, 0.5)   # Adoption → Awareness (feedback loop)
    ]
    
    for start_idx, end_idx, flow_strength in flows:
        start_x, start_y = stages[start_idx][1], stages[start_idx][2]
        end_x, end_y = stages[end_idx][1], stages[end_idx][2]
        
        # Calculate arrow position (from edge to edge)
        dx = end_x - start_x
        dy = end_y - start_y
        distance = np.sqrt(dx**2 + dy**2)
        
        # Normalize and scale to circle edges
        start_radius = 0.5 + (stages[start_idx][3] != '#FF6B6B') * 0.5  # Approximate radius
        end_radius = 0.5 + (stages[end_idx][3] != '#FF6B6B') * 0.5
        
        start_x_adj = start_x + (dx / distance) * start_radius
        start_y_adj = start_y + (dy / distance) * start_radius
        end_x_adj = end_x - (dx / distance) * end_radius
        end_y_adj = end_y - (dy / distance) * end_radius
        
        # Draw arrow with thickness based on flow strength
        arrow = mpatches.FancyArrowPatch(
            (start_x_adj, start_y_adj), (end_x_adj, end_y_adj),
            arrowstyle='->', mutation_scale=20, 
            color='black', alpha=flow_strength,
            linewidth=2 + flow_strength * 3
        )
        ax.add_patch(arrow)
    
    # Add title and statistics
    ax.set_title('AI Adoption Journey in Healthcare\nCircular Flow of Participant Progression', 
                fontsize=16, fontweight='bold', pad=20)
    
    # Add summary statistics
    stats_text = f"""
    Total Participants: {total_participants}
    
    Key Insights:
    • {sum(familiarity_counts.get(level, 0) for level in ['Moderately familiar', 'Very familiar', 'Extremely familiar'])} participants familiar with AI
    • {training_counts.get('Yes', 0) + training_counts.get('Yes, but very limited', 0)} have some AI training
    • {experience_counts.get('Yes', 0)} have AI experience
    • {sum(confidence_counts.get(level, 0) for level in ['Moderately confident', 'Very confident', 'Extremely confident'])} confident in AI use
    • {sum(willingness_counts.get(level, 0) for level in ['Moderately willing', 'Very willing', 'Extremely willing'])} willing to adopt AI
    """
    
    ax.text(-5.5, -5.5, stats_text, fontsize=10, va='top', ha='left',
            bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgray', alpha=0.8))
    
    # Remove axes
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    # Save the figure
    plt.tight_layout()
    plt.savefig('fig12_ai_adoption_journey.png', dpi=300, bbox_inches='tight')
    plt.savefig('fig12_ai_adoption_journey.pdf', bbox_inches='tight')
    
    # Show the figure
    plt.show()
    
    # Print detailed statistics
    print("AI Adoption Journey Analysis:")
    print("=" * 50)
    print(f"Total participants: {total_participants}")
    print(f"\nStage 1 - Awareness (AI Familiarity):")
    for level, count in familiarity_counts.items():
        pct = (count / familiarity_total) * 100
        print(f"  {level}: {count} ({pct:.1f}%)")
    
    print(f"\nStage 2 - Training:")
    for level, count in training_counts.items():
        pct = (count / training_total) * 100
        print(f"  {level}: {count} ({pct:.1f}%)")
    
    print(f"\nStage 3 - Experience:")
    for level, count in experience_counts.items():
        pct = (count / experience_total) * 100
        print(f"  {level}: {count} ({pct:.1f}%)")
    
    print(f"\nStage 4 - Confidence:")
    for level, count in confidence_counts.items():
        pct = (count / confidence_total) * 100
        print(f"  {level}: {count} ({pct:.1f}%)")
    
    print(f"\nStage 5 - Adoption (Willingness):")
    for level, count in willingness_counts.items():
        pct = (count / willingness_total) * 100
        print(f"  {level}: {count} ({pct:.1f}%)")

if __name__ == "__main__":
    create_ai_adoption_journey()
