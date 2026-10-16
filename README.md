# pyprojectbuild

pyprojectbuild is a powerful, modular command-line tool designed to parse project metadata and script entry points directly from pyproject.toml and package Python CLI utilities for multi-platform distribution (Debian .deb, Snap, Flatpak, macOS, Windows executables, and Launchpad PPA publishing).   

## Prerequisites & System Requirements

Before installing and using pyprojectbuild, ensure your environment meets the following requirements:Python 3.8+ (Python 3.11+ recommended for built-in tomllib support).
- Build Tools & Utilities (depending on the targets you wish to build)
    - Debian (deb / PPA):
     dpkg-buildpackage, dh-python, debhelper, debuild, dput, and git.- Snap (snap): snapcraft.Flatpak (flatpak): flatpak and flatpak-builder.
    - Windows/Mac (win/mac):
     PyInstaller (handled via individual builders
     
## Installation
You can install pyprojectbuild locally in editable mode via pip:Bash

```
cd /path/to/pyprojectbuild
pip install --editable .

```
## Usage

pyprojectbuild automatically targets your current working directory if no path is provided, making it fast and easy to run directly inside your project folders.General Syntax Bash

```
pyprojectbuild <command> [project_path]


```
## Available Subcommands
### Debian Package (deb)
Builds a local Debian .deb package.   
```
pyprojectbuild deb

```
### Launchpad PPA Publishing (ppa)

Interactively sets up or loads your .secrets file (GPG Signing Key ID, email, full name, and PPA target) and automatically packages and uploads source changes for target Ubuntu series (noble, resolute).

```
pyprojectbuild ppa

```
### Flatpak Package (flatpak)
Builds and installs a local Flatpak package and exports a standalone .flatpak bundle. (Note: Kept out of the default all pipeline to avoid long build/download times).   Bash

```
pyprojectbuild flatpak

```
### Snap Package (snap)

```
pyprojectbuild snap

```
Windows Executable (win)
```
pyprojectbuild win

```
### macOS Executable (mac)

```
pyprojectbuild mac

```
Build All Standard Targets (all)
Runs the standard local build pipeline (deb, snap, win, mac). (Excludes Flatpak by design).   

```
pyprojectbuild all
```