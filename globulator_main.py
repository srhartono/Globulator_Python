"""
Globulator Python - Main Workflow Script
Equivalent to start.pl - batch processing pipeline for DIC/RG image pairs
"""

import os
import sys
from pathlib import Path
import argparse
from datetime import datetime
import json
import cv2
from typing import List, Tuple, Dict

# Import our modules
from globulator_core import GlobuleDetector, CrescentDetector, ContaminationDetector, ParticleData
from globulator_linker import GlobulatorLinker, LinkedParticle, AmbiguousParticle
from globulator_results import ResultsManager, SummaryAnalyzer
from globulator_visualizer import GlobulatorVisualizer

class GlobulatorPipeline:
    """
    Main pipeline class that orchestrates the complete analysis workflow
    Equivalent to start.pl functionality
    """
    
    def __init__(self, input_dir: str = "Workflows/Inputs", 
                 output_dir: str = "Results", 
                 create_visualizations: bool = True,
                 debug: bool = False):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.create_visualizations = create_visualizations
        self.debug = debug
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize processors
        self.globule_detector = GlobuleDetector()
        self.crescent_detector = CrescentDetector()
        self.contamination_detector = ContaminationDetector()
        self.linker = GlobulatorLinker()
        self.results_manager = ResultsManager(str(self.output_dir))
        
        if self.create_visualizations:
            self.visualizer = GlobulatorVisualizer(str(self.output_dir))
        
        # Set debug mode for all processors
        if self.debug:
            self.globule_detector.debug = True
            self.crescent_detector.debug = True
            self.contamination_detector.debug = True
        
        print(f"Globulator Pipeline initialized")
        print(f"Input directory: {self.input_dir}")
        print(f"Output directory: {self.output_dir}")
        print(f"Visualizations: {'Enabled' if self.create_visualizations else 'Disabled'}")
    
    def find_image_pairs(self) -> List[Tuple[Path, Path]]:
        """
        Find DIC/RG image pairs in the input directory
        Equivalent to start.pl file discovery logic
        """
        if not self.input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {self.input_dir}")
        
        # Find all image files
        image_extensions = ['.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp']
        all_images = []
        
        for ext in image_extensions:
            all_images.extend(self.input_dir.glob(f"*{ext}"))
            all_images.extend(self.input_dir.glob(f"*{ext.upper()}"))
        
        # Separate DIC and RG images based on filename patterns
        dic_images = []
        rg_images = []
        
        for image in all_images:
            filename = image.stem.lower()
            if filename.startswith('dic_') or 'dic' in filename:
                dic_images.append(image)
            elif filename.startswith('rg_') or 'rg' in filename:
                rg_images.append(image)
        
        # If no DIC/RG prefixes found, treat all images as potential pairs
        if not dic_images and not rg_images:
            print("Warning: No DIC_/RG_ prefixed files found. Processing all images as individual files.")
            # For single images, use the same image for both DIC and RG processing
            pairs = [(img, img) for img in all_images]
        else:
            # Match DIC and RG images by base filename
            pairs = []
            for dic_img in dic_images:
                # Extract base name (remove DIC_ prefix)
                dic_base = dic_img.stem.lower().replace('dic_', '')
                
                # Find matching RG image
                rg_match = None
                for rg_img in rg_images:
                    rg_base = rg_img.stem.lower().replace('rg_', '')
                    if dic_base == rg_base:
                        rg_match = rg_img
                        break
                
                if rg_match:
                    pairs.append((dic_img, rg_match))
                    print(f"Found pair: {dic_img.name} <-> {rg_match.name}")
                else:
                    print(f"Warning: No matching RG image found for {dic_img.name}")
        
        print(f"Found {len(pairs)} image pairs to process")
        return pairs
    
    def get_image_dimensions(self, image_path: Path) -> Tuple[int, int]:
        """Get image dimensions"""
        image = cv2.imread(str(image_path))
        if image is not None:
            height, width = image.shape[:2]
            return width, height
        else:
            print(f"Warning: Could not read image {image_path}, using default dimensions")
            return 1000, 1000  # Default dimensions
    
    def process_single_pair(self, dic_image: Path, rg_image: Path) -> Dict:
        """
        Process a single DIC/RG image pair
        Equivalent to processing one slide pair in start.pl
        """
        # Extract base filename (remove extensions and prefixes)
        base_name = dic_image.stem.lower().replace('dic_', '').replace('rg_', '')
        if base_name == dic_image.stem.lower():
            base_name = rg_image.stem.lower().replace('rg_', '')
        
        print(f"\\n" + "="*60)
        print(f"Processing: {base_name}")
        print(f"DIC image: {dic_image.name}")
        print(f"RG image: {rg_image.name}")
        print("="*60)
        
        try:
            # Get image dimensions (use DIC image for reference)
            image_width, image_height = self.get_image_dimensions(dic_image)
            
            # Step 1: Detect globules from DIC image
            print("Step 1: Detecting globules...")
            globules = self.globule_detector.detect_globules(str(dic_image))
            print(f"Found {len(globules)} globules")
            
            # Step 2: Detect crescents from RG image
            print("Step 2: Detecting crescents...")
            crescents = self.crescent_detector.detect_crescents(str(rg_image))
            print(f"Found {len(crescents)} crescents")
            
            # Step 3: Detect contamination from RG image
            print("Step 3: Detecting contamination...")
            contamination = self.contamination_detector.detect_contamination(str(rg_image))
            print(f"Found {len(contamination)} contamination particles")
            
            # Step 4: Link crescents to globules
            print("Step 4: Linking crescents to globules...")
            linked_particles, ambiguous_particles = self.linker.link_crescents_to_globules(
                crescents, globules, image_width, image_height
            )
            print(f"Linked {len(linked_particles)} crescent-globule pairs")
            print(f"Found {len(ambiguous_particles)} ambiguous particles")
            
            # Step 5: Calculate statistics
            print("Step 5: Calculating statistics...")
            stats = self.linker.calculate_statistics(
                linked_particles, len(globules), len(crescents)
            )
            
            # Step 6: Save results
            print("Step 6: Saving results...")
            self.results_manager.save_all_results(
                globules, crescents, contamination, linked_particles,
                ambiguous_particles, stats, base_name
            )
            
            # Step 7: Create visualizations
            if self.create_visualizations:
                print("Step 7: Creating visualizations...")
                self.visualizer.create_all_visualizations(
                    str(dic_image), globules, crescents, contamination,
                    linked_particles, ambiguous_particles, stats, base_name
                )
            
            print(f"Successfully processed {base_name}")
            
            # Return summary for batch reporting
            return {
                'filename': base_name,
                'success': True,
                'globules': len(globules),
                'crescents': len(crescents),
                'contamination': len(contamination),
                'linked_pairs': len(linked_particles),
                'nucleation_rate': stats['globule_with_crescent_percent'],
                'stats': stats
            }
            
        except Exception as e:
            print(f"Error processing {base_name}: {str(e)}")
            if self.debug:
                import traceback
                traceback.print_exc()
            
            return {
                'filename': base_name,
                'success': False,
                'error': str(e)
            }
    
    def run_batch_analysis(self) -> Dict:
        """
        Run complete batch analysis on all image pairs
        Equivalent to full start.pl execution
        """
        start_time = datetime.now()
        print(f"Starting Globulator batch analysis at {start_time}")
        print(f"Timestamp: {self.results_manager.timestamp}")
        
        # Find image pairs
        try:
            image_pairs = self.find_image_pairs()
        except Exception as e:
            print(f"Error finding image pairs: {e}")
            return {'success': False, 'error': str(e)}
        
        if not image_pairs:
            print("No image pairs found to process")
            return {'success': False, 'error': 'No image pairs found'}
        
        # Process each pair
        results = []
        successful_count = 0
        failed_count = 0
        
        for i, (dic_image, rg_image) in enumerate(image_pairs, 1):
            print(f"\\nProcessing pair {i}/{len(image_pairs)}")
            
            result = self.process_single_pair(dic_image, rg_image)
            results.append(result)
            
            if result['success']:
                successful_count += 1
            else:
                failed_count += 1
        
        # Create summary report
        print(f"\\n" + "="*60)
        print("CREATING SUMMARY REPORT")
        print("="*60)
        
        try:
            summary_analyzer = SummaryAnalyzer(str(self.output_dir))
            summary_analyzer.create_summary_report()
        except Exception as e:
            print(f"Warning: Could not create summary report: {e}")
        
        # Calculate batch statistics
        end_time = datetime.now()
        duration = end_time - start_time
        
        batch_summary = {
            'success': True,
            'timestamp': self.results_manager.timestamp,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration.total_seconds(),
            'total_pairs': len(image_pairs),
            'successful': successful_count,
            'failed': failed_count,
            'results': results
        }
        
        # Save batch summary
        summary_path = self.output_dir / f"batch_summary_{self.results_manager.timestamp}.json"
        with open(summary_path, 'w') as f:
            json.dump(batch_summary, f, indent=2, default=str)
        
        # Print final summary
        print(f"\\n" + "="*60)
        print("BATCH ANALYSIS COMPLETE")
        print("="*60)
        print(f"Total pairs processed: {len(image_pairs)}")
        print(f"Successful: {successful_count}")
        print(f"Failed: {failed_count}")
        print(f"Duration: {duration}")
        print(f"Output directory: {self.output_dir}")
        print(f"Summary saved to: {summary_path}")
        
        if successful_count > 0:
            total_globules = sum(r['globules'] for r in results if r['success'])
            total_crescents = sum(r['crescents'] for r in results if r['success'])
            total_linked = sum(r['linked_pairs'] for r in results if r['success'])
            avg_nucleation = sum(r['nucleation_rate'] for r in results if r['success']) / successful_count
            
            print(f"\\nAggregate Results:")
            print(f"Total globules detected: {total_globules}")
            print(f"Total crescents detected: {total_crescents}")
            print(f"Total linked pairs: {total_linked}")
            print(f"Average nucleation rate: {avg_nucleation:.2f}%")
        
        return batch_summary

