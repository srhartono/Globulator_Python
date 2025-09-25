"""
Globulator Python - Visualization Tools
Equivalent to draw_*.R scripts for result validation and overlay visualization
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle
from typing import List, Tuple, Optional
from pathlib import Path
import pandas as pd

from globulator_core import ParticleData
from globulator_linker import LinkedParticle, AmbiguousParticle

class GlobulatorVisualizer:
    """
    Visualization tools for Globulator results
    Equivalent to draw_*.R functionality
    """
    
    def __init__(self, output_dir: str = "Results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def calculate_particle_radius(self, area: float) -> float:
        """Calculate radius from area assuming circular particle"""
        return np.sqrt(area / np.pi)
    
    def draw_globules_map(self, globules: List[ParticleData], image_width: int, image_height: int,
                         filename: str, title: str = "Globules Map", color: str = 'blue'):
        """
        Draw globules as circles on a map
        Equivalent to draw_glob.R
        """
        if not globules:
            print(f"No globules to draw for {filename}")
            return
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Set up the plot area
        ax.set_xlim(0, image_width * 1.1)
        ax.set_ylim(0, image_height * 1.1)
        ax.set_aspect('equal')
        ax.invert_yaxis()  # Invert y-axis to match image coordinates
        
        # Draw each globule as a circle
        for globule in globules:
            radius = self.calculate_particle_radius(globule.area)
            circle = Circle((globule.x, globule.y), radius, 
                          fill=False, edgecolor=color, linewidth=1)
            ax.add_patch(circle)
        
        ax.set_title(title)
        ax.set_xlabel('X Coordinate')
        ax.set_ylabel('Y Coordinate')
        
        # Save the plot
        output_path = self.output_dir / f"{filename}_globules_map.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Saved globules map to {output_path}")
    
    def draw_crescents_map(self, crescents: List[ParticleData], image_width: int, image_height: int,
                          filename: str, title: str = "Crescents Map", color: str = 'red'):
        """
        Draw crescents as circles on a map
        Equivalent to draw_cres.R
        """
        if not crescents:
            print(f"No crescents to draw for {filename}")
            return
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Set up the plot area
        ax.set_xlim(0, image_width * 1.1)
        ax.set_ylim(0, image_height * 1.1)
        ax.set_aspect('equal')
        ax.invert_yaxis()  # Invert y-axis to match image coordinates
        
        # Draw each crescent as a circle
        for crescent in crescents:
            radius = self.calculate_particle_radius(crescent.area)
            circle = Circle((crescent.x, crescent.y), radius, 
                          fill=False, edgecolor=color, linewidth=1)
            ax.add_patch(circle)
        
        ax.set_title(title)
        ax.set_xlabel('X Coordinate')
        ax.set_ylabel('Y Coordinate')
        
        # Save the plot
        output_path = self.output_dir / f"{filename}_crescents_map.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Saved crescents map to {output_path}")
    
    def draw_linked_pairs_map(self, linked_particles: List[LinkedParticle], 
                             image_width: int, image_height: int, filename: str,
                             title: str = "Linked Pairs Map"):
        """
        Draw linked crescent-globule pairs with connecting lines
        Equivalent to draw_link.R
        """
        if not linked_particles:
            print(f"No linked pairs to draw for {filename}")
            return
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Set up the plot area
        ax.set_xlim(0, image_width * 1.1)
        ax.set_ylim(0, image_height * 1.1)
        ax.set_aspect('equal')
        ax.invert_yaxis()  # Invert y-axis to match image coordinates
        
        # Draw each linked pair
        for linked in linked_particles:
            # Draw globule (blue circle)
            glob_radius = self.calculate_particle_radius(linked.globule.area)
            glob_circle = Circle((linked.globule.x, linked.globule.y), glob_radius, 
                               fill=False, edgecolor='blue', linewidth=2, label='Globules')
            ax.add_patch(glob_circle)
            
            # Draw crescent (red circle)
            cres_radius = self.calculate_particle_radius(linked.crescent.area)
            cres_circle = Circle((linked.crescent.x, linked.crescent.y), cres_radius, 
                               fill=False, edgecolor='red', linewidth=2, label='Crescents')
            ax.add_patch(cres_circle)
            
            # Draw connecting line (green)
            ax.plot([linked.globule.x, linked.crescent.x], 
                   [linked.globule.y, linked.crescent.y], 
                   color='green', linewidth=1, alpha=0.7)
        
        ax.set_title(title)
        ax.set_xlabel('X Coordinate')
        ax.set_ylabel('Y Coordinate')
        
        # Add legend
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], color='blue', linewidth=2, label='Globules'),
            Line2D([0], [0], color='red', linewidth=2, label='Crescents'),
            Line2D([0], [0], color='green', linewidth=1, label='Links')
        ]
        ax.legend(handles=legend_elements)
        
        # Save the plot
        output_path = self.output_dir / f"{filename}_linked_pairs_map.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Saved linked pairs map to {output_path}")
    
    def draw_overlay_on_original(self, image_path: str, globules: List[ParticleData], 
                                crescents: List[ParticleData], linked_particles: List[LinkedParticle],
                                filename: str):
        """
        Draw detection results overlaid on the original image
        """
        # Load original image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Could not load original image: {image_path}")
            return
        
        # Convert BGR to RGB for matplotlib
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        fig, ax = plt.subplots(figsize=(15, 10))
        ax.imshow(image)
        
        # Draw globules (blue circles)
        used_globules = {id(lp.globule) for lp in linked_particles}
        for globule in globules:
            radius = self.calculate_particle_radius(globule.area)
            color = 'cyan' if id(globule) in used_globules else 'blue'
            circle = Circle((globule.x, globule.y), radius, 
                          fill=False, edgecolor=color, linewidth=2)
            ax.add_patch(circle)
        
        # Draw crescents (red circles)
        used_crescents = {id(lp.crescent) for lp in linked_particles}
        for crescent in crescents:
            radius = self.calculate_particle_radius(crescent.area)
            color = 'yellow' if id(crescent) in used_crescents else 'red'
            circle = Circle((crescent.x, crescent.y), radius, 
                          fill=False, edgecolor=color, linewidth=2)
            ax.add_patch(circle)
        
        # Draw links (green lines)
        for linked in linked_particles:
            ax.plot([linked.globule.x, linked.crescent.x], 
                   [linked.globule.y, linked.crescent.y], 
                   color='green', linewidth=2, alpha=0.8)
        
        ax.set_title(f"Detection Results Overlay - {filename}")
        ax.axis('off')  # Hide axes for overlay
        
        # Add legend
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], color='blue', linewidth=2, label='Free Globules'),
            Line2D([0], [0], color='cyan', linewidth=2, label='Linked Globules'),
            Line2D([0], [0], color='red', linewidth=2, label='Free Crescents'),
            Line2D([0], [0], color='yellow', linewidth=2, label='Linked Crescents'),
            Line2D([0], [0], color='green', linewidth=2, label='Links')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        # Save the overlay
        output_path = self.output_dir / f"{filename}_overlay.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Saved overlay image to {output_path}")
    
    def create_analysis_summary_plot(self, stats_dict: dict, filename: str):
        """
        Create a summary plot with key statistics
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # Plot 1: Particle counts
        categories = ['Globules', 'Crescents', 'Linked Pairs']
        counts = [
            stats_dict.get('total_globules', 0),
            stats_dict.get('total_crescents', 0),
            stats_dict.get('linked_pairs', 0)
        ]
        colors = ['blue', 'red', 'green']
        
        bars = ax1.bar(categories, counts, color=colors, alpha=0.7)
        ax1.set_title('Particle Counts')
        ax1.set_ylabel('Count')
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(counts)*0.01,
                    str(count), ha='center', va='bottom')
        
        # Plot 2: Nucleation rate
        nucleation_rate = stats_dict.get('globule_with_crescent_percent', 0)
        ax2.pie([nucleation_rate, 100-nucleation_rate], 
               labels=['Nucleated', 'Free'], 
               colors=['lightgreen', 'lightcoral'],
               autopct='%1.1f%%',
               startangle=90)
        ax2.set_title(f'Globule Nucleation Rate: {nucleation_rate:.1f}%')
        
        # Plot 3: Average areas
        if stats_dict.get('linked_pairs', 0) > 0:
            area_categories = ['Crescent Area', 'Globule Area']
            area_values = [
                stats_dict.get('average_crescent_area', 0),
                stats_dict.get('average_globule_area', 0)
            ]
            ax3.bar(area_categories, area_values, color=['red', 'blue'], alpha=0.7)
            ax3.set_title('Average Particle Areas (Linked Only)')
            ax3.set_ylabel('Area (pixels²)')
            
            # Add value labels
            for i, (cat, val) in enumerate(zip(area_categories, area_values)):
                ax3.text(i, val + max(area_values)*0.01, f'{val:.1f}', 
                        ha='center', va='bottom')
        else:
            ax3.text(0.5, 0.5, 'No linked pairs found', 
                    ha='center', va='center', transform=ax3.transAxes)
            ax3.set_title('Average Particle Areas')
        
        # Plot 4: Statistics summary text
        ax4.axis('off')
        stats_text = f"""
Analysis Summary for {filename}

Total Particles Detected:
• Globules: {stats_dict.get('total_globules', 0)}
• Crescents: {stats_dict.get('total_crescents', 0)}
• Contamination: {stats_dict.get('total_contamination', 0)}

Linking Results:
• Linked Pairs: {stats_dict.get('linked_pairs', 0)}
• Nucleation Rate: {stats_dict.get('globule_with_crescent_percent', 0):.2f}%
• Free Globules: {stats_dict.get('total_globules', 0) - stats_dict.get('linked_pairs', 0)}
• Free Crescents: {stats_dict.get('total_crescents', 0) - stats_dict.get('linked_pairs', 0)}

Average Measurements:
• Crescent Area: {stats_dict.get('average_crescent_area', 0):.1f} px²
• Globule Area: {stats_dict.get('average_globule_area', 0):.1f} px²
        """
        ax4.text(0.1, 0.9, stats_text, transform=ax4.transAxes, 
                fontsize=12, verticalalignment='top', fontfamily='monospace')
        
        plt.tight_layout()
        
        # Save the summary plot
        output_path = self.output_dir / f"{filename}_summary.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Saved analysis summary to {output_path}")
    
    def create_all_visualizations(self, image_path: str, globules: List[ParticleData],
                                 crescents: List[ParticleData], contamination: List[ParticleData],
                                 linked_particles: List[LinkedParticle], 
                                 ambiguous_particles: List[AmbiguousParticle],
                                 stats_dict: dict, filename: str):
        """
        Create all visualization outputs for a single analysis
        """
        print(f"\\nGenerating visualizations for {filename}...")
        
        # Get image dimensions
        image = cv2.imread(image_path)
        if image is not None:
            image_height, image_width = image.shape[:2]
        else:
            # Use default dimensions if image can't be loaded
            image_width, image_height = 1000, 1000
            print(f"Warning: Could not load image {image_path}, using default dimensions")
        
        # Create individual maps
        self.draw_globules_map(globules, image_width, image_height, filename)
        self.draw_crescents_map(crescents, image_width, image_height, filename)
        self.draw_linked_pairs_map(linked_particles, image_width, image_height, filename)
        
        # Create overlay on original image
        if image is not None:
            self.draw_overlay_on_original(image_path, globules, crescents, 
                                        linked_particles, filename)
        
        # Create summary statistics plot
        stats_with_contamination = stats_dict.copy()
        stats_with_contamination['total_contamination'] = len(contamination)
        self.create_analysis_summary_plot(stats_with_contamination, filename)
        
        print(f"All visualizations generated for {filename}")

# Test the visualization module
if __name__ == "__main__":
    # Test basic functionality
    visualizer = GlobulatorVisualizer()
    print("Globulator Visualization module loaded successfully!")
    print("Available functionality:")
    print("- draw_globules_map(): Create globule distribution map")
    print("- draw_crescents_map(): Create crescent distribution map") 
    print("- draw_linked_pairs_map(): Create linked pairs visualization")
    print("- draw_overlay_on_original(): Overlay results on original image")
    print("- create_analysis_summary_plot(): Generate summary statistics plot")
    print("- create_all_visualizations(): Generate complete visualization set")