#!/usr/bin/env python3
"""
Create a Sankey diagram for survey data with 3 layers:
1. Training (No, Unsure, Yes) - No at top, Yes at bottom
2. Confidence to use AI tools (No -> Extremely confident) - No at top, Extremely confident at bottom
3. Confidence to discuss AI tools (No -> Extremely confident) - No at top, Extremely confident at bottom
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# =============================================================================
# CONFIGURATION - Modify these settings to change layer order and labels
# =============================================================================

# Layer 1: Training order (from top to bottom)
TRAINING_ORDER = ['No', 'Unsure', 'Yes']

# Layer 2: Confidence to use AI tools order (from top to bottom)
USE_CONFIDENCE_ORDER = ['No', 'Slightly confident', 'Moderately confident', 
                        'Very confident', 'Extremely confident']

# Layer 3: Confidence to discuss AI tools order (from top to bottom)
DISCUSS_CONFIDENCE_ORDER = ['No', 'Slightly confident', 'Moderately confident', 
                            'Very confident', 'Extremely confident']

# Layer labels (what appears in the diagram)
LAYER_LABELS = {
    'training': 'Training',
    'use_confidence': 'Confidence to use AI tools', 
    'discuss_confidence': 'Confidence to discuss AI tools'
}

# Node labels (what appears for each category)
NODE_LABELS = {
    'training': {
        'No': 'No',
        'Unsure': 'Unsure', 
        'Yes': 'Yes'
    },
    'use_confidence': {
        'No': 'No',
        'Slightly confident': 'Slightly confident',
        'Moderately confident': 'Moderately confident',
        'Very confident': 'Very confident',
        'Extremely confident': 'Extremely confident'
    },
    'discuss_confidence': {
        'No': 'No',
        'Slightly confident': 'Slightly',
        'Moderately confident': 'Moderately',
        'Very confident': 'Very',
        'Extremely confident': 'Extremely'
    }
}

# Color schemes for each layer
COLORS = {
    'training': ['#8B5A96', '#4A90E2', '#50C878'],  # Purple, Blue, Green
    'confidence': ['#8B5A96', '#4A90E2', '#50C878', '#F4A460', '#FFD700']  # Purple to Gold
}

# Link transparency (0.0 = fully transparent, 1.0 = fully opaque)
LINK_TRANSPARENCY = 0.3

# Figure size (width, height) in pixels
FIG_SIZE = (750, 450)

# Data cleaning mappings
DATA_MAPPINGS = {
    'training': {
        'Yes, but very limited': 'Unsure',  # Map this to Unsure
        'nan': 'No'  # Treat missing as No
    },
    'confidence': {
        'Not at all confident': 'No',  # Replace with No for simplicity
        'nan': 'No'  # Treat missing as No
    }
}

def load_and_examine_data():
    """Load the survey data and examine the structure"""
    print("Loading survey data...")
    df = pd.read_excel('/home/asadr/works/repos/survey-ai-cwf/data/S2_Survey_Data.xlsx')
    
    print(f"Data shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print("\nFirst few rows:")
    print(df.head())
    
    return df

def find_relevant_columns(df):
    """Find columns related to training and confidence"""
    print("\nSearching for relevant columns...")
    
    # Look for training-related columns
    training_cols = [col for col in df.columns if 'train' in col.lower()]
    print(f"Training columns: {training_cols}")
    
    # Look for confidence-related columns
    confidence_cols = [col for col in df.columns if 'confid' in col.lower()]
    print(f"Confidence columns: {confidence_cols}")
    
    # Look for AI-related columns
    ai_cols = [col for col in df.columns if 'ai' in col.lower()]
    print(f"AI-related columns: {ai_cols}")
    
    return training_cols, confidence_cols, ai_cols

def print_value_counts(df, columns):
    """Print value counts for specified columns"""
    for col in columns:
        if col in df.columns:
            print(f"\nValue counts for '{col}':")
            print(df[col].value_counts(dropna=False))
            print(f"Missing values: {df[col].isnull().sum()}")

def clean_data(df, training_col, use_confidence_col, discuss_confidence_col):
    """Clean the data according to configuration mappings"""
    df_clean = df.copy()
    
    # Clean training data
    df_clean[training_col] = df_clean[training_col].astype(str).str.strip()
    for old_val, new_val in DATA_MAPPINGS['training'].items():
        df_clean[training_col] = df_clean[training_col].str.replace(old_val, new_val)
    
    # Clean confidence data
    for col in [use_confidence_col, discuss_confidence_col]:
        df_clean[col] = df_clean[col].astype(str).str.strip()
        for old_val, new_val in DATA_MAPPINGS['confidence'].items():
            df_clean[col] = df_clean[col].str.replace(old_val, new_val)
    
    # Remove rows with missing values (after cleaning)
    df_clean = df_clean[df_clean[training_col] != 'nan']
    df_clean = df_clean[df_clean[use_confidence_col] != 'nan']
    df_clean = df_clean[df_clean[discuss_confidence_col] != 'nan']
    
    return df_clean

def create_sankey_diagram(df, training_col, use_confidence_col, discuss_confidence_col):
    """Create the Sankey diagram using configuration settings"""
    
    # Clean and prepare the data
    df_clean = clean_data(df, training_col, use_confidence_col, discuss_confidence_col)
    
    print(f"\nData after cleaning: {len(df_clean)} rows")
    
    # Print value counts for each layer
    print("\n" + "="*50)
    print("VALUE COUNTS FOR EACH LAYER")
    print("="*50)
    
    print(f"\nLayer 1 - {LAYER_LABELS['training']} ({training_col}):")
    training_counts = df_clean[training_col].value_counts()
    print(training_counts)
    
    print(f"\nLayer 2 - {LAYER_LABELS['use_confidence']} ({use_confidence_col}):")
    use_counts = df_clean[use_confidence_col].value_counts()
    print(use_counts)
    
    print(f"\nLayer 3 - {LAYER_LABELS['discuss_confidence']} ({discuss_confidence_col}):")
    discuss_counts = df_clean[discuss_confidence_col].value_counts()
    print(discuss_counts)
    
    # Create source, target, and value arrays
    sources = []
    targets = []
    values = []
    labels = []
    
    # Create label mapping
    label_to_index = {}
    current_index = 0
    
    # Add training labels (just the node labels, no layer prefix)
    for label in TRAINING_ORDER:
        if label in training_counts.index:
            label_to_index[f"Training_{label}"] = current_index
            labels.append(NODE_LABELS['training'][label])
            current_index += 1
    
    # Add use confidence labels (empty for middle layer - no labels)
    for label in USE_CONFIDENCE_ORDER:
        if label in use_counts.index:
            label_to_index[f"Use_{label}"] = current_index
            labels.append("")  # Empty label for middle layer
            current_index += 1
    
    # Add discuss confidence labels (just the node labels, no layer prefix)
    for label in DISCUSS_CONFIDENCE_ORDER:
        if label in discuss_counts.index:
            label_to_index[f"Discuss_{label}"] = current_index
            labels.append(NODE_LABELS['discuss_confidence'][label])
            current_index += 1
    
    # Create flows from training to use confidence
    link_colors = []
    for train_val in TRAINING_ORDER:
        if train_val in training_counts.index:
            # Get the color for this training value
            train_color_idx = TRAINING_ORDER.index(train_val)
            train_color = COLORS['training'][train_color_idx]
            # Convert to RGBA with transparency
            train_color_rgba = f"rgba({int(train_color[1:3], 16)}, {int(train_color[3:5], 16)}, {int(train_color[5:7], 16)}, {LINK_TRANSPARENCY})"
            
            for conf_val in USE_CONFIDENCE_ORDER:
                if conf_val in use_counts.index:
                    count = len(df_clean[(df_clean[training_col] == train_val) & 
                                       (df_clean[use_confidence_col] == conf_val)])
                    if count > 0:
                        sources.append(label_to_index[f"Training_{train_val}"])
                        targets.append(label_to_index[f"Use_{conf_val}"])
                        values.append(count)
                        link_colors.append(train_color_rgba)
    
    # Create flows from use confidence to discuss confidence
    for use_val in USE_CONFIDENCE_ORDER:
        if use_val in use_counts.index:
            # Get the color for this confidence value
            conf_color_idx = USE_CONFIDENCE_ORDER.index(use_val)
            conf_color = COLORS['confidence'][conf_color_idx]
            # Convert to RGBA with transparency
            conf_color_rgba = f"rgba({int(conf_color[1:3], 16)}, {int(conf_color[3:5], 16)}, {int(conf_color[5:7], 16)}, {LINK_TRANSPARENCY})"
            
            for discuss_val in DISCUSS_CONFIDENCE_ORDER:
                if discuss_val in discuss_counts.index:
                    count = len(df_clean[(df_clean[use_confidence_col] == use_val) & 
                                       (df_clean[discuss_confidence_col] == discuss_val)])
                    if count > 0:
                        sources.append(label_to_index[f"Use_{use_val}"])
                        targets.append(label_to_index[f"Discuss_{discuss_val}"])
                        values.append(count)
                        link_colors.append(conf_color_rgba)
    
    # Create color array for nodes
    node_colors = []
    
    # Count nodes in each layer to determine which layer we're in
    training_node_count = len([l for l in TRAINING_ORDER if l in training_counts.index])
    use_confidence_node_count = len([l for l in USE_CONFIDENCE_ORDER if l in use_counts.index])
    
    for i, label in enumerate(labels):
        if i < training_node_count:
            # Training layer
            for j, train_val in enumerate(TRAINING_ORDER):
                if train_val in training_counts.index and NODE_LABELS['training'][train_val] == label:
                    node_colors.append(COLORS['training'][j])
                    break
        elif i < training_node_count + use_confidence_node_count:
            # Use confidence layer - use index to determine color since labels are empty
            layer_index = i - training_node_count
            for j, conf_val in enumerate(USE_CONFIDENCE_ORDER):
                if conf_val in use_counts.index and j == layer_index:
                    node_colors.append(COLORS['confidence'][j])
                    break
        else:  # Discuss confidence layer
            for j, conf_val in enumerate(DISCUSS_CONFIDENCE_ORDER):
                if conf_val in discuss_counts.index and NODE_LABELS['discuss_confidence'][conf_val] == label:
                    node_colors.append(COLORS['confidence'][j])
                    break
    
    # Create the Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=node_colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors
        )
    )])
    
    # Calculate positions for layer titles based on actual node distribution
    # Fine-tuned positions to align with the center of each layer
    training_center = 0.02  # Left layer - moved slightly left
    use_confidence_center = 0.5  # Middle layer - seems correctly centered
    discuss_confidence_center = 0.88  # Right layer - moved slightly right
    
    # Create annotations for layer titles
    annotations = []
    layer_centers = [training_center, use_confidence_center, discuss_confidence_center]
    
    for i, (layer_key, layer_title) in enumerate(LAYER_LABELS.items()):
        annotations.append(
            dict(
                x=layer_centers[i],
                y=-0.12,  # Below the diagram
                xref='paper',
                yref='paper',
                text=f"<b>{layer_title}</b>",
                showarrow=False,
                font=dict(size=14, color='black'),
                xanchor='center'
            )
        )
    
    fig.update_layout(
        title_text= '', #f"Survey Data: {LAYER_LABELS['training']} → {LAYER_LABELS['use_confidence']} → {LAYER_LABELS['discuss_confidence']}",
        font=dict(size=12, color="black"),
        width=FIG_SIZE[0],
        height=FIG_SIZE[1],
        annotations=annotations,
        margin=dict(b=80)  # Add bottom margin for layer titles
    )
    
    return fig

def main():
    """Main function"""
    print("Creating Sankey diagram for survey data...")
    print(f"Configuration:")
    print(f"  Training order: {TRAINING_ORDER}")
    print(f"  Use confidence order: {USE_CONFIDENCE_ORDER}")
    print(f"  Discuss confidence order: {DISCUSS_CONFIDENCE_ORDER}")
    print(f"  Layer labels: {LAYER_LABELS}")
    print(f"  Figure size: {FIG_SIZE[0]}x{FIG_SIZE[1]} pixels")
    print(f"  Link transparency: {LINK_TRANSPARENCY}")
    
    # Load data
    df = load_and_examine_data()
    
    # Find relevant columns
    training_cols, confidence_cols, ai_cols = find_relevant_columns(df)
    
    # Print all columns to help identify the right ones
    print(f"\nAll columns in the dataset:")
    for i, col in enumerate(df.columns):
        print(f"{i}: {col}")
    
    # Try to identify the correct columns automatically
    training_col = None
    use_confidence_col = None
    discuss_confidence_col = None
    
    # Look for training column
    for col in training_cols:
        if 'train' in col.lower():
            training_col = col
            break
    
    # Look for confidence columns
    for col in confidence_cols:
        if 'use' in col.lower() or 'using' in col.lower():
            use_confidence_col = col
        elif 'discuss' in col.lower() or 'discussion' in col.lower():
            discuss_confidence_col = col
    
    # If not found automatically, we'll need to specify manually
    if not all([training_col, use_confidence_col, discuss_confidence_col]):
        print(f"\nCould not automatically identify all required columns.")
        print(f"Found: Training={training_col}, Use Confidence={use_confidence_col}, Discuss Confidence={discuss_confidence_col}")
        print("Please check the column names and update the script if needed.")
        return
    
    print(f"\nUsing columns:")
    print(f"Training: {training_col}")
    print(f"Use AI Confidence: {use_confidence_col}")
    print(f"Discuss AI Confidence: {discuss_confidence_col}")
    
    # Print value counts for the selected columns
    print_value_counts(df, [training_col, use_confidence_col, discuss_confidence_col])
    
    # Create and save the Sankey diagram
    fig = create_sankey_diagram(df, training_col, use_confidence_col, discuss_confidence_col)
    
    # JavaScript to make labels bold with black stroke
    js_code = """
    function makeLabelsBold() {
        const labels = document.querySelectorAll('.sankey-node .node-label');
        labels.forEach(label => {
            label.style.fontWeight = 'bold';
            label.style.stroke = 'black';
            label.style.strokeWidth = '0.5px';
            label.style.paintOrder = 'stroke fill';
        });
    }
    
    // Apply after plot is rendered
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', makeLabelsBold);
    } else {
        makeLabelsBold();
    }
    
    // Also apply on plot updates
    const plotDiv = document.getElementById('{plot_id}');
    if (plotDiv) {
        plotDiv.on('plotly_afterplot', makeLabelsBold);
    }
    """
    
    # Save the figure with JavaScript
    output_file = '/home/asadr/works/repos/survey-ai-cwf/fig6_sankey.html'
    fig.write_html(output_file, post_script=[js_code])
    print(f"\nSankey diagram saved to: {output_file}")
    
    # Also save as PNG
    png_file = '/home/asadr/works/repos/survey-ai-cwf/fig6_sankey.png'
    fig.write_image(png_file, width=FIG_SIZE[0], height=FIG_SIZE[1])
    print(f"Sankey diagram saved as PNG to: {png_file}")

    # Also save as SVG
    svg_file = '/home/asadr/works/repos/survey-ai-cwf/fig6_sankey.svg'
    fig.write_image(svg_file, width=FIG_SIZE[0], height=FIG_SIZE[1])
    print(f"Sankey diagram saved as SVG to: {svg_file}")

if __name__ == "__main__":
    main()