#!/usr/bin/env python
import os
from pathlib import Path

def print_directory_structure(startpath, indent=0):
    """Print the directory structure starting from startpath"""
    print(f"{'  ' * indent}📁 {os.path.basename(startpath)}/")
    
    # Sort directories first, then files
    items = sorted(os.listdir(startpath))
    dirs = [item for item in items if os.path.isdir(os.path.join(startpath, item))]
    files = [item for item in items if os.path.isfile(os.path.join(startpath, item))]
    
    # Print directories first
    for d in dirs:
        if d.startswith('.') or d == '__pycache__':  # Skip hidden directories and __pycache__
            continue
        print_directory_structure(os.path.join(startpath, d), indent + 1)
    
    # Then print files
    for f in files:
        if f.startswith('.'):  # Skip hidden files
            continue
        print(f"{'  ' * (indent + 1)}📄 {f}")

if __name__ == "__main__":
    # Path to the templates directory
    templates_dir = Path(__file__).parent / "frontend" / "templates"
    
    if templates_dir.exists():
        print("\n=== Templates Directory Structure ===\n")
        print_directory_structure(templates_dir)
    else:
        print(f"Templates directory not found at {templates_dir}")
        
        # Try alternative location
        alt_templates_dir = Path(__file__).parent / "app" / "templates"
        if alt_templates_dir.exists():
            print(f"Found templates at {alt_templates_dir}")
            print("\n=== Templates Directory Structure ===\n")
            print_directory_structure(alt_templates_dir)
        else:
            print("Could not find templates directory. Please check your project structure.") 