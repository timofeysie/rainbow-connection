#!/usr/bin/env python3
"""
Script to modify STEP file: Move ONLY the horizontal light blue surface down to z=0,
while keeping vertical walls at their current positions.
This is more complex - we need to identify horizontal surfaces vs vertical walls.
"""

import re
import sys
import os

def modify_step_file(input_file, output_file):
    """
    Modify STEP file to move horizontal surface at z=30 down to z=0.
    The challenge is identifying which coordinates belong to horizontal surfaces
    vs vertical walls. We'll use a heuristic: coordinates at z=30 that are part
    of horizontal planes should move, but we need to be careful.
    """
    
    # Read the STEP file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The issue: Moving all z=30 to z=0 extends the vertical posts because
    # the vertical walls have vertices at both z=30 (bottom) and z=36 (top).
    # When we move z=30 to z=0, the walls become 36mm tall instead of 6mm.
    #
    # Solution: Move the entire light blue U-shape structure down as a unit.
    # This means:
    # - Move z=30 (horizontal surface) to z=0
    # - Also move z=36 coordinates that are part of the light blue structure
    #   down to z=6 (maintaining the 6mm wall height)
    #
    # But identifying which z=36 coordinates belong to the light blue structure
    # vs the container top is difficult. Let's try moving z=36 coordinates
    # that are connected to z=30 coordinates in the same face/edge.
    #
    # Actually, a simpler approach: Move z=30 to z=0, and also move z=36
    # coordinates that are "near" the light blue area (based on X,Y coordinates
    # that match the light blue region). But this is complex.
    #
    # Let me try: Move z=30 to z=0, and also move z=36 coordinates that are
    # within the same X,Y bounds as the z=30 coordinates we're moving.
    # This should move the entire U-shape structure down as a unit.
    
    # First pass: collect all X,Y coordinates at z=30 to identify the light blue region
    z30_coords = set()
    pattern_coord = r"CARTESIAN_POINT\('',\((-?\d+\.?\d*),(-?\d+\.?\d*),30\.\)\)"
    for match in re.finditer(pattern_coord, content):
        x = float(match.group(1))
        y = float(match.group(2))
        z30_coords.add((round(x, 1), round(y, 1)))  # Round to avoid floating point issues
    
    print(f"Found {len(z30_coords)} unique X,Y coordinates at z=30")
    
    # Count changes
    changes_made = 0
    z36_moved = 0
    
    def replace_z_in_point(match):
        nonlocal changes_made, z36_moved
        x = match.group(1)
        y = match.group(2)
        z_str = match.group(3)
        
        try:
            z = float(z_str)
            x_float = float(x)
            y_float = float(y)
            coord_key = (round(x_float, 1), round(y_float, 1))
            
            # Move horizontal surface from z=30 to z=0
            if abs(z - 30.0) < 0.01:  # z=30 -> z=0
                changes_made += 1
                return f"CARTESIAN_POINT('',({x},{y},0.))"
            # Also move z=36 coordinates that are in the same X,Y location as z=30
            # This moves the vertical walls down, maintaining their 6mm height
            elif abs(z - 36.0) < 0.01 and coord_key in z30_coords:
                z36_moved += 1
                return f"CARTESIAN_POINT('',({x},{y},6.))"  # Move to z=6 (maintains 6mm height)
            else:
                return match.group(0)  # Keep unchanged
        except ValueError:
            return match.group(0)
    
    # Replace in CARTESIAN_POINT definitions
    pattern = r"CARTESIAN_POINT\('',\((-?\d+\.?\d*),(-?\d+\.?\d*),(-?\d+\.?\d*)\)\)"
    modified_content = re.sub(pattern, replace_z_in_point, content)
    
    # Write the modified content
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print(f"Modified STEP file written to: {output_file}")
    print(f"Made {changes_made} coordinate changes (z=30 -> z=0)")
    print(f"Made {z36_moved} coordinate changes (z=36 -> z=6, maintaining wall height)")
    print(f"Shifted z=30 -> z=0 (horizontal light blue surface)")
    if z36_moved > 0:
        print(f"Shifted corresponding z=36 -> z=6 (vertical walls, maintaining 6mm height)")
    print(f"\nPlease verify in FreeCAD that the light blue surface is flush with bottom")
    print(f"and the vertical walls maintained their height.")

if __name__ == "__main__":
    base_dir = r"C:\Users\timof\repos\timo\rainbow-connection\python\emoji-os\cases"
    input_file = os.path.join(base_dir, "matrix-3-box-modified.step")
    output_file = os.path.join(base_dir, "matrix-3-box-horizontal-only.step")
    
    modify_step_file(input_file, output_file)

