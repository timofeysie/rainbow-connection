# FreeCAD Cube Properties - Finding the Right Settings

## Where to Find Cube Dimensions

When you create a Cube in FreeCAD Part workbench, the properties might be in different places:

### Method 1: Check the "Data" Tab
1. **Select the Cube** in the Model Tree
2. In the **Property Editor** (bottom-left), make sure you're on the **"Data"** tab (not "View" tab)
3. Look for properties like:
   - **Length** (or X Length)
   - **Width** (or Y Length)
   - **Height** (or Z Length)

### Method 2: Right-Click Menu
1. **Right-click the Cube** in the Model Tree
2. Look for options like:
   - **"Transform"** - opens a dialog to move/scale
   - **"Edit"** - might open properties
   - **"Properties"** - shows all properties

### Method 3: Recreate with Dialog
1. **Delete the current Cube** (right-click → Delete)
2. Go to **Part → Primitives → Cube** again
3. This time, **a dialog should appear** before creating the cube
4. Set dimensions in the dialog:
   - **Length:** 200
   - **Width:** 200
   - **Height:** 30
   - **Position X:** -100
   - **Position Y:** -100
   - **Position Z:** -30
5. Click **Create** or **OK**

### Method 4: Use Placement to Position
Even if you can't find Length/Width/Height properties, you can still position it:

1. **Select the Cube** in Model Tree
2. In Property Editor → **Data** tab
3. Find **"Placement"** property
4. Click the **"..."** button (or small button next to it)
5. In Placement dialog:
   - Set **Position Z:** -30
   - You can also use **Rotation** if needed
   - Click **OK**

## Alternative: Create Box Instead
If Cube doesn't work well:

1. Go to **Part → Create Primitives → Box**
2. Set dimensions in the dialog that appears
3. This might give you more control

## Quick Check List
- [ ] Selected Cube in Model Tree?
- [ ] Clicked "Data" tab (not "View" tab) in Property Editor?
- [ ] Looked for "Length", "Width", "Height" properties?
- [ ] Tried right-clicking Cube for Transform/Edit options?
- [ ] Checked Placement property for positioning?

## If Still Can't Find Properties
The cube might be using default dimensions. You can:
1. Use **Placement** to position it correctly (Position Z: -30)
2. The size might be fine if it's large enough to cut the material
3. Try the Boolean Cut operation - it might work even with default cube size

