#!/usr/bin/env python3
"""
Script to create a diverging stacked bar chart from survey data.
This recreates the Likert scale visualization from the survey responses.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches

def load_and_process_data(file_path):
    """Load Excel data and process Likert scale responses into 4 categories."""
    
    # Load the data
    df = pd.read_excel(file_path)
    
    # Define the 8 questions to analyze
    questions = [
        'ai_familiar.q10',
        'ai_willing_to_use.q12', 
        'ai_use_gen_opinion.q13',
        'ai_improve_healthcare_practices.q14',
        'ai_improve_health_outcomes.q15',
        'ai_required_likelihood.q16',
        'ai_knowledge.q17',
        'ai_use_confidence.q19'
    ]
    
    # Question labels for display
    question_labels = [
        'AI Familiarity',
        'Willingness to Use AI',
        'General Opinion of AI',
        'AI Improves Healthcare Practices',
        'AI Improves Health Outcomes',
        'AI Required Likelihood',
        'AI Knowledge Level',
        'AI Use Confidence'
    ]
    
    # Process each question
    processed_data = []
    
    for i, col in enumerate(questions):
        if col not in df.columns:
            print(f"Warning: Column {col} not found in data")
            continue
            
        value_counts = df[col].value_counts()
        total = df[col].dropna().shape[0]
        
        # Map responses to 4 categories based on Likert scale patterns
        if col == 'ai_familiar.q10':
            # Familiarity: Not at all -> Least, Slightly -> Neutral Left, Moderately -> Neutral Right, Very/Extremely -> Most
            least = value_counts.get('Not at all familiar', 0)
            neutral_left = value_counts.get('Slightly familiar', 0)
            neutral_right = value_counts.get('Moderately familiar', 0)
            most = value_counts.get('Very familiar', 0) + value_counts.get('Extremely familiar', 0)
            
        elif col == 'ai_willing_to_use.q12':
            # Willingness: Not at all -> Least, Slightly -> Neutral Left, Moderately -> Neutral Right, Very/Extremely -> Most
            least = value_counts.get('Not at all willing', 0)
            neutral_left = value_counts.get('Slightly willing', 0)
            neutral_right = value_counts.get('Moderately willing', 0)
            most = value_counts.get('Very willing', 0) + value_counts.get('Extremely willing', 0)
            
        elif col == 'ai_use_gen_opinion.q13':
            # Opinion: Very unfavorable -> Least, Unfavorable -> Neutral Left, Neither -> Neutral Right, Favorable/Very favorable -> Most
            least = value_counts.get('Very unfavorable', 0)
            neutral_left = value_counts.get('Unfavorable', 0)
            neutral_right = value_counts.get('Neither favorable nor unfavorable', 0)
            most = value_counts.get('Favorable', 0) + value_counts.get('Very favorable', 0)
            
        elif col in ['ai_improve_healthcare_practices.q14', 'ai_improve_health_outcomes.q15']:
            # Importance: Not at all -> Least, Somewhat -> Neutral Left, Important -> Neutral Right, Very/Extremely -> Most
            least = value_counts.get('Not at all important', 0)
            neutral_left = value_counts.get('Somewhat important', 0)
            neutral_right = value_counts.get('Important', 0)
            most = value_counts.get('Very important', 0) + value_counts.get('Extremely important', 0)
            
        elif col == 'ai_required_likelihood.q16':
            # Likelihood: Extremely unlikely -> Least, Unlikely -> Neutral Left, Likely -> Neutral Right, Extremely likely -> Most
            least = value_counts.get('Extremely unlikely', 0)
            neutral_left = value_counts.get('Unlikely', 0)
            neutral_right = value_counts.get('Likely', 0)
            most = value_counts.get('Extremely likely', 0)
            
        elif col == 'ai_knowledge.q17':
            # Knowledge: Very low -> Least, Low -> Neutral Left, Moderate -> Neutral Right, High/Very high -> Most
            least = value_counts.get('Very low', 0)
            neutral_left = value_counts.get('Low', 0)
            neutral_right = value_counts.get('Moderate', 0)
            most = value_counts.get('High', 0) + value_counts.get('Very high', 0)
            
        elif col == 'ai_use_confidence.q19':
            # Confidence: Not at all -> Least, Slightly -> Neutral Left, Moderately -> Neutral Right, Very/Extremely -> Most
            least = value_counts.get('Not at all confident', 0)
            neutral_left = value_counts.get('Slightly confident', 0)
            neutral_right = value_counts.get('Moderately confident', 0)
            most = value_counts.get('Very confident', 0) + value_counts.get('Extremely confident', 0)
        
        # Calculate percentages
        least_pct = round(least / total * 100, 1)
        neutral_left_pct = round(neutral_left / total * 100, 1)
        neutral_right_pct = round(neutral_right / total * 100, 1)
        most_pct = round(most / total * 100, 1)
        
        processed_data.append({
            'question': question_labels[i],
            'least': least_pct,
            'neutral_left': neutral_left_pct,
            'neutral_right': neutral_right_pct,
            'most': most_pct,
            'left_total': least_pct + neutral_left_pct,
            'right_total': neutral_right_pct + most_pct
        })
    
    return processed_data

def create_likert_chart(data, output_file='likert_chart.png'):
    """Create a diverging stacked bar chart from the processed data."""
    
    # Set up the figure and axis
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Define colors to match the original chart
    colors = {
        'least': '#8B4513',        # Dark brown
        'neutral_left': '#D2B48C', # Light brown
        'neutral_right': '#20B2AA', # Light teal
        'most': '#008B8B'          # Dark teal
    }
    
    # Number of questions
    n_questions = len(data)
    y_positions = np.arange(n_questions)
    
    # Create the diverging bars
    for i, item in enumerate(data):
        y_pos = y_positions[i]
        
        # Calculate cumulative positions for stacking
        left_start = -item['least'] - item['neutral_left']
        neutral_left_start = -item['least']
        neutral_right_start = 0
        most_start = item['neutral_right']
        
        # Draw the bars
        # Least (dark brown) - left side
        if item['least'] > 0:
            ax.barh(y_pos, -item['least'], left=left_start, 
                   color=colors['least'], height=0.6, alpha=0.8)
            # Add percentage text
            ax.text(left_start + item['least']/2, y_pos, f'{item["least"]}%', 
                   ha='center', va='center', fontsize=9, fontweight='bold', color='white')
        
        # Neutral Left (light brown) - left side
        if item['neutral_left'] > 0:
            ax.barh(y_pos, -item['neutral_left'], left=neutral_left_start, 
                   color=colors['neutral_left'], height=0.6, alpha=0.8)
            ax.text(neutral_left_start - item['neutral_left']/2, y_pos, f'{item["neutral_left"]}%', 
                   ha='center', va='center', fontsize=9, fontweight='bold', color='black')
        
        # Neutral Right (light teal) - right side
        if item['neutral_right'] > 0:
            ax.barh(y_pos, item['neutral_right'], left=neutral_right_start, 
                   color=colors['neutral_right'], height=0.6, alpha=0.8)
            ax.text(neutral_right_start + item['neutral_right']/2, y_pos, f'{item["neutral_right"]}%', 
                   ha='center', va='center', fontsize=9, fontweight='bold', color='black')
        
        # Most (dark teal) - right side
        if item['most'] > 0:
            ax.barh(y_pos, item['most'], left=most_start, 
                   color=colors['most'], height=0.6, alpha=0.8)
            ax.text(most_start + item['most']/2, y_pos, f'{item["most"]}%', 
                   ha='center', va='center', fontsize=9, fontweight='bold', color='white')
        
        # Add left and right total labels
        ax.text(left_start - 2, y_pos, f'{item["left_total"]}%', 
               ha='right', va='center', fontsize=10, fontweight='bold')
        ax.text(most_start + item['most'] + 2, y_pos, f'{item["right_total"]}%', 
               ha='left', va='center', fontsize=10, fontweight='bold')
    
    # Customize the chart
    ax.set_yticks(y_positions)
    ax.set_yticklabels([item['question'] for item in data], fontsize=10)
    ax.set_xlim(-60, 60)
    ax.set_xlabel('Percentage (%)', fontsize=12, fontweight='bold')
    ax.set_title('Survey Responses - Likert Scale Analysis', fontsize=14, fontweight='bold', pad=20)
    
    # Add vertical line at 0
    ax.axvline(x=0, color='black', linewidth=0.8)
    
    # Add grid lines
    ax.grid(True, axis='x', alpha=0.3, linestyle='-', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # Create legend
    legend_elements = [
        mpatches.Patch(color=colors['least'], label='Least'),
        mpatches.Patch(color=colors['neutral_left'], label='Neutral'),
        mpatches.Patch(color=colors['neutral_right'], label='Neutral'),
        mpatches.Patch(color=colors['most'], label='Most')
    ]
    ax.legend(handles=legend_elements, loc='lower center', bbox_to_anchor=(0.5, -0.15), 
             ncol=4, fontsize=10)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Chart saved as {output_file}")
    
    # Show the plot
    plt.show()

def main():
    """Main function to run the script."""
    
    # File path to the Excel data
    data_file = '/home/asadr/works/repos/survey-ai-cwf/data/S2_Survey_Data.xlsx'
    output_file = '/home/asadr/works/repos/survey-ai-cwf/scripts/likert_chart.png'
    
    try:
        # Load and process the data
        print("Loading and processing survey data...")
        data = load_and_process_data(data_file)
        
        # Create the chart
        print("Creating diverging stacked bar chart...")
        create_likert_chart(data, output_file)
        
        print("Chart creation completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
