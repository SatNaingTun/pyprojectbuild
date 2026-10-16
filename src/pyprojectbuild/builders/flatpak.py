import json
import os
import subprocess
import sys
from pyprojectbuild.utils import get_project_metadata

def build(project_path, name, version, description):
    _, _, _, script_file, _ = get_project_metadata(project_path)
    print(f"\n==> Building Flatpak package for {name} v{version} using entry point '{script_file}'...")

    manifest_path = os.path.join(project_path, f"{name}.json")
    app_id = f"org.local.{name}"

    manifest_data = {
        "app-id": app_id,
        "runtime": "org.freedesktop.Platform",
        "runtime-version": "23.08",
        "sdk": "org.freedesktop.Sdk",
        "command": name,
        "finish-args": [
            "--share=network",
            "--share=ipc",
            "--socket=x11"
        ],
        "modules": [
            {
                "name": name,
                "buildsystem": "simple",
                "build-commands": [
                    f"install -D {script_file} /app/bin/{name}",
                    f"chmod +x /app/bin/{name}"
                ],
                "sources": [
                    {
                        "type": "dir",
                        "path": "."
                    }
                ]
            }
        ]
    }

    with open(manifest_path, "w") as f:
        json.dump(manifest_data, f, indent=4)
    os.chmod(manifest_path, 0o644)

    build_dir = os.path.join(project_path, ".flatpak-builder-dir")
    repo_dir = os.path.join(build_dir, "repo")
    bundle_path = os.path.join(project_path, f"{name}.flatpak")

    clean_env = os.environ.copy()
    clean_env.pop("VIRTUAL_ENV", None)
    clean_env.pop("PYTHONPATH", None)

    # Ensure flathub repository is added
    subprocess.run(
        ["flatpak", "remote-add", "--if-not-exists", "--user", "flathub", "https://dl.flathub.org/repo/flathub.flatpakrepo"],
        check=False,
        env=clean_env
    )

    try:
        # Build and export to the explicit repo directory
        print("==> Running flatpak-builder...")
        subprocess.run(
            [
                "flatpak-builder",
                "--user",
                "--install-deps-from=flathub",
                "--force-clean",
                f"--repo={repo_dir}",
                build_dir,
                manifest_path
            ],
            cwd=project_path,
            check=True,
            env=clean_env
        )
        
        # Generate the standalone .flatpak bundle in the project root
        if os.path.exists(repo_dir):
            print(f"==> Exporting standalone bundle to {bundle_path}...")
            subprocess.run(
                ["flatpak", "build-bundle", repo_dir, bundle_path, app_id],
                cwd=project_path,
                check=True,
                env=clean_env
            )
            print(f"==> Success! Flatpak bundle generated: {bundle_path}")
        else:
            print(f"\n==> Success! Flatpak package built and installed for '{name}'.")

    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] flatpak-builder/bundle failed with exit code: {e.returncode}")
        sys.exit(1)