# FreeCAD: Completing the Boolean Operations - Preserving Holes

## The Problem
When you do **Union**, it can fill in holes. You need to use **Cut** operations to preserve the negative spaces.

## Correct Operation Sequence

### For the Bottom Box (with hole):

**Step 1: Create the cube with hole (you've done this)**
- Positive cube + Negative cube → **Part → Boolean → Cut**
- This creates "Cut" (cube with hole) ✓

**Step 2: Add it to the bottom of your Box**
- **DO NOT use Union** - it will fill the hole!
- Instead, use this sequence:
  1. **Select your original "Box"**
  2. **Hold Ctrl** and select the **"Cut"** (the cube with hole)
  3. **Part → Boolean → Union** (this adds the cube)
  4. **BUT** - the hole might get filled

**Better Method - Use Cut to Remove Material:**
1. **Select your original "Box"**
2. **Hold Ctrl** and select the **negative cube** (the one that makes the hole)
3. **Part → Boolean → Cut**
4. This removes the hole area from the Box
5. **Then** select the result
6. **Hold Ctrl** and select the **positive cube** (100x100)
7. **Part → Boolean → Union**
8. This adds material at the bottom while preserving the hole

### Alternative: Do Everything in One Sequence

**Complete Sequence for Bottom:**

1. **Select your original "Box"**
2. **Hold Ctrl** and select the **positive cube** (100x100 at bottom)
3. **Part → Boolean → Union** (adds material at bottom)
4. **Select the result** (should be "Fusion" or "Union")
5. **Hold Ctrl** and select the **negative cube** (hole-sized)
6. **Part → Boolean → Cut** (removes hole, preserving void)
7. **Result:** Box with material added at bottom, hole preserved

### For the Top Box (if you have one):

Follow the same sequence:
1. Box + positive cube → Union (add material)
2. Result + negative cube → Cut (preserve hole)

## Why Union Fills Holes

When you Union two solids:
- If they overlap, the overlapping region becomes solid
- Holes can get "filled in" if the union operation closes them
- **Solution:** Always do the **Cut** (remove hole) operation **AFTER** the Union

## Correct Order of Operations

**For each box (bottom and top):**

1. ✅ **Union first** - Add the positive cube to your Box
2. ✅ **Cut second** - Remove the negative cube (hole) from the result

**NOT:**
- ❌ Cut first, then Union (this can fill the hole)

## Step-by-Step for Your Situation

Since you already have "Cut" (cube with hole) created:

### Option A: Start Over with Correct Sequence
1. **Delete** the "Cut" objects (or hide them)
2. Start fresh:
   - Box + positive cube → **Union**
   - Result + negative cube → **Cut**

### Option B: Work with What You Have
1. You have "Cut" (cube with hole) - that's good
2. **Select your original "Box"**
3. **Hold Ctrl** and select the **positive cube** (100x100)
4. **Part → Boolean → Union**
5. **Select the result**
6. **Hold Ctrl** and select the **negative cube** (hole cube)
7. **Part → Boolean → Cut**
8. This should preserve the hole

## Verifying the Result

1. **Rotate the view** to see inside
2. **Check that the hole is still there:**
   - You should see through the object where the hole is
   - The hole should be visible from both top and bottom
3. **If the hole is filled:**
   - Press **Ctrl+Z** to undo
   - Try the sequence again
   - Make sure the negative cube is large enough (Height: 30 or more)

## Export to STL

Once the holes are preserved:
1. **Select the final result** in Model Tree
2. **File → Export → STL Mesh (*.stl)**
3. **In export dialog:**
   - Set **Tolerance:** 0.1
   - Make sure **"Export as binary"** is checked (usually default)
   - Click **OK**
4. **Open in your 3D printing service** - holes should be visible

## Troubleshooting

### Problem: Hole still fills when exporting
**Solution:**
- Make sure the negative cube **Height** is at least 30 (or larger than the material thickness)
- The negative cube must extend completely through the material
- Try increasing the negative cube height to 50 or more

### Problem: Union still fills the hole
**Solution:**
- Don't Union the cube-with-hole directly
- Instead: Union the positive cube first, then Cut the negative cube
- This preserves the void space

## Quick Reference

**Correct Sequence:**
1. Box + Positive Cube → **Union** (add material)
2. Result + Negative Cube → **Cut** (preserve hole)

**Wrong Sequence:**
1. Positive Cube + Negative Cube → Cut (creates cube with hole)
2. Box + Cube-with-hole → Union ❌ (fills the hole!)

The key is: **Always do the Cut operation LAST** to preserve voids.


