# FreeCAD: Moving Plane Using Positive and Negative Cubes

## Your Approach
1. Create a positive cube (100x100) at the bottom - this adds material
2. Create a negative cube matching the rectangular hole - this preserves the hole
3. Use Boolean operations to combine them

## Step-by-Step Instructions

### Step 1: Create Positive Cube at Bottom
1. **Part → Primitives → Cube**
2. **Select the Cube** in Model Tree
3. In **Property Editor → Data tab**, set:
   - **Length:** 100
   - **Width:** 100
   - **Height:** 30 (the distance to move the plane down)
4. **Placement → Position:**
   - Click **"..."** next to Placement
   - Set **Position Z:** -30 (or 0, depending on where you want it)
   - Click **OK**
5. This cube will add material at the bottom

### Step 2: Measure the Rectangular Hole
You need to know the exact size and position of the hole in the light blue plane:

1. **Click on the light blue face** to select it
2. Use **Part → Measure** tool to measure the hole dimensions
3. Or visually estimate:
   - The hole appears to be roughly square/rectangular
   - Note its approximate size (e.g., 20x20, 30x30, etc.)
   - Note its position relative to the center

### Step 3: Create Negative Cube (Subtractive) for the Hole
1. **Part → Primitives → Cube**
2. **Select this new Cube** in Model Tree
3. In **Property Editor → Data tab**, set:
   - **Length:** [hole width] (e.g., 20 if hole is 20mm wide)
   - **Width:** [hole depth] (e.g., 20 if hole is 20mm deep)
   - **Height:** 30 (same as positive cube, or slightly larger)
4. **Placement → Position:**
   - Click **"..."** next to Placement
   - Set **Position X:** [hole X position] (to align with hole center)
   - Set **Position Y:** [hole Y position] (to align with hole center)
   - Set **Position Z:** -30 (same as positive cube)
   - Click **OK**

### Step 4: Combine Everything with Boolean Operations

**Option A: Add Positive, Then Subtract Negative**
1. **Select your original "Box"**
2. **Hold Ctrl** and select the **positive cube** (100x100)
3. **Part → Boolean → Union** (or Fuse)
4. This adds the cube to the bottom
5. **Select the result** (should be "Fusion" or "Union")
6. **Hold Ctrl** and select the **negative cube** (hole-sized)
7. **Part → Boolean → Cut**
8. This removes the hole area, preserving the void

**Option B: Create Compound, Then Cut**
1. **Select the positive cube** (100x100)
2. **Hold Ctrl** and select the **negative cube** (hole-sized)
3. **Part → Boolean → Cut** (this creates a cube with a hole)
4. **Select your original "Box"**
5. **Hold Ctrl** and select the **result** (the cube with hole)
6. **Part → Boolean → Union**
7. This combines them

### Step 5: Clean Up
1. **Hide or delete** the original cubes:
   - Right-click each cube in Model Tree
   - Select **"Toggle visibility"** or **"Delete"**
2. **Check the result:**
   - The light blue plane should now be at the bottom
   - The rectangular hole should be preserved

## Tips

### Finding Hole Dimensions
If you can't measure easily:
1. **Click the light blue face**
2. Look at **Property Editor** - it might show face dimensions
3. Or use **Part → Measure** tool:
   - Click two opposite corners of the hole
   - It will show the distance

### Positioning the Negative Cube
- The hole is likely centered on the light blue plane
- If the plane is centered at (0,0,30), the hole might be at (0,0,30)
- Adjust Position X and Y to match the hole's center

### Alternative: Use Pocket Instead
If the hole is a standard shape:
1. Create the positive cube and union it
2. Create a **Sketch** on the light blue face
3. Draw a rectangle matching the hole
4. Use **Part Design → Pocket** to cut the hole
   - (But this requires Part Design workbench and a Body)

## Quick Reference

**Positive Cube:**
- Size: 100 x 100 x 30
- Position Z: -30 (or 0)

**Negative Cube:**
- Size: [hole width] x [hole depth] x 30
- Position: Aligned with hole center
- Position Z: -30 (same as positive)

**Boolean Operations:**
1. Box + Positive Cube = Union
2. Result - Negative Cube = Cut

This approach effectively "moves" the plane down while preserving the hole!

