import os
import subprocess
import sys
from pyprojectbuild.utils import get_project_metadata

def build(project_path, name, version, description):
    _, _, _, script_file, _ = get_project_metadata(project_path)
    print(f"\n==> Building Snap (.snap) package for {name} v{version} using entry point '{script_file}'...")

    snap_dir = os.path.join(project_path, "snap")
    os.makedirs(snap_dir, exist_ok=True)
    yaml_path = os.path.join(snap_dir, "snapcraft.yaml")

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

    clean_env = os.environ.copy()
    clean_env.pop("VIRTUAL_ENV", None)
    clean_env.pop("PYTHONPATH", None)
    path_dirs = clean_env.get("PATH", "").split(os.pathsep)
    clean_env["PATH"] = os.pathsep.join([d for d in path_dirs if ".venv" not in d])

    try:
        subprocess.run(["snapcraft", "--destructive-mode"], cwd=project_path, check=True, env=clean_env)
        print(f"==> Success! Snap package generated for '{name}'.")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] snapcraft failed with exit code: {e.returncode}")
        sys.exit(1)