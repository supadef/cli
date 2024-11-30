import os


def get_pyproject_path():
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Move one level higher
    parent_dir = os.path.dirname(script_dir)
    # Construct the path to pyproject.toml in the parent directory
    pyproject_path = os.path.join(parent_dir, "pyproject.toml")
    return pyproject_path


def get_version_from_pyproject(pyproject_path):
    with open(pyproject_path, "r") as f:
        # Read all lines from the file
        lines = f.readlines()
        # Filter the line that begins with "version"
        version_line = next(
            (line.strip() for line in lines if line.strip().startswith("version")), None)
        # Extract the version string
        if version_line:
            version = version_line.split("=")[1].strip().strip('"')
            return version
        else:
            return None


VERSION = get_version_from_pyproject(get_pyproject_path())
