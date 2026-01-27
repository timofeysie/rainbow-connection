# FreeCAD Instructions: Modifying STEP Files

## Overview
When you open a `.step` file in FreeCAD, it imports as a **Part object** (not Part Design). This means it's a solid body without parametric features, so the editing approach is different.

## Step-by-Step: Selecting and Moving a Face in a STEP File

### Step 1: Open the STEP File
1. Launch **FreeCAD**
2. Go to **File → Open**
3. Navigate to: `python/emoji-os/cases/matrix-3-box-modified.step`
4. Click **Open** and wait for the file to load
5. You should see a single object in the **Model Tree** (usually named "Shape" or similar)

### Step 2: Switch to Part Workbench
1. In the top toolbar, click the workbench dropdown (currently might say "Start" or "Part Design")
2. Select **"Part"** from the list
   - This workbench has tools for working with imported solid geometry

### Step 3: Select the Horizontal Face
1. **Click directly on the light blue horizontal face** in the 3D view
   - Just click on it - no special button needed
   - The face should highlight when you hover/click
   - FreeCAD will automatically detect it's a face

2. **Verify selection:**
   - The face should be highlighted in the 3D view
   - In the **Model Tree**, the main object should be highlighted
   - The **Property Editor** (bottom-left) should show properties for the selected object

### Step 4: Move the Face Down

**Important:** With STEP files (Part objects), you can't directly move individual faces. You have several options:

#### Method 1: Use Part → Cut (Recommended)
This creates a new object with the face moved:

1. **Note the current position:**
   - The face is currently at z=30 (approximately)
   - You want it at z=0

2. **Create a cutting box:**
   - Go to **Part → Create Primitives → Box**
   - In the dialog, set:
     - **Length X:** 200 (larger than your box)
     - **Length Y:** 200 (larger than your box)
     - **Length Z:** 30 (the distance to move down)
     - **Position:** X=0, Y=0, **Z=-30** (negative moves it down)
   - Click **OK**
   - This creates a box that will "cut away" the space above the face

3. **Cut the object:**
   - Select the **original object** (your box) in the Model Tree
   - Hold **Ctrl** and select the **Box** you just created
   - Go to **Part → Boolean → Cut**
   - This removes the material above the face, effectively moving it down

4. **Clean up:**
   - Hide or delete the cutting box
   - The result should have the face at z=0

#### Method 2: Use Part Design (Convert to Parametric)
This converts the STEP to a parametric model:

1. **Switch to Part Design workbench**

2. **Create a body:**
   - Go to **Part Design → Create Body**
   - A new "Body" appears in the tree

3. **Import the shape:**
   - Select the imported STEP object in the tree
   - Go to **Part Design → Create a SubShapeBinder**
   - Or drag the object into the Body

4. **Now you can edit it parametrically:**
   - You can create sketches and features based on the imported geometry
   - This is more complex but gives you full control

#### Method 3: Use Draft Workbench (Simple Translation)
This moves the entire object:

1. **Switch to Draft workbench**

2. **Select the object** in the Model Tree

3. **Move it:**
   - Go to **Draft → Move** (or press **M**)
   - In the dialog:
     - **Base point:** Click on the light blue face (or enter 0,0,30)
     - **Destination point:** Enter **0,0,0** (or click on the bottom rim)
   - Click **OK**
   - **Note:** This moves the ENTIRE object, not just the face

#### Method 4: Manual Geometry Editing (Advanced)
For precise control:

1. **Select the object** in the tree

2. **Go to Part workbench**

3. **Use Part → Refine Shape** to clean up the geometry

4. **Use Part → Boolean operations** to cut/move specific parts

5. This requires understanding the geometry structure

### Step 5: Export the Result
1. **Select the final object** in the Model Tree
2. Go to **File → Export**
3. Choose **"STL Mesh (*.stl)"** for Tinkercad
4. Save as `matrix-3.stl`

## Which Method Should You Use?

- **Method 1 (Cut)** - Best for simple face movement, creates clean result
- **Method 2 (Part Design)** - Best if you want to make multiple parametric changes
- **Method 3 (Draft Move)** - Only if you want to move the entire object
- **Method 4 (Manual)** - For complex geometry modifications

## Troubleshooting

### Problem: Can't select just the face
**Solution:**
- Make sure you're clicking directly on the face, not an edge
- Try zooming in closer
- The face should highlight when you hover

### Problem: The cut operation doesn't work
**Solution:**
- Make sure both objects are selected (original + cutting box)
- Try using **Part → Refine Shape** on the original first
- Check that the cutting box actually overlaps the area you want to remove

### Problem: The geometry looks wrong after cutting
**Solution:**
- Use **Part → Refine Shape** to clean up
- Try adjusting the cutting box size/position
- You may need to use multiple cut operations

## Tips

- **Save frequently:** Use **File → Save** to save as FreeCAD format (.FCStd) so you can edit later
- **Use Undo:** **Ctrl+Z** works if something goes wrong
- **View modes:** Use **View → Draw Style → Wireframe** to see the structure better
- **Measure:** Use **Part → Measure** to check distances and positions

## Quick Reference

**To move face from z=30 to z=0:**
1. Open STEP file
2. Switch to Part workbench
3. Click the light blue face
4. Create a cutting box (Z=30, Position Z=-30)
5. Use Part → Boolean → Cut
6. Export to STL

Good luck!

