#!/usr/bin/env python3
"""
Test script for Globulator Python
Demonstrates basic functionality and validates installation
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test that all modules can be imported"""
    print("Testing module imports...")
    
    try:
        from globulator_core import GlobuleDetector, CrescentDetector, ContaminationDetector
        from globulator_linker import GlobulatorLinker  
        from globulator_results import ResultsManager, SummaryAnalyzer
        from globulator_visualizer import GlobulatorVisualizer
        from globulator_main import GlobulatorPipeline
        print("✓ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_sample_analysis():
    """Test analysis with sample images if available"""
    print("\nTesting sample analysis...")
    
    input_dir = Path("Workflows/Inputs")
    if not input_dir.exists():
        print("⚠ No Workflows/Inputs directory found - skipping sample analysis")
        return True
        
    sample_images = list(input_dir.glob("*.png")) + list(input_dir.glob("*.jpg"))
    if not sample_images:
        print("⚠ No sample images found in Workflows/Inputs - skipping analysis")
        return True
    
    print(f"Found {len(sample_images)} sample images")
    
    try:
        from globulator_main import GlobulatorPipeline
        
        # Test with first image
        test_image = sample_images[0]
        print(f"Testing with: {test_image.name}")
        
        pipeline = GlobulatorPipeline(
            input_dir=str(input_dir),
            output_dir="Test_Results", 
            create_visualizations=False,  # Skip visualizations for speed
            debug=False
        )
        
        result = pipeline.process_single_pair(test_image, test_image)
        
        if result['success']:
            print("✓ Sample analysis completed successfully")
            print(f"  - Globules: {result['globules']}")
            print(f"  - Crescents: {result['crescents']}")
            print(f"  - Contamination: {result['contamination']}")
            print(f"  - Linked pairs: {result['linked_pairs']}")
            return True
        else:
            print(f"✗ Sample analysis failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"✗ Error during sample analysis: {e}")
        return False

def test_individual_detectors():
    """Test individual detector components"""
    print("\nTesting individual detectors...")
    
    input_dir = Path("Workflows/Inputs")
    sample_images = list(input_dir.glob("*.png")) + list(input_dir.glob("*.jpg"))
    
    if not sample_images:
        print("⚠ No sample images available for detector testing")
        return True
        
    test_image = str(sample_images[0])
    print(f"Using test image: {sample_images[0].name}")
    
    try:
        from globulator_core import GlobuleDetector, CrescentDetector, ContaminationDetector
        
        # Test globule detection
        globule_detector = GlobuleDetector()
        globules = globule_detector.detect_globules(test_image)
        print(f"  - Globule detector: {len(globules)} particles detected")
        
        # Test crescent detection  
        crescent_detector = CrescentDetector()
        crescents = crescent_detector.detect_crescents(test_image)
        print(f"  - Crescent detector: {len(crescents)} particles detected")
        
        # Test contamination detection
        contamination_detector = ContaminationDetector()
        contamination = contamination_detector.detect_contamination(test_image)
        print(f"  - Contamination detector: {len(contamination)} particles detected")
        
        print("✓ All detectors working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Error testing detectors: {e}")
        return False

def run_all_tests():
    """Run all test functions"""
    print("=" * 50)
    print("GLOBULATOR PYTHON - TEST SUITE")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Individual Detectors", test_individual_detectors), 
        ("Sample Analysis", test_sample_analysis),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * len(test_name))
        
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "PASS" if success else "FAIL" 
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Globulator Python is ready to use.")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Check installation and dependencies.")
        return 1

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)