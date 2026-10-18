import datetime
import os
import re
import subprocess
import sys
from pyprojectbuild.utils import get_project_metadata

REQUIRED_SECRETS = {
    "SIGNING_KEY_ID": "Enter your GPG Signing Key ID (e.g., 8ABC1234XYZ): ",
    "DEB_EMAIL": "Enter your Debian/Ubuntu Email: ",
    "DEB_FULLNAME": "Enter your Full Name: ",
    "PPA_TARGET": "Enter your PPA Target (e.g., ppa:satnaingtun/ppa): "
}

def setup_secrets_file(project_path):
    """Checks if .secrets exists in the target project path and contains all required keys."""
    secrets_file = os.path.join(project_path, ".secrets")
    secrets = {}
    if os.path.exists(secrets_file):
        with open(secrets_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    secrets[k.strip()] = v.strip("\"'")

    missing = [k for k in REQUIRED_SECRETS if not secrets.get(k)]
    
    if missing:
        print(f"==> Missing or incomplete publishing credentials in '{secrets_file}'. Let's set them up.")
        print("These will be saved locally so you only have to enter them once.\n")
        
        for key, prompt in REQUIRED_SECRETS.items():
            if not secrets.get(key):
                val = input(prompt).strip()
                if not val:
                    print(f"Error: '{key}' cannot be empty.")
                    sys.exit(1)
                secrets[key] = val
        
        with open(secrets_file, "w") as f:
            for key in REQUIRED_SECRETS:
                f.write(f'{key}="{secrets[key]}"\n')
        print(f"==> Successfully updated '{secrets_file}'!\n")

def load_secrets_file(project_path):
    """Loads environment variables from the local .secrets file inside the target project."""
    setup_secrets_file(project_path)
    secrets_file = os.path.join(project_path, ".secrets")
    with open(secrets_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip("\"'")

def get_gitignore_patterns(project_path):
    patterns = [".git", ".secrets", "debian"]
    gitignore_path = os.path.join(project_path, ".gitignore")
    essential_files = {"pyproject.toml", "README.md", "LICENSE"}

    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    clean = line.rstrip("/")
                    if clean in essential_files:
                        continue
                    if clean and clean not in patterns:
                        patterns.append(clean)

    for forced in [".venv", "venv", "__pycache__", ".pytest_cache", "build", "dist", ".pybuild"]:
        if forced not in patterns:
            patterns.append(forced)

    return patterns

def parse_pyproject_dependencies(project_path):
    """Dynamically parses build and runtime dependencies from pyproject.toml."""
    pyproject_path = os.path.join(project_path, "pyproject.toml")
    
    build_deps = [
        "debhelper-compat (= 13)",
        "dh-python",
        "pybuild-plugin-pyproject",
        "python3",
        "python3-dev",
        "python3-build",
        "python3-wheel"
    ]
    runtime_deps = ["python3 (>= 3.8)"]

    if os.path.exists(pyproject_path):
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f) if 'tomllib' in globals() else {} # fallback handled or via standard parsing

    return ", ".join(build_deps), ", ".join(runtime_deps)

def generate_debian_files(project_path, pkg_name, repo_url, version, description, script_file):
    debian_dir = os.path.join(project_path, "debian")
    os.makedirs(debian_dir, exist_ok=True)

    for stale in ["install", "control", "rules", "copyright", "compat"]:
        stale_path = os.path.join(debian_dir, stale)
        if os.path.exists(stale_path):
            os.remove(stale_path)

    deb_fullname = os.getenv("DEB_FULLNAME", "Maintainer")
    deb_email = os.getenv("DEB_EMAIL", "maintainer@example.com")

    build_deps = "debhelper-compat (= 13), dh-python, pybuild-plugin-pyproject, python3, python3-dev, python3-build, python3-wheel"

    control_content = f"""Source: {pkg_name}
Section: utils
Priority: optional
Maintainer: {deb_fullname} <{deb_email}>
Build-Depends: {build_deps}
Standards-Version: 4.6.1
Homepage: {repo_url}

Package: {pkg_name}
Architecture: all
Depends: ${{shlibs:Depends}}, ${{misc:Depends}}, python3 (>= 3.8)
Description: {description}
"""
    with open(os.path.join(debian_dir, "control"), "w") as f:
        f.write(control_content)

    os.makedirs(os.path.join(debian_dir, "source"), exist_ok=True)
    with open(os.path.join(debian_dir, "source", "format"), "w") as f:
        f.write("3.0 (quilt)\n")

    ignore_patterns = get_gitignore_patterns(project_path)
    escaped_patterns = []
    for p in ignore_patterns:
        clean = p.rstrip("/")
        if not clean:
            continue
        if clean.endswith("/*"):
            base = clean[:-2]
            escaped_patterns.append(re.escape(base) + r"/.*")
        elif "*" in clean:
            rx = clean.replace(".", r"\.").replace("*", ".*")
            escaped_patterns.append(rx)
        else:
            escaped_patterns.append(re.escape(clean))

    if escaped_patterns:
        pattern_group = "|".join(escaped_patterns)
        regex_str = f"(^|/)({pattern_group})(/|$)"
        options_content = f'extend-diff-ignore = "{regex_str}"\n'
    else:
        options_content = ""

    with open(os.path.join(debian_dir, "source", "options"), "w") as f:
        f.write(options_content)

    current_year = datetime.datetime.now().year
    copyright_content = f"""Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: {pkg_name}
Source: {repo_url}
Files: *
Copyright: {current_year} {deb_fullname} <{deb_email}>
License: MIT
"""
    with open(os.path.join(debian_dir, "copyright"), "w") as f:
        f.write(copyright_content)

    rules_content = "#!/usr/bin/make -f\n%:\n\tdh $@ --buildsystem=pybuild\n"
    rules_path = os.path.join(debian_dir, "rules")
    with open(rules_path, "w") as f:
        f.write(rules_content)
    os.chmod(rules_path, 0o755)

    with open(os.path.join(debian_dir, "install"), "w") as f:
        f.write(f"{script_file} usr/bin/{pkg_name}\n")

def update_changelog(project_path, pkg_name, version, series, message):
    changelog_path = os.path.join(project_path, "debian", "changelog")
    now = datetime.datetime.now(datetime.timezone.utc).astimezone()
    date_str = now.strftime("%a, %d %b %Y %H:%M:%S %z")
    deb_fullname = os.getenv("DEB_FULLNAME", "Maintainer")
    deb_email = os.getenv("DEB_EMAIL", "maintainer@example.com")

    entry = f"{pkg_name} ({version}) {series}; urgency=medium\n\n  * {message}\n\n -- {deb_fullname} <{deb_email}>  {date_str}\n\n"
    existing = ""
    if os.path.exists(changelog_path):
        with open(changelog_path, "r") as f:
            existing = f.read()

    with open(changelog_path, "w") as f:
        f.write(entry + existing)

def publish_ppa(project_path):
    load_secrets_file(project_path)
    KEY_ID = os.getenv("SIGNING_KEY_ID")
    DEB_EMAIL = os.getenv("DEB_EMAIL")
    DEB_FULLNAME = os.getenv("DEB_FULLNAME")
    PPA_TARGET = os.getenv("PPA_TARGET")

    if not KEY_ID or not DEB_EMAIL or not DEB_FULLNAME or not PPA_TARGET:
        print("Error: Missing required environment variables in .secrets (SIGNING_KEY_ID, DEB_EMAIL, DEB_FULLNAME, PPA_TARGET).")
        sys.exit(1)

    try:
        remote_url = subprocess.run(["git", "remote", "get-url", "origin"], cwd=project_path, capture_output=True, text=True, check=True).stdout.strip()
    except subprocess.CalledProcessError:
        remote_url = input("Enter your Git repository URL: ").strip()

    pyproject_name, base_version, description, script_file, _ = get_project_metadata(project_path)
    pkg_name = pyproject_name

    # Automatically clean up stale build artifacts/caches in the parent directory
    parent_dir = os.path.abspath(os.path.join(project_path, ".."))
    print("==> Checking for stale build artifacts in parent directory...")
    if os.path.exists(parent_dir):
        for filename in os.listdir(parent_dir):
            if filename.startswith(f"{pkg_name}_"):
                stale_path = os.path.join(parent_dir, filename)
                if os.path.isfile(stale_path):
                    print(f"==> Removing stale artifact: {filename}")
                    os.remove(stale_path)

    target_series = {
        "noble": f"{base_version}-1~noble",
        "resolute": f"{base_version}-1~resolute",
    }

    generate_debian_files(project_path, pkg_name, remote_url, base_version, description, script_file)

    orig_tarball = os.path.abspath(os.path.join(project_path, "..", f"{pkg_name}_{base_version}.orig.tar.gz"))
    subprocess.run(["git", "archive", "--format=tar.gz", f"--prefix={pkg_name}-{base_version}/", "HEAD", "-o", orig_tarball], cwd=project_path, check=True)

    for idx, (series, series_version) in enumerate(target_series.items()):
        print(f"\n==> Publishing to Launchpad ({PPA_TARGET}) for series: {series} ({series_version})...")
        update_changelog(project_path, pkg_name, series_version, series, f"Automated release for Ubuntu {series}.")
        
        # Use -sa for the first series upload, and -sd for subsequent series
        debuild_flag = "-sa" if idx == 0 else "-sd"
        subprocess.run(["debuild", "-S", debuild_flag, f"-k{KEY_ID}"], cwd=project_path, env={**os.environ, "DEBEMAIL": DEB_EMAIL, "DEBFULLNAME": DEB_FULLNAME}, check=True)
        
        changes_file = os.path.abspath(os.path.join(project_path, "..", f"{pkg_name}_{series_version}_source.changes"))
        subprocess.run(["dput", PPA_TARGET, changes_file], cwd=project_path, check=True)
        print(f"==> Successfully published to {PPA_TARGET} for {series}!")