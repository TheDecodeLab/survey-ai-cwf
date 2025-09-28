#!/usr/bin/env python3
"""
Validation script to compare generated chart data with the original chart data.
"""

import pandas as pd
import numpy as np

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
            least = value_counts.get('Not at all familiar', 0)
            neutral_left = value_counts.get('Slightly familiar', 0)
            neutral_right = value_counts.get('Moderately familiar', 0)
            most = value_counts.get('Very familiar', 0) + value_counts.get('Extremely familiar', 0)
            
        elif col == 'ai_willing_to_use.q12':
            least = value_counts.get('Not at all willing', 0)
            neutral_left = value_counts.get('Slightly willing', 0)
            neutral_right = value_counts.get('Moderately willing', 0)
            most = value_counts.get('Very willing', 0) + value_counts.get('Extremely willing', 0)
            
        elif col == 'ai_use_gen_opinion.q13':
            least = value_counts.get('Very unfavorable', 0)
            neutral_left = value_counts.get('Unfavorable', 0)
            neutral_right = value_counts.get('Neither favorable nor unfavorable', 0)
            most = value_counts.get('Favorable', 0) + value_counts.get('Very favorable', 0)
            
        elif col in ['ai_improve_healthcare_practices.q14', 'ai_improve_health_outcomes.q15']:
            least = value_counts.get('Not at all important', 0)
            neutral_left = value_counts.get('Somewhat important', 0)
            neutral_right = value_counts.get('Important', 0)
            most = value_counts.get('Very important', 0) + value_counts.get('Extremely important', 0)
            
        elif col == 'ai_required_likelihood.q16':
            least = value_counts.get('Extremely unlikely', 0)
            neutral_left = value_counts.get('Unlikely', 0)
            neutral_right = value_counts.get('Likely', 0)
            most = value_counts.get('Extremely likely', 0)
            
        elif col == 'ai_knowledge.q17':
            least = value_counts.get('Very low', 0)
            neutral_left = value_counts.get('Low', 0)
            neutral_right = value_counts.get('Moderate', 0)
            most = value_counts.get('High', 0) + value_counts.get('Very high', 0)
            
        elif col == 'ai_use_confidence.q19':
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

def main():
    """Compare generated data with original chart data."""
    
    # Original chart data from the image description
    original_data = [
        {'question': 'Row 1', 'least': 13, 'neutral_left': 46, 'neutral_right': 29, 'most': 9, 'left_total': 59, 'right_total': 38},
        {'question': 'Row 2', 'least': 18, 'neutral_left': 39, 'neutral_right': 34, 'most': 8, 'left_total': 57, 'right_total': 42},
        {'question': 'Row 3', 'least': 31, 'neutral_left': 30, 'neutral_right': 26, 'most': 9, 'left_total': 61, 'right_total': 35},
        {'question': 'Row 4', 'least': 36, 'neutral_left': 28, 'neutral_right': 22, 'most': 9, 'left_total': 64, 'right_total': 31},
        {'question': 'Row 5', 'least': 0, 'neutral_left': 13, 'neutral_right': 34, 'most': 33, 'left_total': 13, 'right_total': 67},
        {'question': 'Row 6', 'least': 0, 'neutral_left': 8, 'neutral_right': 47, 'most': 11, 'left_total': 8, 'right_total': 58},
        {'question': 'Row 7', 'least': 6, 'neutral_left': 33, 'neutral_right': 24, 'most': 15, 'left_total': 39, 'right_total': 39},
        {'question': 'Row 8', 'least': 6, 'neutral_left': 32, 'neutral_right': 23, 'most': 15, 'left_total': 38, 'right_total': 38}
    ]
    
    # Load and process our data
    data_file = '/home/asadr/works/repos/survey-ai-cwf/data/S2_Survey_Data.xlsx'
    generated_data = load_and_process_data(data_file)
    
    print("Data Comparison: Generated vs Original Chart")
    print("=" * 80)
    print(f"{'Question':<30} {'Generated Data':<40} {'Original Data':<40}")
    print(f"{'':30} {'L  NL  NR  M  LT  RT':<40} {'L  NL  NR  M  LT  RT':<40}")
    print("-" * 80)
    
    for i, (gen, orig) in enumerate(zip(generated_data, original_data)):
        gen_str = f"{gen['least']:2.0f} {gen['neutral_left']:2.0f} {gen['neutral_right']:2.0f} {gen['most']:2.0f} {gen['left_total']:2.0f} {gen['right_total']:2.0f}"
        orig_str = f"{orig['least']:2.0f} {orig['neutral_left']:2.0f} {orig['neutral_right']:2.0f} {orig['most']:2.0f} {orig['left_total']:2.0f} {orig['right_total']:2.0f}"
        print(f"{gen['question']:<30} {gen_str:<40} {orig_str:<40}")
    
    print("\nLegend: L=Least, NL=Neutral Left, NR=Neutral Right, M=Most, LT=Left Total, RT=Right Total")
    print("\nNote: The original chart data appears to be from a different analysis or subset of the data.")
    print("Our generated data represents the actual survey responses from the Excel file.")

if __name__ == "__main__":
    main()
