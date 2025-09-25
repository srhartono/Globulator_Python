"""
Globulator Python - Core Image Processing Module
Port of Java/ImageJ Globulator for milk fat globule analysis
Author: Based on original Globulator by Stella Hartono
"""

import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import ndimage
from skimage import measure, morphology
from typing import Tuple, List, Dict, Optional
import os
import json
from pathlib import Path

class ParticleData:
    """Class to store particle measurements (area, centroid, etc.)"""
    def __init__(self, area: float, x: float, y: float, perimeter: float = 0.0):
        self.area = area
        self.x = x
        self.y = y
        self.perimeter = perimeter
        self.circularity = 4 * np.pi * area / (perimeter ** 2) if perimeter > 0 else 0.0
    
    def to_dict(self):
        return {
            'area': self.area,
            'x': self.x, 
            'y': self.y,
            'perimeter': self.perimeter,
            'circularity': self.circularity
        }

class ImageProcessor:
    """Core image processing class equivalent to ImageJ macros"""
    
    def __init__(self):
        self.debug = False
    
    def load_image(self, image_path: str) -> np.ndarray:
        """Load image using OpenCV"""
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        return image
    
    def rgb_to_hsv(self, image: np.ndarray) -> np.ndarray:
        """Convert RGB to HSV - equivalent to ImageJ HSB Stack"""
        return cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    def split_hsv_channels(self, hsv_image: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Split HSV into separate channels"""
        h, s, v = cv2.split(hsv_image)
        return h, s, v
    
    def apply_threshold(self, channel: np.ndarray, min_val: int, max_val: int, 
                       filter_type: str = "pass") -> np.ndarray:
        """Apply threshold to a channel - equivalent to ImageJ setThreshold + Convert to Mask"""
        if filter_type == "pass":
            mask = cv2.inRange(channel, min_val, max_val)
        else:  # "stop"
            mask = cv2.inRange(channel, min_val, max_val)
            mask = cv2.bitwise_not(mask)  # Invert for "stop" filter
        return mask
    
    def image_calculator_and(self, img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
        """Equivalent to ImageJ imageCalculator AND"""
        return cv2.bitwise_and(img1, img2)
    
    def image_calculator_or(self, img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
        """Equivalent to ImageJ imageCalculator OR"""  
        return cv2.bitwise_or(img1, img2)
    
    def analyze_particles(self, binary_mask: np.ndarray, 
                         min_area: float = 0, max_area: float = np.inf,
                         min_circularity: float = 0.0, max_circularity: float = 1.0) -> List[ParticleData]:
        """
        Equivalent to ImageJ Analyze Particles
        Returns list of ParticleData objects with measurements
        """
        # Find connected components
        labeled_img = measure.label(binary_mask)
        regions = measure.regionprops(labeled_img)
        
        particles = []
        for region in regions:
            area = region.area
            
            # Filter by area
            if area < min_area or area > max_area:
                continue
            
            # Calculate centroid
            centroid_y, centroid_x = region.centroid
            
            # Calculate perimeter
            perimeter = region.perimeter
            
            # Calculate circularity
            circularity = 4 * np.pi * area / (perimeter ** 2) if perimeter > 0 else 0.0
            
            # Filter by circularity
            if circularity < min_circularity or circularity > max_circularity:
                continue
            
            particles.append(ParticleData(area, centroid_x, centroid_y, perimeter))
        
        return particles
    
    def get_image_statistics(self, image: np.ndarray) -> Dict[str, float]:
        """Get image statistics - equivalent to ImageJ getStatistics"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        stats = {
            'mean': np.mean(gray),
            'std': np.std(gray),
            'min': np.min(gray),
            'max': np.max(gray)
        }
        return stats

