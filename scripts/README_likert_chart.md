# Likert Scale Diverging Bar Chart Generator

This script recreates a diverging stacked bar chart from survey data, specifically designed to visualize Likert scale responses from the S2_Survey_Data.xlsx file.

## Overview

The script analyzes 8 different survey questions related to AI in healthcare and creates a diverging stacked bar chart that shows the distribution of responses across 4 categories:
- **Least** (Dark Brown): Most negative responses
- **Neutral Left** (Light Brown): Slightly negative/neutral responses
- **Neutral Right** (Light Teal): Slightly positive/neutral responses  
- **Most** (Dark Teal): Most positive responses

## Files

- `create_likert_chart.py` - Main script to generate the chart
- `validate_chart_data.py` - Validation script to compare data with original chart
- `likert_chart.png` - Generated chart output

## Survey Questions Analyzed

1. **AI Familiarity** (`ai_familiar.q10`)
2. **Willingness to Use AI** (`ai_willing_to_use.q12`)
3. **General Opinion of AI** (`ai_use_gen_opinion.q13`)
4. **AI Improves Healthcare Practices** (`ai_improve_healthcare_practices.q14`)
5. **AI Improves Health Outcomes** (`ai_improve_health_outcomes.q15`)
6. **AI Required Likelihood** (`ai_required_likelihood.q16`)
7. **AI Knowledge Level** (`ai_knowledge.q17`)
8. **AI Use Confidence** (`ai_use_confidence.q19`)

## Data Processing

The script processes 5-point Likert scale responses and collapses them into 4 categories:

### AI Familiarity
- Least: "Not at all familiar"
- Neutral Left: "Slightly familiar"
- Neutral Right: "Moderately familiar"
- Most: "Very familiar" + "Extremely familiar"

### Willingness to Use AI
- Least: "Not at all willing"
- Neutral Left: "Slightly willing"
- Neutral Right: "Moderately willing"
- Most: "Very willing" + "Extremely willing"

### General Opinion of AI
- Least: "Very unfavorable"
- Neutral Left: "Unfavorable"
- Neutral Right: "Neither favorable nor unfavorable"
- Most: "Favorable" + "Very favorable"

### AI Improves Healthcare Practices/Health Outcomes
- Least: "Not at all important"
- Neutral Left: "Somewhat important"
- Neutral Right: "Important"
- Most: "Very important" + "Extremely important"

### AI Required Likelihood
- Least: "Extremely unlikely"
- Neutral Left: "Unlikely"
- Neutral Right: "Likely"
- Most: "Extremely likely"

### AI Knowledge Level
- Least: "Very low"
- Neutral Left: "Low"
- Neutral Right: "Moderate"
- Most: "High" + "Very high"

### AI Use Confidence
- Least: "Not at all confident"
- Neutral Left: "Slightly confident"
- Neutral Right: "Moderately confident"
- Most: "Very confident" + "Extremely confident"

## Usage

```bash
# Generate the chart
python create_likert_chart.py

# Validate data against original chart
python validate_chart_data.py
```

## Dependencies

- pandas
- matplotlib
- numpy

## Output

The script generates a high-resolution PNG file (`likert_chart.png`) with:
- 8 horizontal bars representing each survey question
- Diverging stacked bars showing response distributions
- Percentage labels within each segment
- Left and right total percentages
- Color-coded legend
- Professional styling matching the original chart design

## Data Validation

The validation script compares the generated data with the original chart data from the image description. Note that there are some differences, which may be due to:
- Different data subsets or filtering
- Different time periods
- Different analysis methods
- Data preprocessing differences

The generated chart represents the actual survey responses from the Excel file.
