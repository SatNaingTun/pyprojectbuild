import os
import subprocess

def build(project_path, name, version, description):
    """Automatically generates flatpak manifest inside project_path and builds the bundle."""
    print(f"\n==> Building local Flatpak package for {name} v{version} at '{project_path}'...")
    
    # Strictly scoped to project_path
    flatpak_dir = os.path.join(project_path, "flatpak")
    os.makedirs(flatpak_dir, exist_ok=True)

    app_id = f"org.local.{name}"
    manifest_path = os.path.join(flatpak_dir, f"{app_id}.json")
    
    manifest_content = f"""{{
    "app-id": "{app_id}",
    "runtime": "org.freedesktop.Platform",
    "runtime-version": "23.08",
    "sdk": "org.freedesktop.Sdk",
    "command": "{name}.py",
    "finish-args": [
        "--share=ipc",
        "--socket=x11"
    ],
    "modules": [
        {{
            "name": "{name}",
            "buildsystem": "simple",
            "build-commands": [
                "install -D {name}.py /app/bin/{name}.py"
            ],
            "sources": [
                {{
                    "type": "dir",
                    "path": "."
                }}
            ]
        }}
    ]
}}"""
    with open(manifest_path, "w") as f:
        f.write(manifest_content)

    build_dir = "flatpak-build"
    repo_dir = "flatpak-repo"
    
    subprocess.run(["flatpak-builder", "--user", "--install-deps-from=flathub", "--force-clean", build_dir, manifest_path], cwd=project_path, check=True)
    subprocess.run(["flatpak-builder", "--repo=" + repo_dir, "--force-clean", build_dir, manifest_path], cwd=project_path, check=True)
    subprocess.run(["flatpak", "build-bundle", repo_dir, f"{name}.flatpak", app_id], cwd=project_path, check=True)
    print(f"==> Success! Local '{name}.flatpak' bundle generated in '{project_path}'.")