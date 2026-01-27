#!/usr/bin/env python3
"""
Script to modify STEP file: Move middle layer (z=30, z=34.5) to top (z=36),
making them flush with the container top.
"""

import re
import sys
import os

def modify_step_file(input_file, output_file):
    """
    Modify STEP file to move middle layer features to top (z=36).
    """
    
    # Read the STEP file
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Move z=30 and z=34.5 to z=36 (flush with top)
    modified_lines = []
    changes_made = 0
    
    for line in lines:
        original_line = line
        
        # Pattern to match CARTESIAN_POINT with three coordinates
        def replace_z_in_point(match):
            nonlocal changes_made
            x = match.group(1)
            y = match.group(2)
            z_str = match.group(3)
            
            try:
                z = float(z_str)
                
                # Move middle layer Z values to top (z=36)
                if abs(z - 30.0) < 0.01:  # z=30 -> z=36 (light blue middle face)
                    changes_made += 1
                    return f"CARTESIAN_POINT('',({x},{y},36.))"
                elif abs(z - 34.5) < 0.01:  # z=34.5 -> z=36 (upper step)
                    changes_made += 1
                    return f"CARTESIAN_POINT('',({x},{y},36.))"
                else:
                    return match.group(0)  # Keep unchanged
            except ValueError:
                return match.group(0)
        
        # Replace in CARTESIAN_POINT definitions
        pattern = r"CARTESIAN_POINT\('',\((-?\d+\.?\d*),(-?\d+\.?\d*),(-?\d+\.?\d*)\)\)"
        line = re.sub(pattern, replace_z_in_point, line)
        
        modified_lines.append(line)
    
    # Write the modified content
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(modified_lines)
    
    print(f"Modified STEP file written to: {output_file}")
    print(f"Made {changes_made} coordinate changes")
    print(f"Shifted z=30 -> z=36 (light blue middle face - now flush with top)")
    print(f"Shifted z=34.5 -> z=36 (upper step - now flush with top)")
    print(f"Bottom remains at z=0")
    print(f"\nWARNING: Please verify the geometry in FreeCAD.")
    print(f"STEP file modifications can sometimes break topology.")

if __name__ == "__main__":
    base_dir = r"C:\Users\timof\repos\timo\rainbow-connection\python\emoji-os\cases"
    input_file = os.path.join(base_dir, "matrix-3-box-modified.step")
    output_file = os.path.join(base_dir, "matrix-3-box-top-flush.step")
    
    modify_step_file(input_file, output_file)

