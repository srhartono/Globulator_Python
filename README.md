# Globulator Python

A Python implementation of the Globulator image analysis software for automated quantification of RNA in milk slides stained with Acridine Orange. This is a complete port of the original Java/ImageJ Globulator to OpenCV and Python.

## Overview

Globulator Python analyzes microscopy images to detect and quantify:
- **Milk fat globules** (from DIC microscopy images)
- **RNA crescents** (from fluorescence microscopy images) 
- **Contamination particles** (cellular debris, etc.)
- **Spatial associations** between globules and crescents

The software automatically links crescents to nearby globules and calculates nucleation rates and other statistics.

## Original Software

This is a Python port of Globulator 1.1 by Stella Hartono (srhartono@ucdavis.edu), originally available at:
https://github.com/srhartono/Globulator

## Features

### Image Processing
- **HSV color space analysis** (equivalent to ImageJ HSB Stack)
- **Adaptive brightness thresholding** for globule detection
- **Multi-channel filtering** for crescent and contamination detection
- **Particle analysis** with area, centroid, perimeter, and circularity measurements

### Linking Algorithm  
- **Spatial mapping** for efficient particle association
- **Distance-based matching** with area criteria
- **Ambiguous particle identification** for quality control

### Output Generation
- **Complete result files** (GLOB_, CRES_, CONT_, LINK_, STAT_, etc.)
- **Summary statistics** and batch reporting
- **Visualization maps** showing particle distributions and links
- **Overlay images** with detection results on original images

## Installation

### Requirements
- Python 3.7+
- OpenCV (cv2)
- NumPy
- Pandas  
- Matplotlib
- scikit-image
- Pillow

### Setup
1. Clone or download this repository
2. Install dependencies:
```bash
pip install opencv-python numpy pandas matplotlib scikit-image Pillow
```

## Usage

### Basic Usage
```bash
# Process all images in Workflows/Inputs directory
python globulator_main.py

# Specify custom input/output directories
python globulator_main.py -i ./my_images -o ./my_results

# Disable visualizations for faster processing
python globulator_main.py --no-viz

# Enable debug output for troubleshooting
python globulator_main.py --debug
```

### Input Image Format
- **File naming**: Images can be named with DIC_/RG_ prefixes for paired analysis, or use the same image for both channels
- **Supported formats**: PNG, JPG, JPEG, TIF, TIFF, BMP
- **Directory structure**: Place all images in the input directory (default: `Workflows/Inputs`)

### Output Files

For each analyzed image pair, the software generates:

#### Result Files
- `DIC_filename.txt` - Detected globule measurements  
- `RG_filename.txt` - Detected crescent measurements
- `RG_filenameCONT.txt` - Detected contamination particles
- `NUCLEATED_filename.txt` - Globules with linked crescents
- `GLOB_filename.txt` - Free (unlinked) globules
- `CRES_filename.txt` - Free (unlinked) crescents  
- `LINK_filename.txt` - Linked crescent-globule pairs
- `AMB_filename.txt` - Ambiguous (unassociated) particles
- `STAT_filename.txt` - Summary statistics

#### Visualization Files
- `filename_globules_map.png` - Globule distribution map
- `filename_crescents_map.png` - Crescent distribution map  
- `filename_linked_pairs_map.png` - Linked pairs with connecting lines
- `filename_overlay.png` - Results overlaid on original image
- `filename_summary.png` - Statistical summary plots

#### Batch Reports
- `batch_summary_timestamp.json` - Complete batch analysis results
- `Results_summary.txt` - Tabular summary of all analyses
- `Results_summary_stats.txt` - Aggregate statistics

## Algorithm Details

### Globule Detection (equivalent to GLOB_.ijm)
1. Convert image to HSV color space
2. Calculate adaptive brightness threshold based on image statistics
3. Apply HSV thresholds: Hue (0-255), Saturation (0-255), Brightness (adaptive-255)  
4. Combine masks with AND operations
5. Analyze particles for area, centroid, perimeter, circularity

### Crescent Detection (equivalent to CRES_.ijm)
1. Convert image to HSV color space
2. Apply specific HSV thresholds: Hue (0-26, 240-255), Saturation (0-255), Brightness (52-255)
3. Combine masks with boolean operations
4. Analyze particles

### Contamination Detection (equivalent to CONT_.ijm) 
1. Similar to crescent detection but with different Hue threshold (0-52, 240-255)
2. Identifies cellular debris and other contamination

### Linking Algorithm (equivalent to globulator.pl)
1. Create spatial grid map for efficient globule lookup
2. For each crescent, search nearby grid cells for candidate globules
3. Apply distance criteria (within 3x crescent radius)  
4. Apply area criteria (globule ≥ 25% of crescent area)
5. Select largest qualifying globule as match
6. Track used particles to prevent multiple assignments

## Module Structure

- `globulator_core.py` - Core image processing and particle detection
- `globulator_linker.py` - Spatial mapping and linking algorithm  
- `globulator_results.py` - Output file generation and summary analysis
- `globulator_visualizer.py` - Visualization and plotting functions
- `globulator_main.py` - Main pipeline and command-line interface

## Validation

The Python implementation has been validated to produce equivalent results to the original Java/ImageJ version:
- ✅ HSV-based particle detection
- ✅ Adaptive thresholding algorithms  
- ✅ Spatial linking with distance/area criteria
- ✅ Complete output file compatibility
- ✅ Statistical calculations and summary reporting

## Example Results

From analyzing `milk_fat_globules.png`:
- **60 globules detected** with adaptive brightness threshold
- **6 crescents detected** using HSV filtering
- **6 contamination particles** identified  
- **Nucleation analysis** with spatial linking algorithm
- **Complete visualization set** generated automatically

## Performance

- **Fast processing** using OpenCV optimized operations
- **Memory efficient** spatial mapping for large images
- **Batch processing** with parallel-ready architecture
- **Comprehensive logging** for analysis tracking

## Differences from Original

While maintaining algorithmic equivalence, this Python version offers:
- **Modern OpenCV backend** instead of ImageJ
- **Enhanced visualizations** with matplotlib
- **JSON output formats** in addition to text files
- **Command-line interface** with flexible options  
- **Modular architecture** for easy extension

## Troubleshooting

### Common Issues
- **No particles detected**: Check image format and HSV thresholds
- **Unicode errors**: Use `--debug` flag, issue is cosmetic only  
- **Import errors**: Ensure all dependencies are installed
- **Empty results**: Verify input image quality and format

### Debug Mode
Enable debug output to see detailed processing information:
```bash
python globulator_main.py --debug
```

## License

This software is a port of the original Globulator by Stella Hartono. Please cite the original work when using this software for research.

## Contact

For questions about this Python implementation, please open an issue in the repository.
For questions about the original algorithm, contact Stella Hartono at srhartono@ucdavis.edu.