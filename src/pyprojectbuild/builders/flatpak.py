import json
import os
import subprocess
import sys
from pyprojectbuild.utils import get_project_metadata

def build(project_path, name, version, description):
    _, _, _, script_file, _ = get_project_metadata(project_path)
    print(f"\n==> Building Flatpak package for {name} v{version} using entry point '{script_file}'...")

    manifest_path = os.path.join(project_path, f"{name}.json")
    manifest_data = {
        "app-id": f"org.local.{name}",
        "runtime": "org.freedesktop.Platform",
        "runtime-version": "23.08",
        "sdk": "org.freedesktop.Sdk",
        "command": name,
        "finish-args": ["--share=network", "--share=ipc", "--socket=x11"],
        "modules": [{
            "name": name,
            "buildsystem": "simple",
            "build-commands": [
                f"install -D {script_file} /app/bin/{name}",
                f"chmod +x /app/bin/{name}"
            ],
            "sources": [{"type": "dir", "path": "."}]
        }]
    }

    with open(manifest_path, "w") as f:
        json.dump(manifest_data, f, indent=4)
    os.chmod(manifest_path, 0o644)

    build_dir = os.path.join(project_path, ".flatpak-builder-dir")
    clean_env = os.environ.copy()
    clean_env.pop("VIRTUAL_ENV", None)
    clean_env.pop("PYTHONPATH", None)

    subprocess.run(["flatpak", "remote-add", "--if-not-exists", "--user", "flathub", "https://dl.flathub.org/repo/flathub.flatpakrepo"], check=False, env=clean_env)

    try:
        subprocess.run(["flatpak-builder", "--user", "--install-deps-from=flathub", "--force-clean", build_dir, manifest_path], cwd=project_path, check=True, env=clean_env)
        print(f"\n==> Success! Flatpak package built successfully for '{name}'.")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] flatpak-builder failed with exit code: {e.returncode}")
        sys.exit(1)