import os
import subprocess
import sys

def build(project_path, name, version, description):
    """Generates a macOS-optimized PyInstaller spec and builds the standalone binary."""
    print(f"\n==> Building macOS package bundle for {name} v{version} at '{project_path}'...")

    # Intelligently locate the target script
    script_file = None
    for candidate in [f"{name}.py", f"{name}", "main.py", "cli.py", "ext.py"]:
        if os.path.exists(os.path.join(project_path, candidate)):
            script_file = candidate
            break
    if not script_file:
        py_files = [f for f in os.listdir(project_path) if f.endswith(".py") and f not in ["setup.py", "conftest.py"]]
        script_file = py_files[0] if py_files else f"{name}.py"

    print(f"==> Detected script entry point: {script_file}")

    if sys.platform != "darwin":
        print("\n[NOTE] You are generating a macOS build configuration from a non-macOS system.")
        print("PyInstaller builds native binaries for the host OS. A .spec file will be generated for macOS compilation.")

    # Generate PyInstaller Spec file optimized for macOS CLI/apps
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{script_file}'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""
    spec_path = os.path.join(project_path, f"{name}.spec")
    with open(spec_path, "w") as f:
        f.write(spec_content)
    os.chmod(spec_path, 0o644)
    print(f"==> Generated PyInstaller spec: {spec_path}")

    # Sanitize environment
    clean_env = os.environ.copy()
    clean_env.pop("VIRTUAL_ENV", None)
    clean_env.pop("PYTHONPATH", None)
    path_dirs = clean_env.get("PATH", "").split(os.pathsep)
    clean_env["PATH"] = os.pathsep.join([d for d in path_dirs if ".venv" not in d])

    # If running on macOS, build immediately
    if sys.platform == "darwin":
        try:
            subprocess.run(
                ["pyinstaller", "--clean", spec_path],
                cwd=project_path,
                check=True,
                env=clean_env
            )
            print(f"\n==> Success! macOS standalone binary built for '{name}' in dist/ folder.")
        except subprocess.CalledProcessError as e:
            print(f"\n[ERROR] PyInstaller failed with exit code: {e.returncode}")
            sys.exit(1)
    else:
        print(f"==> Spec file ready at '{spec_path}'. Transfer this project to macOS and run 'pyinstaller {name}.spec' to compile the native Mac binary.")