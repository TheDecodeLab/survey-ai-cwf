#!/usr/bin/env python3
"""
Figure 19: Specialty-Specific AI Applications - Chord Diagram
Circular chord diagram showing which AI benefits are most relevant to which medical specialties,
with chord thickness representing strength of association.

To run: conda activate eda && python fig19.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import seaborn as sns

def create_chord_diagram():
    """Create chord diagram showing specialty-specific AI applications"""
    
    # Read the survey data
    df = pd.read_excel('../data/S2_Survey_Data.xlsx', sheet_name='Sheet 1')
    
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
    
    # Get top specialties with sufficient data
    specialty_counts = df['specialty_category'].value_counts()
    top_specialties = specialty_counts[specialty_counts >= 8].index.tolist()
    top_specialties = [spec for spec in top_specialties if spec != 'Other/Unknown']
    
    # Define main AI benefits
    main_benefits = [
        'Improved efficiency in healthcare documentation work',
        'Increased efficiency in healthcare delivery',
        'Improved diagnostic accuracy',
        'Improved medical training or simulations',
        'Enhanced patient outcomes',
        'Enabling personalized medicine',
        'Improved patient experience and engagement',
        'Enhanced surgical training planning'
    ]
    
    # Calculate benefit-specialty associations
    benefit_specialty_matrix = {}
    
    for specialty in top_specialties:
        spec_data = df[df['specialty_category'] == specialty]
        benefits_data = spec_data['ai_benefits.q31'].dropna()
        
        if len(benefits_data) > 0:
            all_benefits = []
            for response in benefits_data:
                benefits = [benefit.strip() for benefit in str(response).split(',')]
                all_benefits.extend(benefits)
            
            benefit_counts = Counter(all_benefits)
            specialty_benefits = {}
            
            for benefit in main_benefits:
                count = benefit_counts.get(benefit, 0)
                percentage = (count / len(benefits_data)) * 100
                specialty_benefits[benefit] = percentage
            
            benefit_specialty_matrix[specialty] = specialty_benefits
    
    # Create the chord diagram
    fig, ax = plt.subplots(figsize=(16, 16))
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_aspect('equal')
    
    # Define positions for specialties and benefits in a circle
    n_specialties = len(top_specialties)
    n_benefits = len(main_benefits)
    
    # Calculate angles for specialties (outer circle)
    specialty_angles = np.linspace(0, 2*np.pi, n_specialties, endpoint=False)
    specialty_radius = 1.0
    
    # Calculate angles for benefits (inner circle)
    benefit_angles = np.linspace(0, 2*np.pi, n_benefits, endpoint=False)
    benefit_radius = 0.6
    
    # Define colors
    specialty_colors = plt.cm.Set3(np.linspace(0, 1, n_specialties))
    benefit_colors = plt.cm.Pastel1(np.linspace(0, 1, n_benefits))
    
    # Draw specialty nodes (outer circle)
    specialty_positions = {}
    for i, (specialty, angle) in enumerate(zip(top_specialties, specialty_angles)):
        x = specialty_radius * np.cos(angle)
        y = specialty_radius * np.sin(angle)
        specialty_positions[specialty] = (x, y, angle)
        
        # Draw specialty node
        circle = plt.Circle((x, y), 0.08, color=specialty_colors[i], alpha=0.8, 
                           edgecolor='black', linewidth=1)
        ax.add_patch(circle)
        
        # Add specialty label
        label_x = 1.15 * np.cos(angle)
        label_y = 1.15 * np.sin(angle)
        ax.text(label_x, label_y, specialty, ha='center', va='center', 
                fontsize=10, fontweight='bold', rotation=0)
    
    # Draw benefit nodes (inner circle)
    benefit_positions = {}
    for i, (benefit, angle) in enumerate(zip(main_benefits, benefit_angles)):
        x = benefit_radius * np.cos(angle)
        y = benefit_radius * np.sin(angle)
        benefit_positions[benefit] = (x, y, angle)
        
        # Draw benefit node
        circle = plt.Circle((x, y), 0.06, color=benefit_colors[i], alpha=0.8, 
                           edgecolor='black', linewidth=1)
        ax.add_patch(circle)
        
        # Add benefit label (shortened)
        short_benefit = benefit.replace('Improved ', '').replace('Increased ', '').replace('Enhanced ', '')
        short_benefit = short_benefit.replace(' in healthcare', '').replace(' healthcare', '')
        if len(short_benefit) > 20:
            short_benefit = short_benefit[:17] + '...'
        
        label_x = 0.45 * np.cos(angle)
        label_y = 0.45 * np.sin(angle)
        ax.text(label_x, label_y, short_benefit, ha='center', va='center', 
                fontsize=8, fontweight='bold', rotation=0)
    
    # Draw chords between specialties and benefits
    chord_data = []
    
    for specialty in top_specialties:
        if specialty in benefit_specialty_matrix:
            specialty_x, specialty_y, specialty_angle = specialty_positions[specialty]
            
            for benefit in main_benefits:
                if benefit in benefit_specialty_matrix[specialty]:
                    percentage = benefit_specialty_matrix[specialty][benefit]
                    
                    if percentage > 5:  # Only draw chords for significant associations
                        benefit_x, benefit_y, benefit_angle = benefit_positions[benefit]
                        
                        # Calculate chord thickness based on percentage
                        thickness = max(0.5, percentage / 10)
                        
                        # Draw chord as a curved line
                        t = np.linspace(0, 1, 100)
                        
                        # Control points for the curve
                        mid_x = (specialty_x + benefit_x) / 2
                        mid_y = (specialty_y + benefit_y) / 2
                        
                        # Add some curvature
                        control_x = mid_x + 0.3 * np.cos((specialty_angle + benefit_angle) / 2)
                        control_y = mid_y + 0.3 * np.sin((specialty_angle + benefit_angle) / 2)
                        
                        # Bezier curve
                        curve_x = (1-t)**2 * specialty_x + 2*(1-t)*t * control_x + t**2 * benefit_x
                        curve_y = (1-t)**2 * specialty_y + 2*(1-t)*t * control_y + t**2 * benefit_y
                        
                        # Draw the chord
                        ax.plot(curve_x, curve_y, linewidth=thickness, alpha=0.6, 
                               color=specialty_colors[top_specialties.index(specialty)])
                        
                        chord_data.append((specialty, benefit, percentage))
    
    # Add title
    plt.title('Specialty-Specific AI Applications\nChord Diagram of Benefit-Specialty Associations', 
              fontsize=16, fontweight='bold', pad=20)
    
    # Add legend for specialties
    specialty_legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                                           markerfacecolor=specialty_colors[i], 
                                           markersize=10, label=specialty) 
                                for i, specialty in enumerate(top_specialties)]
    
    legend1 = ax.legend(handles=specialty_legend_elements, loc='upper left', 
                       bbox_to_anchor=(0, 1), title='Medical Specialties', fontsize=10)
    ax.add_artist(legend1)
    
    # Add legend for benefits
    benefit_legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                                         markerfacecolor=benefit_colors[i], 
                                         markersize=8, label=benefit.replace('Improved ', '').replace('Increased ', '').replace('Enhanced ', '')) 
                              for i, benefit in enumerate(main_benefits)]
    
    legend2 = ax.legend(handles=benefit_legend_elements, loc='upper right', 
                       bbox_to_anchor=(1, 1), title='AI Benefits', fontsize=9)
    
    # Add statistics
    stats_text = f"""
    Chord Diagram Statistics:
    • Specialties: {n_specialties}
    • AI Benefits: {n_benefits}
    • Significant Associations: {len(chord_data)}
    • Average Association Strength: {np.mean([data[2] for data in chord_data]):.1f}%
    """
    
    ax.text(-1.1, -1.1, stats_text, fontsize=10, va='bottom', ha='left',
            bbox=dict(boxstyle="round,pad=0.5", facecolor='lightblue', alpha=0.8))
    
    # Remove axes
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    plt.tight_layout()
    
    # Save the figure
    plt.savefig('fig19_chord_specialty_applications.png', dpi=300, bbox_inches='tight')
    plt.savefig('fig19_chord_specialty_applications.pdf', bbox_inches='tight')
    
    # Show the figure
    plt.show()
    
    # Print detailed analysis
    print("Specialty-Specific AI Applications - Chord Diagram Analysis:")
    print("=" * 70)
    
    print(f"\nSpecialty-Benefit Association Matrix:")
    print(f"{'Specialty':<20} {'Benefit':<40} {'Association %':<15}")
    print("-" * 75)
    
    for specialty in top_specialties:
        if specialty in benefit_specialty_matrix:
            print(f"\n{specialty}:")
            specialty_benefits = benefit_specialty_matrix[specialty]
            sorted_benefits = sorted(specialty_benefits.items(), key=lambda x: x[1], reverse=True)
            
            for benefit, percentage in sorted_benefits:
                if percentage > 5:  # Only show significant associations
                    short_benefit = benefit.replace('Improved ', '').replace('Increased ', '').replace('Enhanced ', '')
                    if len(short_benefit) > 35:
                        short_benefit = short_benefit[:32] + '...'
                    print(f"{'':<20} {short_benefit:<40} {percentage:.1f}%")
    
    # Find strongest associations
    print(f"\nStrongest Specialty-Benefit Associations:")
    sorted_chords = sorted(chord_data, key=lambda x: x[2], reverse=True)
    for i, (specialty, benefit, percentage) in enumerate(sorted_chords[:10]):
        short_benefit = benefit.replace('Improved ', '').replace('Increased ', '').replace('Enhanced ', '')
        if len(short_benefit) > 30:
            short_benefit = short_benefit[:27] + '...'
        print(f"{i+1:2d}. {specialty} ↔ {short_benefit}: {percentage:.1f}%")
    
    # Calculate specialty AI focus
    print(f"\nSpecialty AI Focus Analysis:")
    for specialty in top_specialties:
        if specialty in benefit_specialty_matrix:
            specialty_benefits = benefit_specialty_matrix[specialty]
            avg_association = np.mean(list(specialty_benefits.values()))
            max_association = max(specialty_benefits.values())
            top_benefit = max(specialty_benefits, key=specialty_benefits.get)
            
            print(f"{specialty}:")
            print(f"  Average association: {avg_association:.1f}%")
            print(f"  Top benefit: {top_benefit.replace('Improved ', '').replace('Increased ', '').replace('Enhanced ', '')} ({max_association:.1f}%)")

if __name__ == "__main__":
    create_chord_diagram()
