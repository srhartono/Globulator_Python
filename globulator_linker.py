"""
Globulator Python - Linking Algorithm Module
Port of globulator.pl for linking crescents to globules
"""

import numpy as np
import math
from typing import List, Tuple, Dict, Optional
from globulator_core import ParticleData

class LinkedParticle:
    """Represents a linked crescent-globule pair"""
    def __init__(self, crescent: ParticleData, globule: ParticleData, distance: float):
        self.crescent = crescent
        self.globule = globule
        self.distance = distance
    
    def to_dict(self):
        return {
            'cres_area': self.crescent.area,
            'cres_x': self.crescent.x,
            'cres_y': self.crescent.y,
            'glob_area': self.globule.area,
            'glob_x': self.globule.x,
            'glob_y': self.globule.y,
            'distance': self.distance
        }

class AmbiguousParticle:
    """Represents particles that couldn't be linked"""
    def __init__(self, particle: ParticleData, particle_type: str):
        self.particle = particle
        self.type = particle_type  # 'crescent' or 'globule'
    
    def to_dict(self):
        return {
            'area': self.particle.area,
            'x': self.particle.x,
            'y': self.particle.y,
            'type': self.type
        }

class GlobulatorLinker:
    """
    Main linking algorithm - ports globulator.pl logic
    Links crescents to globules using spatial mapping and distance criteria
    """
    
    def __init__(self, map_length: int = 50, map_width: int = 50):
        self.map_length = map_length  # Grid cell size for spatial mapping
        self.map_width = map_width
        self.pi = math.pi
    
    def calculate_distance(self, x1: float, y1: float, x2: float, y2: float) -> float:
        """Calculate Euclidean distance between two points"""
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    
    def calculate_radius(self, area: float) -> float:
        """Calculate radius from area assuming circular particle"""
        return math.sqrt(area / self.pi)
    
    def create_spatial_map(self, globules: List[ParticleData], 
                          image_width: int, image_height: int) -> List[List[List[ParticleData]]]:
        """
        Create spatial grid map for efficient globule lookup
        Equivalent to globulator.pl map creation
        """
        # Calculate map dimensions
        map_x_size = (image_width // self.map_length) + 1
        map_y_size = (image_height // self.map_width) + 1
        
        # Initialize empty map
        spatial_map = [[[] for _ in range(map_y_size)] for _ in range(map_x_size)]
        
        # Place globules in map grid cells
        for globule in globules:
            map_x = int(globule.x // self.map_length)
            map_y = int(globule.y // self.map_width)
            
            # Ensure coordinates are within bounds
            map_x = max(0, min(map_x, map_x_size - 1))
            map_y = max(0, min(map_y, map_y_size - 1))
            
            spatial_map[map_x][map_y].append(globule)
        
        return spatial_map
    
    def get_nearby_globules(self, crescent: ParticleData, spatial_map: List[List[List[ParticleData]]],
                           search_radius: int = 1) -> List[Tuple[float, ParticleData]]:
        """
        Get globules in nearby map cells with their distances to the crescent
        Equivalent to globulator.pl bin creation and search
        """
        map_x = int(crescent.x // self.map_length)
        map_y = int(crescent.y // self.map_width)
        
        nearby_globules = []
        
        # Search in surrounding cells (equivalent to Perl min_x, max_x, min_y, max_y logic)
        min_x = max(0, map_x - search_radius)
        max_x = min(len(spatial_map) - 1, map_x + search_radius)
        min_y = max(0, map_y - search_radius)
        max_y = min(len(spatial_map[0]) - 1, map_y + search_radius)
        
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                for globule in spatial_map[x][y]:
                    distance = self.calculate_distance(crescent.x, crescent.y, 
                                                     globule.x, globule.y)
                    nearby_globules.append((distance, globule))
        
        # Sort by distance (closest first)
        nearby_globules.sort(key=lambda x: x[0])
        return nearby_globules
    
    def find_best_globule_for_crescent(self, crescent: ParticleData, 
                                      nearby_globules: List[Tuple[float, ParticleData]]) -> Optional[Tuple[float, ParticleData]]:
        """
        Find the best globule match for a crescent
        Equivalent to globulator.pl equalizer function
        """
        if not nearby_globules:
            return None
        
        crescent_area = crescent.area
        crescent_radius = self.calculate_radius(crescent_area)
        radius_limit = crescent_radius * 3  # Search within 3x crescent radius
        
        # Filter globules within radius limit
        candidate_globules = []
        for distance, globule in nearby_globules:
            if distance <= radius_limit:
                candidate_globules.append((distance, globule))
        
        if not candidate_globules:
            return None
        
        # Find globules that meet the area criteria
        # Globule area must be at least 25% of crescent area
        valid_globules = []
        for distance, globule in candidate_globules:
            if globule.area >= (0.25 * crescent_area):
                valid_globules.append((distance, globule))
        
        if not valid_globules:
            return None
        
        # Return the largest valid globule (equivalent to Perl logic)
        best_globule = max(valid_globules, key=lambda x: x[1].area)
        return best_globule
    
    def link_crescents_to_globules(self, crescents: List[ParticleData], 
                                  globules: List[ParticleData],
                                  image_width: int, image_height: int) -> Tuple[List[LinkedParticle], List[AmbiguousParticle]]:
        """
        Main linking algorithm
        Links crescents to globules using spatial mapping and criteria matching
        """
        # Create spatial map for efficient globule lookup
        spatial_map = self.create_spatial_map(globules, image_width, image_height)
        
        linked_particles = []
        ambiguous_particles = []
        used_globules = set()  # Track which globules have been used
        
        # Process each crescent
        for crescent in crescents:
            # Find nearby globules
            nearby_globules = self.get_nearby_globules(crescent, spatial_map)
            
            # Filter out already used globules
            available_globules = [(dist, glob) for dist, glob in nearby_globules 
                                if id(glob) not in used_globules]
            
            # Find best match
            best_match = self.find_best_globule_for_crescent(crescent, available_globules)
            
            if best_match:
                distance, globule = best_match
                linked_particles.append(LinkedParticle(crescent, globule, distance))
                used_globules.add(id(globule))
            else:
                # Crescent couldn't be linked - mark as ambiguous
                ambiguous_particles.append(AmbiguousParticle(crescent, 'crescent'))
        
        # Mark unused globules as ambiguous
        for globule in globules:
            if id(globule) not in used_globules:
                ambiguous_particles.append(AmbiguousParticle(globule, 'globule'))
        
        return linked_particles, ambiguous_particles
    
    def calculate_statistics(self, linked_particles: List[LinkedParticle], 
                           total_globules: int, total_crescents: int) -> Dict[str, float]:
        """
        Calculate summary statistics
        Equivalent to globulator.pl STAT_ output
        """
        if total_globules == 0:
            return {
                'total_globules': 0,
                'total_crescents': total_crescents,
                'linked_pairs': 0,
                'globule_with_crescent_percent': 0.0,
                'average_crescent_area': 0.0,
                'average_globule_area': 0.0
            }
        
        linked_count = len(linked_particles)
        globule_with_crescent_percent = (linked_count / total_globules) * 100
        
        # Calculate average areas
        if linked_count > 0:
            avg_crescent_area = sum(lp.crescent.area for lp in linked_particles) / linked_count
            avg_globule_area = sum(lp.globule.area for lp in linked_particles) / linked_count
        else:
            avg_crescent_area = 0.0
            avg_globule_area = 0.0
        
        return {
            'total_globules': total_globules,
            'total_crescents': total_crescents,
            'linked_pairs': linked_count,
            'globule_with_crescent_percent': globule_with_crescent_percent,
            'average_crescent_area': avg_crescent_area,
            'average_globule_area': avg_globule_area
        }

# Test the linking module
if __name__ == "__main__":
    # Test basic functionality
    linker = GlobulatorLinker()
    print("Globulator Linker module loaded successfully!")
    print("Available classes:")
    print("- LinkedParticle: Represents linked crescent-globule pairs")
    print("- AmbiguousParticle: Represents unlinked particles")
    print("- GlobulatorLinker: Main linking algorithm")