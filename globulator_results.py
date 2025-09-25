"""
Globulator Python - Results Analysis and Output System
Generate output files equivalent to globulator.pl results
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
from typing import List, Dict
from pathlib import Path
import json

from globulator_core import ParticleData
from globulator_linker import LinkedParticle, AmbiguousParticle, GlobulatorLinker

class ResultsManager:
    """
    Manages output generation and file writing
    Equivalent to globulator.pl output functionality
    """
    
    def __init__(self, output_dir: str = "Results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
        
    def save_globule_results(self, globules: List[ParticleData], filename: str):
        """
        Save globule detection results to GLOB_*.txt
        Format matches original ImageJ output
        """
        if not globules:
            # Create empty file with headers
            df = pd.DataFrame(columns=['Area', 'X', 'Y', 'Perim.', 'Circ.'])
        else:
            data = []
            for i, globule in enumerate(globules, 1):
                data.append({
                    'Area': globule.area,
                    'X': globule.x,
                    'Y': globule.y,
                    'Perim.': globule.perimeter,
                    'Circ.': globule.circularity
                })
            df = pd.DataFrame(data)
        
        # Save with header comment (matching ImageJ format)
        output_path = self.output_dir / f"DIC_{filename}.txt"
        with open(output_path, 'w') as f:
            f.write("  \t\\n")  # ImageJ header format
            f.write(" \tArea\tX\tY\tPerim.\tCirc.\\n")  # ImageJ column headers
            df.to_csv(f, sep='\t', index=False, header=False, float_format='%.3f')
        
        print(f"Saved {len(globules)} globules to {output_path}")
    
    def save_crescent_results(self, crescents: List[ParticleData], filename: str):
        """
        Save crescent detection results to RG_*.txt
        Format matches original ImageJ output
        """
        if not crescents:
            # Create empty file with headers
            df = pd.DataFrame(columns=['Area', 'X', 'Y', 'Perim.', 'Circ.'])
        else:
            data = []
            for crescent in crescents:
                data.append({
                    'Area': crescent.area,
                    'X': crescent.x,
                    'Y': crescent.y,
                    'Perim.': crescent.perimeter,
                    'Circ.': crescent.circularity
                })
            df = pd.DataFrame(data)
        
        # Save with ImageJ format
        output_path = self.output_dir / f"RG_{filename}.txt"
        with open(output_path, 'w') as f:
            f.write("  \t\\n")  # ImageJ header format
            f.write(" \tArea\tX\tY\tPerim.\tCirc.\\n")  # ImageJ column headers
            df.to_csv(f, sep='\t', index=False, header=False, float_format='%.3f')
        
        print(f"Saved {len(crescents)} crescents to {output_path}")
    
    def save_contamination_results(self, contamination: List[ParticleData], filename: str):
        """
        Save contamination detection results to RG_*CONT.txt
        Format matches original ImageJ output
        """
        if not contamination:
            # Create empty file with headers
            df = pd.DataFrame(columns=['Area', 'X', 'Y', 'Perim.', 'Circ.'])
        else:
            data = []
            for cont in contamination:
                data.append({
                    'Area': cont.area,
                    'X': cont.x,
                    'Y': cont.y,
                    'Perim.': cont.perimeter,
                    'Circ.': cont.circularity
                })
            df = pd.DataFrame(data)
        
        # Save with ImageJ format
        output_path = self.output_dir / f"RG_{filename}CONT.txt"
        with open(output_path, 'w') as f:
            f.write("  \t\\n")  # ImageJ header format
            f.write(" \tArea\tX\tY\tPerim.\tCirc.\\n")  # ImageJ column headers
            df.to_csv(f, sep='\t', index=False, header=False, float_format='%.3f')
        
        print(f"Saved {len(contamination)} contamination particles to {output_path}")
    
    def save_nucleated_results(self, linked_particles: List[LinkedParticle], filename: str):
        """
        Save nucleated (linked) globules to NUCLEATED_*.txt
        Only globules that have linked crescents
        """
        if not linked_particles:
            # Create empty file
            data = []
        else:
            data = []
            for linked in linked_particles:
                data.append({
                    'Area': linked.globule.area,
                    'X': linked.globule.x,
                    'Y': linked.globule.y,
                    'Perim.': linked.globule.perimeter,
                    'Circ.': linked.globule.circularity
                })
        
        df = pd.DataFrame(data)
        output_path = self.output_dir / f"NUCLEATED_{filename}.txt"
        df.to_csv(output_path, sep='\t', index=False, float_format='%.3f')
        print(f"Saved {len(linked_particles)} nucleated globules to {output_path}")
    
    def save_globule_only_results(self, globules: List[ParticleData], 
                                 used_globules: set, filename: str):
        """
        Save globules without crescents to GLOB_*.txt
        """
        free_globules = [g for g in globules if id(g) not in used_globules]
        
        if not free_globules:
            data = []
        else:
            data = []
            for globule in free_globules:
                data.append({
                    'Area': globule.area,
                    'X': globule.x,
                    'Y': globule.y,
                    'Perim.': globule.perimeter,
                    'Circ.': globule.circularity
                })
        
        df = pd.DataFrame(data)
        output_path = self.output_dir / f"GLOB_{filename}.txt"
        df.to_csv(output_path, sep='\t', index=False, float_format='%.3f')
        print(f"Saved {len(free_globules)} free globules to {output_path}")
    
    def save_crescent_only_results(self, crescents: List[ParticleData], 
                                  used_crescents: set, filename: str):
        """
        Save crescents without globules to CRES_*.txt
        """
        free_crescents = [c for c in crescents if id(c) not in used_crescents]
        
        if not free_crescents:
            data = []
        else:
            data = []
            for crescent in free_crescents:
                data.append({
                    'Area': crescent.area,
                    'X': crescent.x,
                    'Y': crescent.y,
                    'Perim.': crescent.perimeter,
                    'Circ.': crescent.circularity
                })
        
        df = pd.DataFrame(data)
        output_path = self.output_dir / f"CRES_{filename}.txt"
        df.to_csv(output_path, sep='\t', index=False, float_format='%.3f')
        print(f"Saved {len(free_crescents)} free crescents to {output_path}")
    
    def save_linked_results(self, linked_particles: List[LinkedParticle], filename: str):
        """
        Save linked crescent-globule pairs to LINK_*.txt
        """
        if not linked_particles:
            data = []
        else:
            data = []
            for linked in linked_particles:
                data.append({
                    'Cres_area': linked.crescent.area,
                    'Cres_x': linked.crescent.x,
                    'Cres_y': linked.crescent.y,
                    'Glob_area': linked.globule.area,
                    'Glob_x': linked.globule.x,
                    'Glob_y': linked.globule.y,
                    'Distance': linked.distance
                })
        
        df = pd.DataFrame(data)
        output_path = self.output_dir / f"LINK_{filename}.txt"
        df.to_csv(output_path, sep='\t', index=False, float_format='%.3f')
        print(f"Saved {len(linked_particles)} linked pairs to {output_path}")
    
    def save_ambiguous_results(self, ambiguous_particles: List[AmbiguousParticle], filename: str):
        """
        Save ambiguous (unlinked) particles to AMB_*.txt
        """
        if not ambiguous_particles:
            data = []
        else:
            data = []
            for amb in ambiguous_particles:
                data.append({
                    'Type': amb.type,
                    'Area': amb.particle.area,
                    'X': amb.particle.x,
                    'Y': amb.particle.y,
                    'Perim.': amb.particle.perimeter,
                    'Circ.': amb.particle.circularity
                })
        
        df = pd.DataFrame(data)
        output_path = self.output_dir / f"AMB_{filename}.txt"
        df.to_csv(output_path, sep='\t', index=False, float_format='%.3f')
        print(f"Saved {len(ambiguous_particles)} ambiguous particles to {output_path}")
    
    def save_statistics(self, stats: Dict[str, float], filename: str):
        """
        Save summary statistics to STAT_*.txt
        """
        output_path = self.output_dir / f"STAT_{filename}.txt"
        
        with open(output_path, 'w') as f:
            f.write("Globulator Analysis Statistics\\n")
            f.write(f"Filename: {filename}\\n")
            f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")
            f.write("\\n")
            f.write(f"Total Globules: {stats['total_globules']}\\n")
            f.write(f"Total Crescents: {stats['total_crescents']}\\n")
            f.write(f"Linked Pairs: {stats['linked_pairs']}\\n")
            f.write(f"Globules with Crescents (%): {stats['globule_with_crescent_percent']:.2f}\\n")
            f.write(f"Average Crescent Area: {stats['average_crescent_area']:.3f}\\n")
            f.write(f"Average Globule Area: {stats['average_globule_area']:.3f}\\n")
        
        print(f"Saved statistics to {output_path}")
    
    def save_all_results(self, globules: List[ParticleData], crescents: List[ParticleData],
                        contamination: List[ParticleData], linked_particles: List[LinkedParticle],
                        ambiguous_particles: List[AmbiguousParticle], stats: Dict[str, float],
                        filename: str):
        """
        Save all results for a single image analysis
        Equivalent to complete globulator.pl output
        """
        print(f"\\nSaving all results for {filename}...")
        
        # Extract used particles for tracking
        used_globules = {id(lp.globule) for lp in linked_particles}
        used_crescents = {id(lp.crescent) for lp in linked_particles}
        
        # Save all result types
        self.save_globule_results(globules, filename)
        self.save_crescent_results(crescents, filename)
        self.save_contamination_results(contamination, filename)
        self.save_nucleated_results(linked_particles, filename)
        self.save_globule_only_results(globules, used_globules, filename)
        self.save_crescent_only_results(crescents, used_crescents, filename)
        self.save_linked_results(linked_particles, filename)
        self.save_ambiguous_results(ambiguous_particles, filename)
        self.save_statistics(stats, filename)
        
        print(f"All results saved for {filename}")

class SummaryAnalyzer:
    """
    Equivalent to summarizer.pl functionality
    Creates summary reports from multiple analysis results
    """
    
    def __init__(self, results_dir: str):
        self.results_dir = Path(results_dir)
    
    def create_summary_report(self, output_filename: str = None):
        """
        Create summary report from all STAT_*.txt files in results directory
        """
        stat_files = list(self.results_dir.glob("STAT_*.txt"))
        
        if not stat_files:
            print("No STAT_*.txt files found for summary")
            return
        
        if output_filename is None:
            output_filename = f"{self.results_dir.name}_summary.txt"
        
        summary_data = []
        
        for stat_file in stat_files:
            # Parse filename to extract base name
            filename = stat_file.stem.replace("STAT_", "")
            
            # Read statistics from file (simple parsing)
            stats = {}
            try:
                with open(stat_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        if ':' in line:
                            key, value = line.strip().split(':', 1)
                            key = key.strip()
                            value = value.strip()
                            
                            # Try to convert to number
                            try:
                                if '.' in value:
                                    stats[key] = float(value)
                                else:
                                    stats[key] = int(value)
                            except ValueError:
                                stats[key] = value
                
                stats['Filename'] = filename
                summary_data.append(stats)
                
            except Exception as e:
                print(f"Error reading {stat_file}: {e}")
        
        if not summary_data:
            print("No valid statistics found for summary")
            return
        
        # Create summary DataFrame
        df = pd.DataFrame(summary_data)
        
        # Reorder columns
        column_order = ['Filename', 'Total Globules', 'Total Crescents', 'Linked Pairs', 
                       'Globules with Crescents (%)', 'Average Crescent Area', 'Average Globule Area']
        
        df = df.reindex(columns=[col for col in column_order if col in df.columns])
        
        # Save summary
        output_path = self.results_dir / output_filename
        df.to_csv(output_path, sep='\\t', index=False, float_format='%.3f')
        
        # Also save summary statistics
        summary_stats_path = self.results_dir / output_filename.replace('.txt', '_stats.txt')
        with open(summary_stats_path, 'w') as f:
            f.write("GLOBULATOR BATCH SUMMARY STATISTICS\\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")
            f.write(f"Total Files Analyzed: {len(summary_data)}\\n")
            f.write("\\n")
            
            # Calculate aggregate statistics
            if 'Total Globules' in df.columns:
                f.write(f"Total Globules (all files): {df['Total Globules'].sum()}\\n")
                f.write(f"Average Globules per file: {df['Total Globules'].mean():.2f}\\n")
            
            if 'Total Crescents' in df.columns:
                f.write(f"Total Crescents (all files): {df['Total Crescents'].sum()}\\n")
                f.write(f"Average Crescents per file: {df['Total Crescents'].mean():.2f}\\n")
            
            if 'Linked Pairs' in df.columns:
                f.write(f"Total Linked Pairs (all files): {df['Linked Pairs'].sum()}\\n")
                f.write(f"Average Linked Pairs per file: {df['Linked Pairs'].mean():.2f}\\n")
            
            if 'Globules with Crescents (%)' in df.columns:
                f.write(f"Average Nucleation Rate: {df['Globules with Crescents (%)'].mean():.2f}%\\n")
        
        print(f"Summary report saved to {output_path}")
        print(f"Summary statistics saved to {summary_stats_path}")

# Test the results module
if __name__ == "__main__":
    # Test basic functionality
    results_manager = ResultsManager()
    print("Globulator Results module loaded successfully!")
    print("Available classes:")
    print("- ResultsManager: Save analysis results to files")
    print("- SummaryAnalyzer: Create summary reports from batch results")