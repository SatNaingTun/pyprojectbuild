import argparse
import os
from pyprojectbuild.publishers import ppa
from pyprojectbuild.builders import deb, snap, mac, win, flatpak
from pyprojectbuild.utils import get_project_metadata

def main():
    parser = argparse.ArgumentParser(description="Multi-platform Python project packager and publisher.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Make path optional (defaults to current working directory if omitted)
    for action in ["deb", "snap", "mac", "win", "flatpak", "ppa", "all"]:
        sub = subparsers.add_parser(action, help=f"Execute {action} package operation")
        sub.add_argument(
            "path", 
            nargs="?", 
            default=".", 
            help="Path to the target project directory (default: current working directory)"
        )

    args = parser.parse_args()
    project_path = os.path.abspath(args.path)

    name, version, description, _, _ = get_project_metadata(project_path)
    print(f"==> Project: {name} v{version}")

    if args.command == "deb":
        deb.build_local(project_path, name, version, description)
    elif args.command == "ppa":
        ppa.publish_ppa(project_path)
    elif args.command == "snap":
        snap.build(project_path, name, version, description)
    elif args.command == "mac":
        mac.build(project_path, name, version, description)
    elif args.command == "win":
        win.build(project_path, name, version, description)
    elif args.command == "flatpak":
        flatpak.build(project_path, name, version, description)
    elif args.command == "all":
        print("==> Running standard local build pipeline...")
        deb.build_local(project_path, name, version, description)
        snap.build(project_path, name, version, description)
        mac.build(project_path, name, version, description)
        win.build(project_path, name, version, description)
        print("\n==> Standard build artifacts generated successfully!")

if __name__ == "__main__":
    main()