# FreeCAD: Creating a Notched Void Using Boolean Operations

## Understanding the Notch

From your screenshot, the notch appears to be a **triangular cutout** in the corner of the inner opening. To create this using Boolean operations, you'll create a triangular prism and cut it out.

## Method 1: Using a Wedge (Triangular Prism)

### Step 1: Create a Wedge Primitive
1. **Part → Primitives → Wedge**
   - A wedge is a triangular prism - perfect for creating notches
2. **Select the Wedge** in Model Tree
3. In **Property Editor → Data tab**, set:
   - **Xmin:** 0
   - **Xmax:** [notch width] (e.g., 5 or 10 mm)
   - **Ymin:** 0
   - **Ymax:** [notch depth] (e.g., 5 or 10 mm)
   - **Zmin:** 0
   - **Zmax:** [notch height] (e.g., 30 mm - tall enough to cut through)
   - **X2max:** [notch width] (same as Xmax for triangular shape)
   - **Y2max:** [notch depth] (same as Ymax for triangular shape)

### Step 2: Position the Wedge
1. **Placement → Position:**
   - Click **"..."** next to Placement
   - Set **Position X, Y, Z** to position the wedge at the corner where you want the notch
   - The notch appears to be at the top-left corner of the opening
   - You may need to rotate it: Set **Rotation** if needed
   - Click **OK**

### Step 3: Cut the Notch
1. **Select your main object** (the Box or Fusion result)
2. **Hold Ctrl** and select the **Wedge**
3. **Part → Boolean → Cut**
4. The notch is now cut out!

## Method 2: Using a Cube and Rotating It

If Wedge doesn't work or you want more control:

### Step 1: Create a Cube
1. **Part → Primitives → Cube**
2. **Select the Cube** in Model Tree
3. Set dimensions:
   - **Length:** [notch size] (e.g., 10 mm)
   - **Width:** [notch size] (e.g., 10 mm)
   - **Height:** 30 (tall enough to cut through)

### Step 2: Position and Rotate
1. **Placement → Position:**
   - Position it at the corner where the notch should be
2. **Placement → Rotation:**
   - Rotate it 45 degrees if needed to create the triangular notch
   - Or use **Part → Create Primitives → Cone** with a small angle

### Step 3: Cut the Notch
1. Select your main object
2. Hold Ctrl and select the Cube
3. **Part → Boolean → Cut**

## Method 3: Create a Custom Shape Using Sketches (More Precise)

For exact control over the notch shape:

### Step 1: Create a Sketch
1. **Switch to Part Design workbench**
2. **Select the face** where you want the notch
3. **Part Design → Create Sketch**
4. Draw a triangle:
   - Use the **Polyline** tool
   - Draw three lines forming a triangle
   - Constrain the dimensions
5. **Close** the sketch

### Step 2: Create a Pocket
1. With the sketch selected, **Part Design → Pocket**
2. Set **Length** to cut through the material
3. This creates the notch

### Step 3: Export
1. Select the final object
2. **File → Export → STL**

## Finding the Notch Position

To position the notch correctly:

1. **Measure the opening:**
   - Use **Part → Measure** tool
   - Click on the corners of the opening
   - Note the X, Y coordinates

2. **Position the wedge/cube:**
   - Set Placement Position X, Y to match the corner
   - The notch appears to be at the **top-left corner** of the opening

## Quick Reference: Wedge Properties

For a triangular notch at a corner:
- **Xmin:** 0
- **Xmax:** [notch width] (e.g., 5 mm)
- **Ymin:** 0  
- **Ymax:** [notch depth] (e.g., 5 mm)
- **Zmin:** 0
- **Zmax:** 30 (height to cut through)
- **X2max:** Same as Xmax (creates triangle)
- **Y2max:** Same as Ymax (creates triangle)

**Placement Position:** Set to the corner coordinates where you want the notch

## About "Length 2: 100 mm"

In Part Design, "Length 2" is a property of Pad features:
- It's the **second length** when using "Two dimensions" type
- It controls how far the pad extends in a second direction
- For your notch, you probably don't need to worry about this - it's a Part Design feature property, not relevant to Boolean operations

## Recommended Approach

**Use Method 1 (Wedge):**
1. It's designed for triangular shapes
2. Easier to position
3. Works well with Boolean operations
4. Quick to create

**Steps:**
1. Part → Primitives → Wedge
2. Set dimensions (Xmax, Ymax, Zmax, X2max, Y2max)
3. Position at corner using Placement
4. Select main object + Wedge → Part → Boolean → Cut
5. Export to STL

The notch should now be cut out of your model!

