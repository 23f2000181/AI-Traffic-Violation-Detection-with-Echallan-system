# Installation Instructions for Virtual Environment

## The Issue
You're running the backend from your `venv` virtual environment, but `flask-cors` needs to be installed in that environment.

## Solution

Run this command from your venv:

```bash
# Make sure you're in the venv (you should see (venv) in your prompt)
pip install flask-cors
```

## Complete Setup for Virtual Environment

If you want to ensure all dependencies are installed in your venv:

```bash
# Activate venv (if not already activated)
# You should already be in it based on your prompt

# Install all required packages
pip install flask-cors
```

## Then Start the Backend

```bash
# From D:\Codes\Miniproj\backend
python app.py
```

## Alternative: Use the Batch Script

The batch script I created (`start_backend.bat`) runs from the project root, which might use the global Python. If you prefer to use your venv, run the commands manually as shown above.

## Quick Commands

```bash
# In D:\Codes\Miniproj\backend with venv activated
pip install flask-cors
python app.py
```

That should resolve the ModuleNotFoundError!
