# FreeCAD: Cut Cube001 Out of Cube - Exact Steps

## Steps to Cut the Negative Space

### Step 1: Select the Objects
1. **Click on "Cube"** in the Model Tree (the positive bottom piece)
   - It should highlight in blue
2. **Hold Ctrl** and **click on "Cube001"** (the negative space cube)
   - Both should now be selected (both highlighted in blue)
   - You should see both "Cube" and "Cube001" selected in the Model Tree

### Step 2: Perform the Cut Operation
1. Go to **Part → Boolean → Cut**
   - This is in the Part workbench menu
2. A new object appears in the Model Tree
   - It will be named "Cut" or "Cut001"
   - This is the result: Cube with Cube001 removed

### Step 3: Verify the Result
1. **Click on the "Cut" object** in the Model Tree
2. **Rotate the view** to see the result
3. You should see:
   - The Cube with a hole where Cube001 was
   - The negative space (hole) should be visible

### Step 4: Hide the Original Cubes (Optional)
1. **Right-click "Cube"** in Model Tree
2. Select **"Toggle visibility"** (eye icon) to hide it
3. **Right-click "Cube001"** in Model Tree
4. Select **"Toggle visibility"** to hide it
5. Now you only see the "Cut" result

## Important Notes

- **Selection Order Matters:**
  - First select the object to be cut (Cube)
  - Then select the cutting object (Cube001)
  - The first selected object is what gets cut
  - The second selected object is what cuts it

- **If it doesn't work:**
  - Make sure both objects are selected (both blue in tree)
  - Make sure Cube001 is positioned correctly (inside Cube)
  - Make sure Cube001 is large enough to cut through Cube

## Next Steps

After creating the "Cut" (Cube with hole):
1. You'll use this "Cut" object in the next operation
2. Select your original "Box"
3. Hold Ctrl and select the "Cut" object
4. Part → Boolean → Union (to add it to the bottom of your Box)

But wait - as we discussed, you might want to do it differently to preserve the hole. See the next section.

## Alternative: Better Sequence

Actually, to preserve the hole in the final result:

1. **First:** Box + Cube (positive) → Union (add material)
2. **Then:** Result + Cube001 (negative) → Cut (remove hole)

This way the hole is preserved in the final Box.

But if you just want to create the cube-with-hole first (which you're doing), then:
- Cube + Cube001 → Cut ✓ (you're doing this now)
- Then later: Box + positive cube → Union, then Result + Cube001 → Cut


