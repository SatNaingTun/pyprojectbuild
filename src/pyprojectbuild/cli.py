import argparse
import os
from pyprojectbuild.project_parser import parse_pyproject
from pyprojectbuild.builders import deb, snap, flatpak, exe

def main():
    VALID_TARGETS = ["deb", "snap", "flatpak", "exe", "all"]

    parser = argparse.ArgumentParser(
        description="pyprojectbuild: Zero-config local multi-platform packager for Python projects."
    )
    parser.add_argument(
        "arg1", 
        nargs="?", 
        default="all", 
        help="Target (deb, snap, flatpak, exe, all) or project path."
    )
    parser.add_argument(
        "arg2", 
        nargs="?", 
        default=None, 
        help="Project path if arg1 is a target."
    )
    args = parser.parse_args()

    if args.arg1 in VALID_TARGETS:
        target = args.arg1
        path_input = args.arg2 if args.arg2 else "."
    else:
        target = "all"
        path_input = args.arg1

    project_path = os.path.abspath(path_input)
    name, version, description = parse_pyproject(project_path)
    
    print(f"==> Target Project: {name} (v{version})")
    print(f"==> Project Path:   {project_path}")
    print(f"==> Build Target:   {target}")

    if target in ["deb", "all"]:
        deb.build(project_path, name, version, description)
    
    if target in ["snap", "all"]:
        snap.build(project_path, name, version, description)

    if target in ["flatpak", "all"]:
        flatpak.build(project_path, name, version, description)

    if target in ["exe", "all"]:
        exe.build(project_path, name)

    print("\n==> Build process completed successfully!")

if __name__ == "__main__":
    main()