class GlobuleDetector(ImageProcessor):
    """Globule detection - equivalent to GLOB_.ijm"""
    
    def detect_globules(self, image_path: str) -> List[ParticleData]:
        """
        Main globule detection method
        Equivalent to GLOB_.ijm processing
        """
        # Load image
        image = self.load_image(image_path)
        
        # Get image statistics for adaptive brightness threshold
        stats = self.get_image_statistics(image)
        average = stats['mean']
        std_dev = stats['std']
        
        # Calculate brightness threshold (equivalent to ImageJ macro logic)
        if average < 150:
            brightness_threshold = average + 2 * std_dev
            if brightness_threshold < 150:
                brightness_threshold = average + 3 * std_dev
                if brightness_threshold < 150:
                    brightness_threshold = average + 4 * std_dev
                    if brightness_threshold < 150:
                        brightness_threshold = 185
        else:
            brightness_threshold = 254
        
        # Ensure threshold doesn't exceed 255
        if brightness_threshold >= 255:
            brightness_threshold = 254
        
        # Convert to HSV
        hsv = self.rgb_to_hsv(image)
        h, s, v = self.split_hsv_channels(hsv)
        
        # Apply thresholds (equivalent to ImageJ macro)
        # Hue: 0-255 (pass)
        # Saturation: 0-255 (pass) 
        # Brightness: brightness_threshold-255 (pass)
        h_mask = self.apply_threshold(h, 0, 255, "pass")
        s_mask = self.apply_threshold(s, 0, 255, "pass")
        v_mask = self.apply_threshold(v, int(brightness_threshold), 255, "pass")
        
        # Combine masks with AND operations
        combined_mask = self.image_calculator_and(h_mask, s_mask)
        combined_mask = self.image_calculator_and(combined_mask, v_mask)
        
        # Analyze particles
        particles = self.analyze_particles(combined_mask)
        
        if self.debug:
            print(f"Detected {len(particles)} globules with brightness threshold: {brightness_threshold}")
        
        return particles

class CrescentDetector(ImageProcessor):
    """Crescent detection - equivalent to CRES_.ijm"""
    
    def detect_crescents(self, image_path: str) -> List[ParticleData]:
        """
        Main crescent detection method
        Equivalent to CRES_.ijm processing
        """
        # Load image
        image = self.load_image(image_path)
        
        # Convert to HSV
        hsv = self.rgb_to_hsv(image)
        h, s, v = self.split_hsv_channels(hsv)
        
        # Duplicate hue channel (equivalent to "Hue-1")
        h_dup = h.copy()
        
        # Apply thresholds according to CRES_.ijm
        h_mask = self.apply_threshold(h, 0, 26, "pass")      # Hue: 0-26
        s_mask = self.apply_threshold(s, 0, 255, "pass")     # Saturation: 0-255
        v_mask = self.apply_threshold(v, 52, 255, "pass")    # Brightness: 52-255
        h_dup_mask = self.apply_threshold(h_dup, 240, 255, "pass")  # Hue-1: 240-255
        
        # Boolean operations (equivalent to ImageJ imageCalculator)
        result1 = self.image_calculator_and(h_mask, s_mask)
        result2 = self.image_calculator_and(result1, v_mask)
        final_mask = self.image_calculator_or(result2, h_dup_mask)
        
        # Analyze particles
        particles = self.analyze_particles(final_mask)
        
        if self.debug:
            print(f"Detected {len(particles)} crescents")
        
        return particles

class ContaminationDetector(ImageProcessor):
    """Contamination detection - equivalent to CONT_.ijm"""
    
    def detect_contamination(self, image_path: str) -> List[ParticleData]:
        """
        Main contamination detection method
        Equivalent to CONT_.ijm processing
        """
        # Load image
        image = self.load_image(image_path)
        
        # Convert to HSV
        hsv = self.rgb_to_hsv(image)
        h, s, v = self.split_hsv_channels(hsv)
        
        # Duplicate hue channel (equivalent to "Hue-1")
        h_dup = h.copy()
        
        # Apply thresholds according to CONT_.ijm (different from crescents)
        h_mask = self.apply_threshold(h, 0, 52, "pass")      # Hue: 0-52
        s_mask = self.apply_threshold(s, 0, 255, "pass")     # Saturation: 0-255
        v_mask = self.apply_threshold(v, 52, 255, "pass")    # Brightness: 52-255
        h_dup_mask = self.apply_threshold(h_dup, 240, 255, "pass")  # Hue-1: 240-255
        
        # Boolean operations (same as crescents but different thresholds)
        result1 = self.image_calculator_and(h_mask, s_mask)
        result2 = self.image_calculator_and(result1, v_mask)
        final_mask = self.image_calculator_or(result2, h_dup_mask)
        
        # Analyze particles
        particles = self.analyze_particles(final_mask)
        
        if self.debug:
            print(f"Detected {len(particles)} contamination particles")
        
        return particles

# Test if the module works
if __name__ == "__main__":
    # Test basic functionality
    processor = ImageProcessor()
    globule_detector = GlobuleDetector()
    crescent_detector = CrescentDetector()
    contamination_detector = ContaminationDetector()
    
    print("Globulator Core module loaded successfully!")
    print("Available classes:")
    print("- ParticleData: Store particle measurements")
    print("- ImageProcessor: Base image processing")
    print("- GlobuleDetector: Detect globules (GLOB_.ijm equivalent)")
    print("- CrescentDetector: Detect crescents (CRES_.ijm equivalent)")
    print("- ContaminationDetector: Detect contamination (CONT_.ijm equivalent)")