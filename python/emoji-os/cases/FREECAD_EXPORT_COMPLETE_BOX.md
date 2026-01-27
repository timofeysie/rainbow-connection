# FreeCAD: Export Complete Box to STL

## The Goal
Export the **entire box** (original Box + bottom piece + top piece if you have one) as one STL file for 3D printing.

## Complete Workflow

### Step 1: Combine Everything Together

You need to combine:
- Your original **"Box"** (the STEP file)
- The **"Cut"** object (bottom piece with hole)
- Any other pieces you've created

**Method: Use Boolean Union**

1. **Select your original "Box"** in the Model Tree
2. **Hold Ctrl** and select **"Cut"** (your bottom piece with hole)
3. If you have a top piece, **Hold Ctrl** and select that too
4. Go to **Part → Boolean → Union** (or Fuse)
5. A new object appears: **"Fusion"** or **"Union"** or **"Fusion001"**
   - This is your complete box!

### Step 2: Verify the Complete Box

1. **Click on "Fusion"** (or "Union") in the Model Tree
2. **Rotate the view** to inspect:
   - The original box should be there
   - The bottom piece should be attached
   - The hole should be visible
   - Everything should be one solid object

### Step 3: Export the Complete Box

1. **Select "Fusion"** (or "Union") in the Model Tree
2. Go to **File → Export**
3. Select **"STL Mesh (*.stl)"**
4. Save as `matrix-3-complete.stl` (or your preferred name)
5. In export dialog:
   - **Tolerance:** 0.1
   - **Export as binary:** checked
   - Click **OK**

## Important: Preserving the Hole

If you're adding the bottom piece to the original Box:

**The hole might get filled when you Union!**

To preserve the hole:

### Option A: Cut the Hole After Union
1. Box + Cut (bottom piece) → **Union** (combine them)
2. Select the result
3. Hold Ctrl and select the **negative cube** (Cube001 - the hole cube)
4. **Part → Boolean → Cut** (this removes the hole area)
5. Export this final result

### Option B: Use the Correct Sequence
1. **Box + positive cube** (100x100) → **Union** (add material at bottom)
2. **Result + negative cube** (Cube001) → **Cut** (remove hole)
3. Export this result

## If You Have Both Bottom and Top Pieces

1. **Select "Box"**
2. **Hold Ctrl** and select **"Cut"** (bottom)
3. **Hold Ctrl** and select **"Cut001"** (top, if you have it)
4. **Part → Boolean → Union**
5. This combines everything
6. **Then** select the result
7. **Hold Ctrl** and select the **negative cubes** (Cube001, Cube002, etc.)
8. **Part → Boolean → Cut** (to preserve all holes)
9. Export the final result

## Quick Checklist

- [ ] Original "Box" selected
- [ ] "Cut" (bottom piece) selected
- [ ] Any other pieces selected
- [ ] Part → Boolean → Union (combine them)
- [ ] Verify "Fusion" object looks correct
- [ ] If holes are filled, do Cut operation with negative cubes
- [ ] Select final combined object
- [ ] File → Export → STL
- [ ] Verify STL file has all parts and holes

## Troubleshooting

### Problem: Hole disappears after Union
**Solution:**
- Do the Cut operation AFTER Union
- Select the Fusion result
- Hold Ctrl and select the negative cube(s)
- Part → Boolean → Cut

### Problem: Parts don't join correctly
**Solution:**
- Make sure the pieces are positioned correctly
- Check that they overlap where they should join
- Use Part → Refine Shape on the Fusion object

### Problem: STL file is too large
**Solution:**
- Increase Tolerance to 0.2 or 0.3
- This reduces file size but also reduces quality slightly

Your complete box should now be ready for 3D printing!


