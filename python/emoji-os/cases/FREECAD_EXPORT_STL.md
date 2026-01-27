# FreeCAD: Export to STL for 3D Printing

## Steps to Export Your Cut Object

### Step 1: Select the Object to Export
1. **Click on "Cut"** (or "Cut001") in the Model Tree
   - This is your cube with the hole
   - It should be highlighted in blue
   - Make sure it's the final object you want to print

### Step 2: Export to STL
1. Go to **File → Export**
2. In the file dialog:
   - **File type:** Select **"STL Mesh (*.stl)"** from the dropdown
   - **Navigate to:** `python/emoji-os/cases/` (or wherever you want to save it)
   - **File name:** Enter a name like `matrix-3-bottom.stl`
   - Click **Save**

### Step 3: STL Export Settings
A dialog box will appear with export options:

1. **Tolerance:** Set to **0.1** (or leave default)
   - Lower = higher quality but larger file
   - 0.1 is usually good for 3D printing

2. **Export as binary:** Should be **checked** (usually default)
   - Binary STL files are smaller and load faster

3. **Object to export:** Should show "Cut" or your object name
   - If it shows something else, make sure "Cut" is selected in Model Tree

4. Click **OK**

### Step 4: Verify the Export
1. The file should be saved
2. You can open it in your 3D printing service to verify:
   - The hole should be visible
   - The negative space should be preserved

## Important Notes

### If the Hole Doesn't Appear in the STL
- Make sure the "Cut" object is selected (not the original cubes)
- Check that Cube001 (negative cube) was large enough to cut through
- Try increasing the **Tolerance** to 0.05 for better quality
- Make sure Cube001's **Height** was at least as tall as Cube

### Exporting Multiple Objects
If you have both bottom and top pieces:
1. Export them separately:
   - Select "Cut" (bottom) → Export as `matrix-3-bottom.stl`
   - Select "Cut001" (top) → Export as `matrix-3-top.stl`
2. Or combine them first:
   - Select both Cut objects
   - Part → Boolean → Union
   - Then export the combined result

### File Location
The STL file will be saved where you specify. Common locations:
- `python/emoji-os/cases/matrix-3-bottom.stl`
- Or your desktop/documents folder

## Quick Checklist

- [ ] "Cut" object selected in Model Tree
- [ ] File → Export
- [ ] Selected "STL Mesh (*.stl)" file type
- [ ] Set Tolerance to 0.1
- [ ] Export as binary checked
- [ ] Clicked OK
- [ ] File saved successfully

## Troubleshooting

### Problem: Export dialog doesn't appear
**Solution:**
- Make sure an object is selected in Model Tree
- Try selecting "Cut" again, then File → Export

### Problem: STL file is empty or corrupted
**Solution:**
- Make sure "Cut" is a valid solid (not just faces)
- Try Part → Refine Shape on "Cut" first
- Then export again

### Problem: Hole is filled in the STL
**Solution:**
- The negative cube (Cube001) might not have been large enough
- Recreate with larger Cube001
- Or check that the Cut operation actually worked (rotate view to see hole)

Your STL file should now be ready for 3D printing with the negative space preserved!


