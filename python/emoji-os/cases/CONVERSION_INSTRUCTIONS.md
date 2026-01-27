# Converting STEP to Tinkercad-Compatible Format

The modified STEP file needs to be converted to a format Tinkercad supports (STL or 3MF).

## Option 1: FreeCAD (Recommended - if you have it installed)

Since the original file was created in FreeCAD, you likely have it installed.

### Method A: Using FreeCAD GUI
1. Open FreeCAD
2. File → Open → Select `matrix-3-box-modified.step`
3. File → Export → Choose either:
   - **STL** format (`.stl`) - Most compatible
   - **3MF** format (`.3mf`) - Better for 3D printing
4. Save as `matrix-3.stl` or `matrix-3.3mf` in the same directory

### Method B: Using Command Line (if FreeCAD is installed)
```powershell
cd "C:\Users\timof\repos\timo\rainbow-connection\python\emoji-os\cases"
"C:\Program Files\FreeCAD\bin\FreeCAD.exe" -c convert_step_to_stl.py
```

## Option 2: Online Converters

If you don't have FreeCAD, use an online converter:

1. **CloudConvert** (https://cloudconvert.com/step-to-stl)
   - Upload `matrix-3-box-modified.step`
   - Convert to STL or 3MF
   - Download the converted file

2. **AnyConv** (https://anyconv.com/step-to-stl-converter/)
   - Similar process

## Option 3: Other CAD Software

- **Fusion 360** (free for personal use)
- **Onshape** (free cloud CAD)
- **Blender** (with STEP import addon)

## File Locations

- **Source STEP file**: `python/emoji-os/cases/matrix-3-box-modified.step`
- **Target 3MF file**: `python/emoji-os/cases/matrix-3.3mf`
- **Target STL file**: `python/emoji-os/cases/matrix-3.stl`

