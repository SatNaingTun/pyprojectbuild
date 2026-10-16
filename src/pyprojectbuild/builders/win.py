import os
import subprocess
import sys

def build(project_path, name):
    """Builds a standalone executable using PyInstaller directly inside project_path."""
    print(f"\n==> Building standalone executable for {name} via PyInstaller at '{project_path}'...")
    
    script_path = os.path.join(project_path, f"{name}.py")
    if not os.path.exists(script_path):
        print(f"Error: Main script '{script_path}' not found.")
        sys.exit(1)

    # Executed within the external project path context
    subprocess.run([sys.executable, "-m", "PyInstaller", "--onefile", f"{name}.py"], cwd=project_path, check=True)
    print(f"==> Success! Executable created in '{os.path.join(project_path, 'dist')}' folder.")