def main():
    """Main function with command-line interface"""
    parser = argparse.ArgumentParser(
        description="Globulator Python - Automated milk fat globule analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python globulator_main.py                          # Process default input directory
  python globulator_main.py -i ./images -o ./output # Specify custom directories
  python globulator_main.py --no-viz --debug        # Disable visualizations, enable debug
        """
    )
    
    parser.add_argument('-i', '--input', type=str, default='Workflows/Inputs',
                       help='Input directory containing DIC/RG image pairs (default: Workflows/Inputs)')
    parser.add_argument('-o', '--output', type=str, default='Results',
                       help='Output directory for results (default: Results)')
    parser.add_argument('--no-viz', action='store_true',
                       help='Disable visualization generation')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug output')
    
    args = parser.parse_args()
    
    # Initialize and run pipeline
    try:
        pipeline = GlobulatorPipeline(
            input_dir=args.input,
            output_dir=args.output,
            create_visualizations=not args.no_viz,
            debug=args.debug
        )
        
        batch_result = pipeline.run_batch_analysis()
        
        # Exit with appropriate code
        if batch_result['success'] and batch_result['successful'] > 0:
            print("\\nBatch analysis completed successfully!")
            sys.exit(0)
        else:
            print("\\nBatch analysis completed with errors or no successful results")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\\nAnalysis interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\\nFatal error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()