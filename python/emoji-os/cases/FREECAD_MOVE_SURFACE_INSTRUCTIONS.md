# FreeCAD Instructions: Move Horizontal Light Blue Surface to Bottom

## Overview
These instructions will help you move only the horizontal light blue surface (the base of the U-shape) down to be flush with the bottom of the container, without moving the vertical posts/shafts.

## Step-by-Step Instructions

### Step 1: Open the File
1. Launch **FreeCAD**
2. Go to **File → Open**
3. Navigate to: `python/emoji-os/cases/matrix-3-box-modified.step`
4. Click **Open** and wait for the file to load

### Step 2: Switch to Part Workbench
1. In the top toolbar, click the dropdown that says "Start" (or your current workbench)
2. Select **"Part"** from the workbench list
   - This gives you access to Part tools for working with solid geometry

### Step 3: Select the Horizontal Surface

1. **Rotate the view** to see the inside of the box:
   - Hold **middle mouse button** and drag to rotate
   - Or use the view cube in the top-right corner
   - Rotate so you can see the light blue horizontal surface inside (the purple recessed area)

2. **Enable Face Selection Mode:**
   - Look at the **status bar** at the bottom of the FreeCAD window
   - You should see selection filter buttons/icons
   - Click the button that shows a **square/face icon** (this enables face selection)
   - OR look in the toolbar for a button with a face/square icon
   - The button might be labeled or have a tooltip when you hover over it
   - **Alternative:** Simply **click directly on the face** - FreeCAD will auto-detect it's a face

