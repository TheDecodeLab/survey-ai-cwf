#!/usr/bin/env python3
"""
Figure 17: Career Stage → AI Readiness - Sankey Diagram
Multi-layer Sankey showing how medical career stage (student → resident → practitioner)
influences AI training, confidence, and adoption patterns.

To run: conda activate eda && python fig17.py
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

def create_career_sankey():
    """Create Sankey diagram showing career stage progression to AI readiness"""
    
    # Read the survey data
    df = pd.read_excel('../data/S2_Survey_Data.xlsx', sheet_name='Sheet 1')
    
    # Clean and categorize professional roles
    def categorize_career_stage(role):
        if pd.isna(role):
            return 'Unknown'
        role_str = str(role).lower()
        if 'student' in role_str:
            return 'Medical Student'
        elif 'resident' in role_str or 'fellow' in role_str:
            return 'Resident/Fellow'
        elif 'physician' in role_str:
            return 'Practicing Physician'
        elif 'advanced practitioner' in role_str or 'nurse practitioner' in role_str or 'physician assistant' in role_str:
            return 'Advanced Practitioner'
        else:
            return 'Other'
    
    df['career_stage'] = df['pro_role.q4'].apply(categorize_career_stage)
    
    # Categorize AI training levels
    def categorize_training(training):
        if pd.isna(training):
            return 'No Training'
        training_str = str(training).lower()
        if 'no' in training_str:
            return 'No Training'
        elif 'limited' in training_str:
            return 'Limited Training'
        elif 'yes' in training_str:
            return 'Full Training'
        else:
            return 'No Training'
    
    df['training_level'] = df['ai_training.q18'].apply(categorize_training)
    
    # Categorize AI confidence levels
    def categorize_confidence(confidence):
        if pd.isna(confidence):
            return 'No Confidence'
        confidence_str = str(confidence).lower()
        if 'not at all' in confidence_str:
            return 'No Confidence'
        elif 'slightly' in confidence_str:
            return 'Low Confidence'
        elif 'moderately' in confidence_str:
            return 'Moderate Confidence'
        elif 'very' in confidence_str:
            return 'High Confidence'
        elif 'extremely' in confidence_str:
            return 'Very High Confidence'
        else:
            return 'No Confidence'
    
    df['confidence_level'] = df['ai_use_confidence.q19'].apply(categorize_confidence)
    
    # Categorize AI willingness levels
    def categorize_willingness(willingness):
        if pd.isna(willingness):
            return 'Not Willing'
        willingness_str = str(willingness).lower()
        if 'not at all' in willingness_str:
            return 'Not Willing'
        elif 'slightly' in willingness_str:
            return 'Slightly Willing'
        elif 'moderately' in willingness_str:
            return 'Moderately Willing'
        elif 'very' in willingness_str:
            return 'Very Willing'
        elif 'extremely' in willingness_str:
            return 'Extremely Willing'
        else:
            return 'Not Willing'
    
    df['willingness_level'] = df['ai_willing_to_use.q12'].apply(categorize_willingness)
    
    # Create the Sankey diagram
    # Define node labels and positions
    career_stages = ['Medical Student', 'Resident/Fellow', 'Practicing Physician', 'Advanced Practitioner']
    training_levels = ['No Training', 'Limited Training', 'Full Training']
    confidence_levels = ['No Confidence', 'Low Confidence', 'Moderate Confidence', 'High Confidence', 'Very High Confidence']
    willingness_levels = ['Not Willing', 'Slightly Willing', 'Moderately Willing', 'Very Willing', 'Extremely Willing']
    
    # Create all labels
    all_labels = career_stages + training_levels + confidence_levels + willingness_levels
    
    # Create label to index mapping
    label_to_index = {label: i for i, label in enumerate(all_labels)}
    
    # Calculate flows
    sources = []
    targets = []
    values = []
    colors = []
    
    # Career Stage → Training Level flows
    for career_stage in career_stages:
        career_data = df[df['career_stage'] == career_stage]
        if len(career_data) > 0:
            for training_level in training_levels:
                count = len(career_data[career_data['training_level'] == training_level])
                if count > 0:
                    sources.append(label_to_index[career_stage])
                    targets.append(label_to_index[training_level])
                    values.append(count)
                    colors.append('rgba(255, 107, 107, 0.6)')  # Red for career stage
    
    # Training Level → Confidence Level flows
    for training_level in training_levels:
        training_data = df[df['training_level'] == training_level]
        if len(training_data) > 0:
            for confidence_level in confidence_levels:
                count = len(training_data[training_data['confidence_level'] == confidence_level])
                if count > 0:
                    sources.append(label_to_index[training_level])
                    targets.append(label_to_index[confidence_level])
                    values.append(count)
                    colors.append('rgba(78, 205, 196, 0.6)')  # Teal for training
    
    # Confidence Level → Willingness Level flows
    for confidence_level in confidence_levels:
        confidence_data = df[df['confidence_level'] == confidence_level]
        if len(confidence_data) > 0:
            for willingness_level in willingness_levels:
                count = len(confidence_data[confidence_data['willingness_level'] == willingness_level])
                if count > 0:
                    sources.append(label_to_index[confidence_level])
                    targets.append(label_to_index[willingness_level])
                    values.append(count)
                    colors.append('rgba(69, 183, 209, 0.6)')  # Blue for confidence
    
    # Create node colors
    node_colors = []
    for i, label in enumerate(all_labels):
        if i < len(career_stages):
            node_colors.append('#FF6B6B')  # Red for career stages
        elif i < len(career_stages) + len(training_levels):
            node_colors.append('#4ECDC4')  # Teal for training
        elif i < len(career_stages) + len(training_levels) + len(confidence_levels):
            node_colors.append('#45B7D1')  # Blue for confidence
        else:
            node_colors.append('#96CEB4')  # Green for willingness
    
    # Create the Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_labels,
            color=node_colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=colors
        )
    )])
    
    # Update layout
    fig.update_layout(
        title_text="Career Stage Progression to AI Readiness<br>Medical Career Development → AI Training → Confidence → Willingness",
        font=dict(size=12, color="black"),
        width=1000,
        height=600,
        margin=dict(b=80, t=80)
    )
    
    # Add annotations for layer titles
    annotations = [
        dict(
            x=0.1, y=-0.15,
            xref='paper', yref='paper',
            text="<b>Career Stage</b>",
            showarrow=False,
            font=dict(size=14, color='black'),
            xanchor='center'
        ),
        dict(
            x=0.35, y=-0.15,
            xref='paper', yref='paper',
            text="<b>AI Training</b>",
            showarrow=False,
            font=dict(size=14, color='black'),
            xanchor='center'
        ),
        dict(
            x=0.65, y=-0.15,
            xref='paper', yref='paper',
            text="<b>AI Confidence</b>",
            showarrow=False,
            font=dict(size=14, color='black'),
            xanchor='center'
        ),
        dict(
            x=0.9, y=-0.15,
            xref='paper', yref='paper',
            text="<b>AI Willingness</b>",
            showarrow=False,
            font=dict(size=14, color='black'),
            xanchor='center'
        )
    ]
    
    fig.update_layout(annotations=annotations)
    
    # Save the figure
    fig.write_html('fig17_career_sankey.html')
    fig.write_image('fig17_career_sankey.png', width=1000, height=600)
    fig.write_image('fig17_career_sankey.pdf', width=1000, height=600)
    
    # Show the figure
    fig.show()
    
    # Print detailed analysis
    print("Career Stage → AI Readiness - Sankey Analysis:")
    print("=" * 60)
    
    print(f"\nCareer Stage Distribution:")
    career_counts = df['career_stage'].value_counts()
    for stage, count in career_counts.items():
        pct = (count / len(df)) * 100
        print(f"  {stage}: {count} ({pct:.1f}%)")
    
    print(f"\nAI Training by Career Stage:")
    training_by_career = df.groupby('career_stage')['training_level'].value_counts(normalize=True)
    for stage in career_stages:
        if stage in training_by_career.index.get_level_values(0):
            print(f"\n{stage}:")
            stage_training = training_by_career[stage]
            for training, pct in stage_training.items():
                print(f"  {training}: {pct:.1%}")
    
    print(f"\nAI Confidence by Career Stage:")
    confidence_by_career = df.groupby('career_stage')['confidence_level'].value_counts(normalize=True)
    for stage in career_stages:
        if stage in confidence_by_career.index.get_level_values(0):
            print(f"\n{stage}:")
            stage_confidence = confidence_by_career[stage]
            for confidence, pct in stage_confidence.items():
                print(f"  {confidence}: {pct:.1%}")
    
    print(f"\nAI Willingness by Career Stage:")
    willingness_by_career = df.groupby('career_stage')['willingness_level'].value_counts(normalize=True)
    for stage in career_stages:
        if stage in willingness_by_career.index.get_level_values(0):
            print(f"\n{stage}:")
            stage_willingness = willingness_by_career[stage]
            for willingness, pct in stage_willingness.items():
                print(f"  {willingness}: {pct:.1%}")
    
    # Calculate AI readiness progression
    print(f"\nAI Readiness Progression Analysis:")
    for stage in career_stages:
        stage_data = df[df['career_stage'] == stage]
        if len(stage_data) > 0:
            # Calculate readiness score (0-100)
            training_scores = stage_data['training_level'].map({
                'No Training': 0, 'Limited Training': 50, 'Full Training': 100
            }).fillna(0)
            
            confidence_scores = stage_data['confidence_level'].map({
                'No Confidence': 0, 'Low Confidence': 25, 'Moderate Confidence': 50,
                'High Confidence': 75, 'Very High Confidence': 100
            }).fillna(0)
            
            willingness_scores = stage_data['willingness_level'].map({
                'Not Willing': 0, 'Slightly Willing': 25, 'Moderately Willing': 50,
                'Very Willing': 75, 'Extremely Willing': 100
            }).fillna(0)
            
            avg_training = training_scores.mean()
            avg_confidence = confidence_scores.mean()
            avg_willingness = willingness_scores.mean()
            overall_readiness = (avg_training + avg_confidence + avg_willingness) / 3
            
            print(f"{stage}:")
            print(f"  Training: {avg_training:.1f}")
            print(f"  Confidence: {avg_confidence:.1f}")
            print(f"  Willingness: {avg_willingness:.1f}")
            print(f"  Overall Readiness: {overall_readiness:.1f}")

if __name__ == "__main__":
    create_career_sankey()
