import os
import tomllib

def get_project_metadata(project_path):
    """Parses name, version, description, and exact script entry point from pyproject.toml."""
    toml_path = os.path.join(project_path, "pyproject.toml")
    
    # Defaults fallback
    dir_name = os.path.basename(os.path.normpath(project_path))
    name = dir_name
    version = "0.1.0"
    description = "A Python project"
    script_file = f"{dir_name}.py"
    entry_func = "main"

    if os.path.exists(toml_path):
        try:
            with open(toml_path, "rb") as f:
                data = tomllib.load(f)
            proj = data.get("project", {})
            name = proj.get("name", name)
            version = proj.get("version", version)
            description = proj.get("description", description)
            
            # Parse [project.scripts] e.g. ext = "ext:main" or pyprojectbuild = "pyprojectbuild.cli:main"
            scripts = proj.get("scripts", {})
            if scripts:
                script_name, entry_str = next(iter(scripts.items()))
                if ":" in entry_str:
                    mod_part, func_part = entry_str.split(":", 1)
                    entry_func = func_part
                    
                    # Resolve module path to file path
                    # Check src/ layout first
                    if os.path.exists(os.path.join(project_path, "src")):
                        parts = mod_part.split(".")
                        candidate_src = os.path.join(project_path, "src", *parts) + ".py"
                        if os.path.exists(candidate_src):
                            script_file = os.path.relpath(candidate_src, project_path)
                        else:
                            script_file = mod_part.replace(".", "/") + ".py"
                    else:
                        script_file = mod_part.replace(".", "/") + ".py"
        except Exception as e:
            print(f"[WARNING] Could not parse pyproject.toml: {e}")

    # Fallback sanity check for the script file existence
    full_script_path = os.path.join(project_path, script_file)
    if not os.path.exists(full_script_path):
        for candidate in [script_file, f"{name}.py", "main.py", "cli.py", "ext.py"]:
            if os.path.exists(os.path.join(project_path, candidate)):
                script_file = candidate
                break

    return name, version, description, script_file, entry_func