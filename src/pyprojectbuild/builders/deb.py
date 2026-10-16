import datetime
import os
import subprocess
import sys

def build(project_path, name, version, description):
    """Automatically generates debian/ files for standard Python wheel packages and builds them."""
    print(f"\n==> Building Debian (.deb) package (via Python Wheel) for {name} v{version} at '{project_path}'...")
    
    debian_dir = os.path.join(project_path, "debian")
    source_dir = os.path.join(debian_dir, "source")
    os.makedirs(source_dir, exist_ok=True)

    changelog_path = os.path.join(debian_dir, "changelog")
    control_path = os.path.join(debian_dir, "control")
    format_path = os.path.join(source_dir, "format")
    rules_path = os.path.join(debian_dir, "rules")
    install_path = os.path.join(debian_dir, "install")  # Stale file cleanup

    # Remove existing files completely (including any old install config)
    for path in [changelog_path, control_path, format_path, rules_path, install_path]:
        if os.path.exists(path):
            os.remove(path)

    # 1. Changelog
    now = datetime.datetime.now(datetime.timezone.utc).astimezone()
    date_str = now.strftime("%a, %d %b %Y %H:%M:%S %z")
    changelog_content = (
        f"{name} ({version}-1) unstable; urgency=medium\n\n"
        f"  * Automated wheel-based build of {name} v{version}.\n\n"
        f" -- Local Developer <dev@local.com>  {date_str}\n"
    )
    with open(changelog_path, "w") as f:
        f.write(changelog_content)
    os.chmod(changelog_path, 0o644)

    # 2. Control
    with open(control_path, "w") as f:
        f.write(f"""Source: {name}
Section: python
Priority: optional
Maintainer: Local Developer <dev@local.com>
Build-Depends: debhelper-compat (= 13),
               dh-python,
               python3-all,
               python3-setuptools,
               python3-build,
               python3-installer,
               python3-wheel
Standards-Version: 4.6.1

Package: {name}
Architecture: all
Depends: ${{python3:Depends}}, ${{misc:Depends}}
Description: {description}
""")
    os.chmod(control_path, 0o644)

    # 3. Source Format
    with open(format_path, "w") as f:
        f.write("3.0 (quilt)\n")
    os.chmod(format_path, 0o644)

    # 4. Rules (Standard pybuild - wheel manages installation automatically)
    rules_content = """#!/usr/bin/make -f
%:
\tdh $@ --buildsystem=pybuild
"""
    with open(rules_path, "w") as f:
        f.write(rules_content)
    os.chmod(rules_path, 0o755)

    # Sanitize environment to prevent .venv pollution during system packaging
    clean_env = os.environ.copy()
    clean_env.pop("VIRTUAL_ENV", None)
    clean_env.pop("PYTHONPATH", None)
    
    path_dirs = clean_env.get("PATH", "").split(os.pathsep)
    clean_env["PATH"] = os.pathsep.join([d for d in path_dirs if ".venv" not in d])

    # Run build package command with sanitized environment
    try:
        subprocess.run(
            ["dpkg-buildpackage", "-us", "-uc", "-b"], 
            cwd=project_path, 
            check=True, 
            text=True, 
            capture_output=True,
            env=clean_env
        )
        print(f"==> Success! Wheel-based .deb package generated for '{name}'.")
    except subprocess.CalledProcessError as e:
        print("\n[ERROR] dpkg-buildpackage failed with exit code:", e.returncode)
        print("--- STDOUT ---")
        print(e.stdout)
        print("--- STDERR ---")
        print(e.stderr)
        sys.exit(1)