3. **Select the light blue horizontal surface:**
   - **Click directly on the light blue horizontal face** you see in the purple recessed area
   - The face should highlight when you hover over it (it's already light blue in your screenshot)
   - **Click once** to select it
   - The selected face should change color or show a selection highlight

4. **Verify selection:**
   - Look at the **Model Tree** (left panel) - the selected object/face should be highlighted
   - Check the **Property Editor** (bottom-left) - it should show properties for the selected face
   - The face should remain highlighted in the 3D view
   - If you see "Pad002" or another feature selected in the tree, you may need to click the face again

### Step 4: Move the Surface Down

**Important:** For STEP files imported into FreeCAD, you need to use Boolean operations to modify geometry. The face is at approximately z=30, and you want it at z=0.

**Method 1: Use Part Workbench - Boolean Cut (Recommended for STEP files)**

1. **Switch to Part Workbench:**
   - Click the workbench dropdown (currently "Part Design")
   - Select **"Part"** from the list

2. **Create a Cutting Cube:**
   - Go to **Part → Primitives → Cube**
   - **A dialog may appear** - if it does, you can set dimensions there:
     - **Length:** 200
     - **Width:** 200
     - **Height:** 30
     - Click **Create** or **OK**
   - If no dialog appears, a cube is created with default size
   - The cube appears in the Model Tree as "Cube" or "Cube001"
   - It may appear inside the hole initially - that's okay, we'll position it

3. **Position and Size the Cube to Cut Material Above the Face:**
   - **Select the Cube** in the Model Tree
   - In the **Property Editor** (bottom-left), click the **"Data"** tab (not "View" tab)
   - Look for these properties (they might be named slightly differently):
     - **Length:** Set to 200 (larger than your box, e.g., 200 mm)
     - **Width:** Set to 200 (larger than your box, e.g., 200 mm)  
     - **Height:** Set to 30 (the distance to move the face down, e.g., 30 mm)
   - OR if you see:
     - **X Length:** Set to 200
     - **Y Length:** Set to 200
     - **Z Length:** Set to 30
   - Find **"Placement"** property and click the **"..."** button (or the small button with three dots)
   - In the Placement dialog:
     - **Position X:** -100 (to center it, or adjust based on your box position)
     - **Position Y:** -100 (to center it, or adjust based on your box position)
     - **Position Z:** -30 (this positions the cube to cut the area above z=0, removing material from z=0 to z=30)
     - Click **OK**
   - The cube should now be positioned to cut the material above your face
   
   **Note:** If you don't see Length/Width/Height properties, the cube might have been created with default size. Try:
   - **Right-click the Cube** in the Model Tree
   - Select **"Transform"** or look for dimension properties
   - Or delete the cube and create it again, this time a dialog might appear where you can set dimensions

4. **Cut the Material:**
   - **Select your original "Box"** (the STEP file object) in the Model Tree
   - **Hold Ctrl** and click the **Cube** you just created
   - Both should be selected (highlighted in blue)
   - Go to **Part → Boolean → Cut**
   - A new "Cut" object appears in the tree
   - This removes the material above the face, effectively moving it down to z=0

5. **Hide the Cutting Cube:**
   - Right-click the "Cube" in the Model Tree
   - Select **"Toggle visibility"** to hide it (or delete it)
   - You should now see your box with the face moved down

**Method 2: Modify Pad Feature (For Part Design .FCStd files only)**

If you're working with the original .FCStd file (not STEP), you can modify the Pad:

1. **Find the feature that created the face:**
   - In the **Model Tree**, click different Pad features (Pad002, Pad003, Pad008, etc.)
   - Watch which one highlights your light blue face
   - **Select that Pad feature** in the tree

2. **Edit the Pad Length:**
   - With the Pad selected, in **Property Editor**:
     - Find **"Length"** under "Pad" section
     - **Decrease it** to move the face down (e.g., subtract 30mm)
   - OR edit the **Sketch** that the Pad is based on:
     - Double-click the Sketch in the tree
     - Move the geometry down
     - Click **"Close"** when done

### Step 5: Verify the Result
1. **Check the geometry:**
   - Rotate the view to see the result
   - The light blue horizontal surface should now be flush with the bottom rim
   - The vertical posts should remain at their original positions (not extended)

2. **If the cut didn't work correctly:**
   - Press **Ctrl+Z** to undo
   - Adjust the cube position/size in the Placement dialog
   - Make sure the cube's Z position is set to -30 and Length Z is 30
   - Try again with Part → Boolean → Cut

### Step 6: Export to STL (When Satisfied)
1. **Select the Cut object:**
   - In the **Model Tree**, click on the **"Cut"** object (the result of the Boolean operation)
   - This should be the final modified geometry

2. **Export:**
   - Go to **File → Export**
   - Choose **"STL Mesh (*.stl)"** from the file type dropdown
   - Navigate to: `python/emoji-os/cases/`
   - Name it: `matrix-3.stl`
   - Click **Save**

3. **In the export dialog:**
   - Set **Tolerance:** 0.1 (or leave default)
   - Click **OK**

## Troubleshooting

### Problem: Can't select just the face
**Solution:**
- Make sure you're in **Face Selection Mode** (View → Selection → Select Face)
- Try zooming in closer to the surface
- Use **Ctrl+Click** to cycle through overlapping selections

### Problem: The cube appears inside the hole
**Solution:**
- This is normal! The cube will be positioned correctly using the Placement dialog
- Set Placement → Position Z to -30 to position it below the face
- The cube should extend from z=-30 to z=0, cutting the material above the face

### Problem: The cut doesn't remove the right material
**Solution:**
- Check the cube's **Length Z** is 30 (the distance to move)
- Check the cube's **Position Z** is -30 (to position it correctly)
- Make sure the cube is large enough (Length X and Y should be 200 or larger)
- Try using **Part → Refine Shape** on the original Box first, then cut

### Problem: The vertical posts still extend
**Solution:**
- The Boolean Cut should only remove material above the face
- If posts are still wrong, the cube positioning might need adjustment
- Try adjusting the cube's Position X and Y to better align with your box

### Problem: FreeCAD crashes or becomes slow
**Solution:**
- The STEP file is complex - be patient
- Try working with a simpler view (hide other parts)
- Use **View → Draw Style → Wireframe** to reduce rendering load

## Tips

- **Use the View Cube:** The 3D navigation cube in the top-right helps orient the view
- **Zoom:** Use mouse wheel or **View → Zoom** to get closer to the surface
- **Selection Modes:** Toggle between different selection modes (Face, Edge, Vertex) in View menu
- **Undo/Redo:** **Ctrl+Z** and **Ctrl+Y** work as expected
- **Save frequently:** Use **File → Save** or **File → Save As** to save your work as a FreeCAD file (.FCStd)

## Alternative: Use Part Design Workbench

If the above methods don't work well, you can try:

1. Switch to **Part Design** workbench
2. Select the object
3. Use **Part Design → Move Object** or similar transformation tools
4. This workbench has more advanced parametric modeling features

## Final Notes

- The goal is to move the **horizontal surface only** from z=30 to z=0
- The vertical posts should **not** extend downward
- If you need to adjust the vertical walls separately, you may need to select and move them individually
- FreeCAD's geometry can be complex - don't hesitate to undo and try again

Good luck! Let me know if you need clarification on any step.

