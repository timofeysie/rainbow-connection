# FreeCAD Menu Options for Moving STEP File Geometry

## Important: Draft is a Workbench, Not a Menu

**Draft** is a **workbench** (like Part Design), not a menu item. You need to **switch workbenches** first.

## Method 1: Edit → Placement (Works in Any Workbench)

This moves the **entire object**, not just a face:

1. **Select the object** ("Box" in your Model Tree)
2. Go to **Edit → Placement...**
3. In the Placement dialog:
   - Set **Position Z** to move it down (e.g., -30)
   - Or use **Translation** with Z: -30
   - Click **OK**

**Note:** This moves the ENTIRE box, not just the face.

## Method 2: Part Workbench → Boolean → Cut (Best for Moving Just a Face)

This is the recommended method to move just the face:

1. **Switch to Part workbench:**
   - Click the workbench dropdown (currently says "Part Design")
   - Select **"Part"** from the list

2. **Create a cutting box:**
   - Go to **Part → Create Primitives → Box**
   - Set dimensions to cut the area above the face
   - Position it to remove material above z=30

3. **Cut the material:**
   - Select your "Box" object
   - Hold **Ctrl** and select the cutting box
   - Go to **Part → Boolean → Cut**

## Method 3: Draft Workbench (For Moving Entire Object)

1. **Switch to Draft workbench:**
   - Click the workbench dropdown
   - Select **"Draft"** from the list

2. **Move the object:**
   - Select "Box" in the tree
   - Go to **Draft → Move** (or press **M**)
   - Set base point and destination

## Quick Reference: Menu Paths

### For Entire Object:
- **Edit → Placement...** (any workbench)

### For Moving Just a Face (STEP file):
1. Switch to **Part** workbench
2. **Part → Create Primitives → Box** (create cutter)
3. **Part → Boolean → Cut** (remove material)

### For Draft Move:
1. Switch to **Draft** workbench  
2. **Draft → Move**

## Your Current Situation

Since you're in **Part Design** workbench and have a STEP file imported as "Box":
- Use **Edit → Placement...** to move the entire object, OR
- Switch to **Part** workbench and use **Part → Boolean → Cut** to move just the face

The **Edit → Placement...** option is the simplest and works right now without switching workbenches!

