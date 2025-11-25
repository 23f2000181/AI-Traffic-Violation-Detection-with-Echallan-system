# URGENT: Fix Required for central_detection_manager.py

## Problem
The code you added has indentation issues. The methods are not properly indented to be part of the CentralDetectionManager class.

## What Needs to be Fixed

### Issue 1: detect_triple_riding method (line ~464)
The method definition needs proper indentation (4 spaces for class methods).

**Current (WRONG):**
```python
    def detect_triple_riding(self, image_path, image):
    """
```

**Should be:**
```python
    def detect_triple_riding(self, image_path, image):
        """
```

### Issue 2: is_person_on_motorbike method (line ~533)
This method is completely outside the class! It needs to be indented to be part of CentralDetectionManager.

**Current (WRONG):**
```python
def is_person_on_motorbike(self, person_bbox, motorbike_bbox):
    """
```

**Should be:**
```python
    def is_person_on_motorbike(self, person_bbox, motorbike_bbox):
        """
```

## Quick Fix Steps

1. Open `central_detection_manager.py`
2. Find line ~464 where `detect_triple_riding` starts
3. Make sure the docstring `"""` on the next line has 8 spaces (2 indents)
4. Find line ~533 where `is_person_on_motorbike` starts  
5. Add 4 spaces before `def` to make it a class method
6. Add 4 more spaces to all lines inside that method

## Or Use This Clean Version

I can provide you with a completely clean, working version of the file if these manual fixes are too tedious. Just let me know!

## Test After Fixing

After fixing the indentation:
1. Save the file
2. Run: `python central_detection_manager.py`
3. It should load without IndentationError
4. Then restart your backend

The triple riding detection logic itself is correct - it's just the indentation that's wrong!
