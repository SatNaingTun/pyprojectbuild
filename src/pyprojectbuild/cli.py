import argparse
import os
from pyprojectbuild.builders import deb, snap, mac, win, flatpak
from pyprojectbuild.utils import get_project_metadata

def main():
    parser = argparse.ArgumentParser(description="Multi-platform Python project packager.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    builder_names = ["deb", "snap", "mac", "win", "flatpak", "all"]
    for builder_name in builder_names:
        sub_parser = subparsers.add_parser(builder_name, help=f"Build {builder_name} package(s)")
        sub_parser.add_argument("path", help="Path to the target project directory")

    args = parser.parse_args()
    project_path = os.path.abspath(args.path)

    # Automatically parse project metadata and entry point from pyproject.toml
    name, version, description, script_file, entry_func = get_project_metadata(project_path)
    print(f"==> Target Project: {name} (v{version})")
    print(f"==> Entry Point File: {script_file} (Function: {entry_func})")

    if args.command == "deb":
        deb.build(project_path, name, version, description)
    elif args.command == "snap":
        snap.build(project_path, name, version, description)
    elif args.command == "mac":
        mac.build(project_path, name, version, description)
    elif args.command == "win":
        win.build(project_path, name, version, description)
    elif args.command == "flatpak":
        flatpak.build(project_path, name, version, description)
    elif args.command == "all":
        print("==> Running standard build pipeline (Debian, Snap, Mac, Windows, Flatpak)")
        deb.build(project_path, name, version, description)
        snap.build(project_path, name, version, description)
        mac.build(project_path, name, version, description)
        win.build(project_path, name, version, description)
        flatpak.build(project_path, name, version, description)
        print("\n==> Standard multi-platform build assets generated successfully!")

if __name__ == "__main__":
    main()