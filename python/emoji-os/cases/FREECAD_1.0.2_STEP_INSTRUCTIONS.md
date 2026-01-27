# FreeCAD 1.0.2: Moving Face in STEP File - Exact Steps

## Problem
STEP files import as **Part objects**, not **Part Design Bodies**. Part Design features (like Subtractive Box) require an active Body, so they're disabled.

## Solution: Use Part Workbench

### Step 1: Switch to Part Workbench
1. Click the **workbench dropdown** (currently says "Part Design")
2. Select **"Part"** from the list
3. The toolbar will change to show Part workbench tools

### Step 2: Create a Cutting Box
1. Go to **Part → Create Primitives → Box**
   - This menu option exists in Part workbench (not Part Design)
2. In the dialog that appears, set:
   - **Length X:** 200 (larger than your box width)
   - **Length Y:** 200 (larger than your box depth)
   - **Length Z:** 30 (the distance to move the face down)
   - **Position X:** -100 (to center it)
   - **Position Y:** -100 (to center it)
   - **Position Z:** -30 (this positions it to cut the area above the face)
3. Click **OK**
4. A new "Box" object appears in the Model Tree

### Step 3: Cut the Material
1. **Select your original "Box"** (the STEP file object) in the Model Tree
2. **Hold Ctrl** and click the **cutting box** you just created
3. Both should be selected (highlighted in blue)
4. Go to **Part → Boolean → Cut**
5. A new "Cut" object appears in the tree
6. This removes the material above the face, effectively moving it down

### Step 4: Hide/Delete the Cutting Box
1. Right-click the cutting "Box" in the Model Tree
2. Select **"Toggle visibility"** to hide it
3. Or right-click → **Delete** to remove it

### Step 5: Verify and Export
1. The "Cut" object should show your box with the face moved down
2. Select the "Cut" object
3. Go to **File → Export → STL Mesh (*.stl)**
4. Save as `matrix-3.stl`

## Alternative: Convert to Part Design Body (More Complex)

If you want to use Part Design features:

### Step 1: Create a Body
1. Switch to **Part Design** workbench
2. Go to **Part Design → Create Body**
3. A new "Body" appears in the tree

### Step 2: Import the Shape
1. Select your "Box" (STEP object) in the tree
2. Go to **Part Design → Create a SubShapeBinder**
   - Or drag the Box into the Body
3. This makes the STEP geometry available in Part Design

### Step 3: Use Subtractive Features
1. Make sure the **Body** is active (click it in tree)
2. Now **Part Design → Create Subtractive Primitive → Subtractive Box** should be enabled
3. Create a subtractive box to cut the material

## Quick Reference: Menu Paths for FreeCAD 1.0.2

### Part Workbench (Recommended for STEP files):
- **Part → Create Primitives → Box** ✓
- **Part → Boolean → Cut** ✓

### Part Design Workbench:
- **Part Design → Create Subtractive Primitive** ✗ (disabled for STEP files)
- **Part Design → Create Subtractive Feature → Pocket** ✓ (but requires Body)

## Why Part Design Features Are Disabled

- STEP files import as **Part objects** (solid geometry)
- Part Design features require a **Body** (parametric container)
- You need to either:
  1. Use **Part workbench** (simpler), OR
  2. Create a **Body** and import the STEP geometry into it

## Recommended Approach

**Use Part Workbench:**
1. Switch to Part workbench
2. Part → Create Primitives → Box
3. Part → Boolean → Cut

This is the simplest and most direct method for STEP files in FreeCAD 1.0.2.

