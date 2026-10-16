import os
import subprocess

def build(project_path, name, version, description):
    """Automatically generates snap/ configurations inside project_path and builds the package."""
    print(f"\n==> Building local Snap (.snap) package for {name} v{version} at '{project_path}'...")
    
    # Strictly scoped to project_path
    snap_dir = os.path.join(project_path, "snap")
    os.makedirs(snap_dir, exist_ok=True)
    
    snapcraft_yaml = f"""name: {name}
base: core24
version: '{version}'
summary: {description}
grade: stable
confinement: classic

apps:
  {name}:
    command: bin/{name}.py

parts:
  {name}:
    plugin: nil
    override-build: |
      mkdir -p $CRAFT_PART_INSTALL/bin
      cp {name}.py $CRAFT_PART_INSTALL/bin/
      chmod +x $CRAFT_PART_INSTALL/bin/{name}.py
"""
    with open(os.path.join(snap_dir, "snapcraft.yaml"), "w") as f:
        f.write(snapcraft_yaml)

    subprocess.run(["snapcraft", "--destructive-mode"], cwd=project_path, check=True)
    print(f"==> Success! .snap package generated in '{project_path}'.")