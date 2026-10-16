import os
import sys

try:
    import tomllib
except ImportError:
    try:
        import toml as tomllib
    except ImportError:
        print("Error: Please install 'toml' package (`pip install toml`) or use Python 3.11+")
        sys.exit(1)

def parse_pyproject(project_path="."):
    """Reads project details directly from pyproject.toml at the given project path[cite: 1]."""
    pyproject_file = os.path.join(project_path, "pyproject.toml")
    if not os.path.exists(pyproject_file):
        print(f"Error: pyproject.toml not found in '{project_path}'[cite: 1].")
        sys.exit(1)
        
    with open(pyproject_file, "rb") as f:
        data = tomllib.load(f)
        
    proj = data.get("project", {})
    name = proj.get("name")
    version = proj.get("version")
    description = proj.get("description", "No description provided.")
    
    if not name or not version:
        print("Error: 'name' and 'version' must be specified in [project] section of pyproject.toml.")
        sys.exit(1)
        
    return name, version, description