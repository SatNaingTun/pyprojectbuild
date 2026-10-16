import os
import subprocess
import sys

def build(project_path, name, version, description):
    """Automatically detects the target script and builds the Snap package."""
    print(f"\n==> Building Snap (.snap) package for {name} v{version} at '{project_path}'...")

    snap_dir = os.path.join(project_path, "snap")
    os.makedirs(snap_dir, exist_ok=True)

    yaml_path = os.path.join(snap_dir, "snapcraft.yaml")

    # Intelligently locate the actual script file in the project folder
    script_file = None
    for candidate in [f"{name}.py", f"{name}", "main.py", "cli.py"]:
        if os.path.exists(os.path.join(project_path, candidate)):
            script_file = candidate
            break
    
    if not script_file:
        # Fallback: find any .py file in the root directory
        py_files = [f for f in os.listdir(project_path) if f.endswith(".py") and f not in ["setup.py", "conftest.py"]]
        if py_files:
            script_file = py_files[0]
        else:
            script_file = f"{name}.py"

    print(f"==> Detected script entry point: {script_file}")

    yaml_content = f"""name: {name}
base: core22
version: '{version}'
summary: {description}
description: |
  {description}
grade: stable
confinement: classic

apps:
  {name}:
    command: bin/{name}

parts:
  {name}:
    plugin: nil
    source: .
    override-build: |
      mkdir -p $CRAFT_PART_INSTALL/bin
      cp {script_file} $CRAFT_PART_INSTALL/bin/{name}
      chmod +x $CRAFT_PART_INSTALL/bin/{name}
"""
    with open(yaml_path, "w") as f:
        f.write(yaml_content)
    os.chmod(yaml_path, 0o644)

    # Sanitize environment to prevent .venv pollution
    clean_env = os.environ.copy()
    clean_env.pop("VIRTUAL_ENV", None)
    clean_env.pop("PYTHONPATH", None)
    
    path_dirs = clean_env.get("PATH", "").split(os.pathsep)
    clean_env["PATH"] = os.pathsep.join([d for d in path_dirs if ".venv" not in d])

    # Run snapcraft with destructive mode
    try:
        subprocess.run(
            ["snapcraft", "--destructive-mode"], 
            cwd=project_path, 
            check=True, 
            text=True, 
            capture_output=True,
            env=clean_env
        )
        print(f"==> Success! Snap package generated for '{name}'.")
    except subprocess.CalledProcessError as e:
        print("\n[ERROR] snapcraft failed with exit code:", e.returncode)
        print("--- STDOUT ---")
        print(e.stdout)
        print("--- STDERR ---")
        print(e.stderr)
        sys.exit(1)