# FreeCAD: Moving a Single Surface/Plane

## The Problem
In FreeCAD, you **cannot directly move individual faces** of a solid object. The light blue surface is part of the solid "Box" object, so you can only move the entire box, not just that face.

## Solutions

### Option 1: Use Part → Split (Requires a Cutting Plane)
Split requires a cutting object. Here's how:

1. **Create a cutting plane:**
   - Go to **Part → Create Primitives → Plane**
   - In the Property Editor, set:
     - **Length:** 200 (large enough to cut through your box)
     - **Width:** 200
   - Set **Placement → Position Z:** 30 (at the level of the light blue face)
   - This creates a plane that will slice your box

2. **Split the solid:**
   - **Select your "Box"** in the Model Tree
   - **Hold Ctrl** and select the **Plane**
   - Go to **Part → Split → Slice Apart** (or Slice to Compound)
   - This should create separate objects above and below the plane

3. **Move the separated piece:**
   - Check the Model Tree - you should see new objects
   - Select the piece containing the light blue face
   - Use **Edit → Placement** to move it down (Position Z: -30)

4. **Rejoin if needed:**
   - Select both pieces
   - Use **Part → Boolean → Union** to rejoin them

**Note:** This method is complex and may not work well with your geometry. The Boolean Cut method (Option 3) is more reliable.

### Option 2: Convert to Part Design (Recommended)
Convert the STEP to a parametric model so you can edit the feature that created the face:

1. **Switch to Part Design workbench**

2. **Create a Body:**
   - Go to **Part Design → Create Body**
   - A new "Body" appears in the tree

3. **Import the STEP geometry:**
   - Select your "Box" (STEP object) in the tree
   - Go to **Part Design → Create a SubShapeBinder**
   - Or drag the Box into the Body
   - This makes the geometry available in Part Design

4. **Now you can create features based on it:**
   - Create sketches on the faces
   - Use Pocket to remove material above the face
   - Or modify the geometry parametrically

### Option 3: Boolean Cut (What We've Been Doing)
This doesn't "move" the face, but **removes material above it**, which has the same visual effect:

1. Create a cutting cube positioned to remove material from z=0 to z=30
2. Use **Part → Boolean → Cut**
3. This effectively "moves" the face down by removing the material above it

### Option 4: Manual Geometry Reconstruction
1. **Extract the face as a separate object:**
   - Select the light blue face
   - Go to **Part → Create a Copy → Create a Shape Copy**
   - This creates a copy of just that face

2. **Move the copy:**
   - Select the copied face
   - Use **Edit → Placement** to move it (Position Z: -30)

3. **Recreate the geometry:**
   - You'd need to manually rebuild the rest of the box
   - This is very complex and not recommended

## Best Approach for Your Situation

Since you want to move just the light blue plane with the square void:

**Try Option 1 (Split) first:**
1. Click the light blue face
2. **Part → Split → Slice Apart** (or Slice to Compound)
3. See if it separates the geometry
4. If it works, move the separated piece down
5. Rejoin with Union if needed

**If that doesn't work, use Option 3 (Boolean Cut):**
- This is the most reliable method
- It doesn't actually "move" the face, but removes material above it
- The end result is the same - the face ends up at z=0

## Why You Can't Move Just a Face

In CAD software, solid objects are **topologically connected**. A face is part of the solid's boundary - you can't move it independently without breaking the solid. You need to either:
- Split the solid into pieces
- Use Boolean operations to modify it
- Work parametrically (Part Design) to modify the feature that created it

## The Reality: Boolean Cut is Your Best Option

For STEP files, **you cannot easily separate and move individual faces**. The most reliable method is:

### Use Boolean Cut (Recommended):

1. **Create a cutting cube:**
   - **Part → Primitives → Cube**
   - Set it large enough (200x200x30)
   - Position it at Z: -30 (using Placement)

2. **Cut the material:**
   - Select your "Box"
   - Hold Ctrl and select the "Cube"
   - **Part → Boolean → Cut**
   - This removes material from z=0 to z=30, effectively moving the face down

3. **Result:**
   - The light blue face ends up at z=0
   - The vertical posts remain unchanged
   - This achieves your goal without needing to "move" the face

**This is the standard CAD approach** - you modify geometry by adding/removing material, not by moving individual faces.

