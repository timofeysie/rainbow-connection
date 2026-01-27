#!/usr/bin/env python3
"""
FreeCAD script to convert STEP file to STL format for Tinkercad.
This script should be run with FreeCAD's Python interpreter.

Usage (if FreeCAD is installed):
    "C:\Program Files\FreeCAD 1.0\bin\FreeCAD.exe" -c convert_step_to_stl.py

Or run from FreeCAD's Python console:
    exec(open('convert_step_to_stl.py').read())
"""

import FreeCAD
import Part
import Mesh
import sys
import os

# File paths - adjust these if needed
# When running with -c flag, __file__ may not be defined, so use absolute paths
base_dir = r"C:\Users\timof\repos\timo\rainbow-connection\python\emoji-os\cases"
input_file = os.path.join(base_dir, "matrix-3-box-modified.step")
output_file = os.path.join(base_dir, "matrix-3.stl")

try:
    # Open the STEP file
    print(f"Opening STEP file: {input_file}")
    doc = FreeCAD.openDocument(input_file)
    
    # Get all objects in the document
    objects = doc.Objects
    
    if not objects:
        print("Error: No objects found in STEP file")
        sys.exit(1)
    
    # Create a compound of all objects
    shapes = []
    for obj in objects:
        if hasattr(obj, 'Shape') and obj.Shape:
            shapes.append(obj.Shape)
    
    if not shapes:
        print("Error: No shapes found in objects")
        sys.exit(1)
    
    # Combine all shapes into a compound
    if len(shapes) == 1:
        compound = shapes[0]
    else:
        compound = Part.makeCompound(shapes)
    
    # Convert to mesh
    print("Converting to mesh...")
    mesh = compound.tessellate(0.1)  # 0.1mm tolerance
    
    # Create mesh object
    mesh_obj = Mesh.Mesh()
    mesh_obj.addFacets(mesh[0], mesh[1])
    
    # Export to STL
    print(f"Exporting to STL: {output_file}")
    mesh_obj.write(output_file)
    
    print(f"✓ Successfully converted to: {output_file}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

