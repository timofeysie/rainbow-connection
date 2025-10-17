# Virtual Environment (venv) Management Guide

## What is a Virtual Environment?

A virtual environment is an isolated Python environment that allows you to install packages without affecting your system Python installation. This prevents conflicts between different projects that might need different versions of the same packages.

## Your Current Setup

Your project uses a virtual environment located at:

```sh
.venv/
```

The Python interpreter is at:

```sh
.venv/Scripts/python.exe
```

## Basic Commands

### Activating the Virtual Environment

**Windows (PowerShell/Command Prompt):**

```bash
.venv\Scripts\activate
```

**Windows (Git Bash):**

```bash
source .venv/Scripts/activate
```

**Linux/Mac:**

```bash
source .venv/bin/activate
```

When activated, your prompt will show `(.venv)` at the beginning.

### Deactivating the Virtual Environment

```bash
deactivate
```

### Running Scripts with the Virtual Environment

**Option 1: Activate first, then run**

```bash
.venv\Scripts\activate
python python/emoji-os/emoji-os-zero.py
```

**Option 2: Run directly with venv Python (recommended)**

```bash
.venv\Scripts\python.exe python/emoji-os/emoji-os-zero.py
```

## Package Management

### Installing Packages

```bash
# Activate venv first
.venv\Scripts\activate

# Install packages
pip install package-name

# Or install from requirements file
pip install -r requirements.txt
```

### Creating Requirements File

```bash
# Generate requirements.txt from current environment
pip freeze > requirements.txt
```

### Installing from Requirements File

```bash
pip install -r requirements.txt
```

## Current Project Dependencies

Your project currently has these packages installed:
- `pillow` (PIL) - For image processing and tkinter integration

## Managing the Virtual Environment

### Checking Installed Packages

```bash
.venv\Scripts\activate
pip list
```

### Upgrading Packages

```bash
.venv\Scripts\activate
pip install --upgrade package-name
```

### Removing Packages

```bash
.venv\Scripts\activate
pip uninstall package-name
```

### Recreating the Environment

If you need to recreate the environment:

```bash
# Remove old environment
rmdir /s .venv

# Create new environment
python -m venv .venv

# Activate and install packages
.venv\Scripts\activate
pip install pillow
```

## IDE Integration

### VS Code/Cursor

1. Open Command Palette (`Ctrl+Shift+P`)
2. Type "Python: Select Interpreter"
3. Choose `.venv\Scripts\python.exe`

### PyCharm

1. Go to File → Settings → Project → Python Interpreter
2. Click gear icon → Add
3. Select "Existing Environment"
4. Browse to `.venv\Scripts\python.exe`

## Best Practices

1. **Always activate the venv** before installing packages
2. **Commit requirements.txt** to version control
3. **Don't commit the .venv folder** (add to .gitignore)
4. **Use descriptive names** for requirements files if you have multiple environments

## Troubleshooting

### "Python not found" errors

- Make sure you're using the full path: `.venv\Scripts\python.exe`
- Check that the virtual environment was created successfully

### Package installation fails

- Ensure the virtual environment is activated
- Try upgrading pip: `python -m pip install --upgrade pip`

### Import errors

- Verify packages are installed: `pip list`
- Check that you're using the correct Python interpreter

## Project-Specific Notes

### Running Emoji OS Scripts

```bash
# Run the main emoji OS script
.venv\Scripts\python.exe python/emoji-os/emoji-os-zero.py

# Run other scripts
.venv\Scripts\python.exe python/zero/smiley-matrix-controller.py
```

### Adding New Dependencies

If you add new Python packages to your project:

1. Install them in the virtual environment
2. Update requirements.txt: `pip freeze > requirements.txt`
3. Commit the updated requirements.txt

## Environment Variables

If you need environment variables, create a `.env` file in your project root:

```bash
# .env file
PYTHONPATH=.
DEBUG=True
```

Then install python-dotenv:

```bash
pip install python-dotenv
```

And load it in your Python scripts:

```python
from dotenv import load_dotenv
load_dotenv()
```
