# FreeCAD Face Selection - Quick Guide

## How to Select a Face in FreeCAD 1.0.2

### Simple Method (Just Click!)
1. **Click directly on the light blue horizontal face** in the 3D view
   - No special button needed - just click on the face
   - FreeCAD will automatically detect it's a face
   - The face should highlight when you hover/click

2. **Verify it's selected:**
   - The face should change color or show a highlight
   - Check the **Model Tree** (left panel) - a feature should be highlighted
   - Check the **Property Editor** (bottom-left) - it should show properties

### Finding Selection Filters (If Needed)
- Look at the **status bar** at the very bottom of the FreeCAD window
- You might see small icon buttons for different selection modes
- One of them should be a **square/face icon** - click it to enable face-only selection
- But usually you don't need this - just clicking the face works!

## Important: You're in Part Design Workbench

Since you're working with a **Part Design** model (I can see Pad002, Sketch003, etc. in your tree), you need to modify the **feature** that created the face, not just move the face itself.

### Step-by-Step for Your Model:

1. **Click on the light blue face** in the 3D view
   - This will select it and highlight the corresponding feature in the Model Tree

2. **Look at the Model Tree** (left panel):
   - One of the Pad features should now be highlighted (probably Pad002, Pad003, or Pad008)
   - This is the feature that created that face

3. **Select that Pad feature** in the Model Tree:
   - Click on it in the tree (e.g., "Pad002")

4. **Look at the Property Editor** (bottom-left):
   - You should see properties like "Length", "Length2", etc.
   - These control how far the Pad extends

5. **To move the face down:**
   - **Option A:** Change the **"Length"** value (decrease it to move the face down)
   - **Option B:** Edit the **Sketch** that the Pad is based on:
     - Find the Sketch in the tree (e.g., "Sketch003", "Sketch004")
     - **Double-click the Sketch** to edit it
     - Move the geometry in the sketch down
     - Click **"Close"** when done

6. **Or use Placement:**
   - With the Pad feature selected, find **"Placement"** in Property Editor
   - Click the **"..."** button next to Placement
   - Set **Position Z** to move it down (e.g., -30)
   - Click **OK**

## Which Pad Feature Creates the Light Blue Face?

To find out which Pad feature created your light blue face:

1. Click on different **Pad** features in the Model Tree (Pad002, Pad003, Pad008, etc.)
2. Watch the 3D view - the face that highlights is the one created by that Pad
3. When you click the Pad that highlights your light blue face, that's the one to modify!

## Quick Test:
- Click **Pad002** in the tree → Does it highlight the light blue face? If yes, modify Pad002.
- Click **Pad003** in the tree → Does it highlight the light blue face? If yes, modify Pad003.
- And so on...

Once you find the right Pad feature, modify its Length or edit its Sketch to move the face down to z=0.

