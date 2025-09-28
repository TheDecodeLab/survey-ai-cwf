#!/usr/bin/env python3
"""
Figure 15: AI Tool Ecosystem - Network Diagram
Interactive network showing connections between different AI tools mentioned,
with node sizes representing usage frequency and connections showing co-usage patterns.

To run: conda activate eda && python fig15.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
from collections import Counter, defaultdict
import re

def create_ai_tool_network():
    """Create network diagram of AI tool ecosystem"""
    
    # Read the survey data
    df = pd.read_excel('../data/S2_Survey_Data.xlsx', sheet_name='Sheet 1')
    
    # Get AI tool usage data
    ai_tools_data = df['curr_use_which_ai_tools.q38'].dropna()
    
    # Clean and standardize tool names
    def clean_tool_name(tool):
        tool = str(tool).strip().lower()
        # Standardize common variations
        if 'chatgpt' in tool or 'chat gpt' in tool or 'chat-gpt' in tool:
            return 'ChatGPT'
        elif 'viz' in tool and 'ai' in tool:
            return 'Viz.ai'
        elif 'dax' in tool or 'copilot' in tool:
            return 'DAX Copilot'
        elif 'cad' in tool:
            return 'CAD (Computer Aided Detection)'
        elif 'siemens' in tool:
            return 'Siemens AI-Rad'
        elif 'muse' in tool:
            return 'MUSE EKG'
        elif 'grammarly' in tool:
            return 'Grammarly'
        elif 'microsoft' in tool or 'azure' in tool:
            return 'Microsoft Azure'
        elif 'google' in tool or 'palm' in tool:
            return 'Google/PaLM'
        elif 'matlab' in tool:
            return 'MATLAB'
        elif 'robotics' in tool:
            return 'Robotics'
        elif 'ffr-ct' in tool or 'heartflow' in tool:
            return 'FFR-CT (HeartFlow)'
        elif 'hologic' in tool:
            return 'Hologic Image Analysis'
        elif 'rapid' in tool:
            return 'Rapid'
        elif 'freed' in tool:
            return 'Freed'
        elif 'doximity' in tool:
            return 'Doximity'
        else:
            return tool.title()
    
    # Extract and clean tools from each response
    tool_networks = []
    tool_frequencies = Counter()
    
    for response in ai_tools_data:
        # Split by common delimiters
        tools = re.split(r'[,;]', str(response))
        tools = [clean_tool_name(tool) for tool in tools if len(tool.strip()) > 2]
        
        # Filter out non-AI tools and clean up
        ai_tools = []
        for tool in tools:
            if any(keyword in tool.lower() for keyword in ['ai', 'chat', 'gpt', 'viz', 'dax', 'cad', 'siemens', 'muse', 'grammarly', 'microsoft', 'google', 'matlab', 'robotics', 'heartflow', 'hologic', 'rapid', 'freed', 'doximity']):
                ai_tools.append(tool)
                tool_frequencies[tool] += 1
        
        if len(ai_tools) > 1:  # Only include responses with multiple tools
            tool_networks.append(ai_tools)
    
    # Create co-occurrence matrix
    co_occurrence = defaultdict(int)
    for tool_list in tool_networks:
        for i, tool1 in enumerate(tool_list):
            for tool2 in tool_list[i+1:]:
                pair = tuple(sorted([tool1, tool2]))
                co_occurrence[pair] += 1
    
    # Create network graph
    G = nx.Graph()
    
    # Add nodes with frequency as weight
    for tool, freq in tool_frequencies.items():
        if freq >= 1:  # Include tools mentioned at least once
            G.add_node(tool, weight=freq)
    
    # Add edges with co-occurrence as weight
    for (tool1, tool2), co_freq in co_occurrence.items():
        if tool1 in G.nodes and tool2 in G.nodes and co_freq >= 1:
            G.add_edge(tool1, tool2, weight=co_freq)
    
    # Create the visualization
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Calculate layout
    pos = nx.spring_layout(G, k=3, iterations=50)
    
    # Draw the network
    # Node sizes based on frequency
    node_sizes = [G.nodes[node]['weight'] * 200 for node in G.nodes()]
    
    # Node colors based on tool category
    def get_tool_category(tool):
        tool_lower = tool.lower()
        if 'chatgpt' in tool_lower or 'gpt' in tool_lower:
            return '#FF6B6B'  # Red - General AI
        elif 'viz' in tool_lower or 'cad' in tool_lower or 'siemens' in tool_lower or 'hologic' in tool_lower:
            return '#4ECDC4'  # Teal - Medical Imaging
        elif 'dax' in tool_lower or 'copilot' in tool_lower:
            return '#45B7D1'  # Blue - Documentation
        elif 'muse' in tool_lower or 'ffr-ct' in tool_lower or 'heartflow' in tool_lower:
            return '#96CEB4'  # Green - Clinical Decision Support
        elif 'grammarly' in tool_lower or 'microsoft' in tool_lower or 'google' in tool_lower:
            return '#FFEAA7'  # Yellow - Productivity
        else:
            return '#DDA0DD'  # Purple - Other
    
    node_colors = [get_tool_category(node) for node in G.nodes()]
    
    # Draw nodes with better sizing
    min_size = 100
    max_size = 2000
    node_sizes = [max(min_size, min(max_size, G.nodes[node]['weight'] * 100)) for node in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, 
                          alpha=0.8, ax=ax)
    
    # Draw edges with thickness based on co-occurrence
    edge_weights = [G.edges[edge]['weight'] for edge in G.edges()]
    max_weight = max(edge_weights) if edge_weights else 1
    edge_widths = [weight / max_weight * 5 for weight in edge_weights]
    
    nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.6, 
                          edge_color='gray', ax=ax)
    
    # Draw labels
    labels = {node: node for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight='bold', ax=ax)
    
    # Add title and legend
    ax.set_title('AI Tool Ecosystem in Healthcare\nNetwork of Co-usage Patterns', 
                fontsize=16, fontweight='bold', pad=20)
    
    # Create legend for tool categories
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FF6B6B', 
                   markersize=10, label='General AI (ChatGPT)'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#4ECDC4', 
                   markersize=10, label='Medical Imaging'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#45B7D1', 
                   markersize=10, label='Documentation'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#96CEB4', 
                   markersize=10, label='Clinical Decision Support'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FFEAA7', 
                   markersize=10, label='Productivity Tools'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#DDA0DD', 
                   markersize=10, label='Other')
    ]
    
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, 1))
    
    # Add statistics text
    stats_text = f"""
    Network Statistics:
    • Total AI Tools: {len(G.nodes())}
    • Tool Connections: {len(G.edges())}
    • Most Popular: {max(tool_frequencies, key=tool_frequencies.get)} ({max(tool_frequencies.values())} mentions)
    • Network Density: {nx.density(G):.3f}
    """
    
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10, 
            verticalalignment='top', bbox=dict(boxstyle="round,pad=0.5", 
            facecolor='lightgray', alpha=0.8))
    
    # Remove axes
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    plt.tight_layout()
    
    # Save the figure
    plt.savefig('fig15_ai_tool_network.png', dpi=300, bbox_inches='tight')
    plt.savefig('fig15_ai_tool_network.pdf', bbox_inches='tight')
    
    # Show the figure
    plt.show()
    
    # Print detailed analysis
    print("AI Tool Ecosystem - Network Analysis:")
    print("=" * 50)
    
    print(f"\nTotal AI tools mentioned: {len(tool_frequencies)}")
    print(f"Tools in network (≥2 mentions): {len(G.nodes())}")
    print(f"Tool connections: {len(G.edges())}")
    print(f"Network density: {nx.density(G):.3f}")
    
    print(f"\nTool Frequencies:")
    for tool, freq in tool_frequencies.most_common():
        if freq >= 2:
            print(f"  {tool}: {freq} mentions")
    
    print(f"\nStrongest Tool Connections:")
    sorted_edges = sorted(G.edges(data=True), key=lambda x: x[2]['weight'], reverse=True)
    for edge in sorted_edges[:5]:
        print(f"  {edge[0]} ↔ {edge[1]}: {edge[2]['weight']} co-occurrences")
    
    # Calculate centrality measures
    if len(G.nodes()) > 1:
        centrality = nx.degree_centrality(G)
        print(f"\nMost Central Tools (by connections):")
        sorted_centrality = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        for tool, cent in sorted_centrality[:5]:
            print(f"  {tool}: {cent:.3f} centrality")

if __name__ == "__main__":
    create_ai_tool_network()
