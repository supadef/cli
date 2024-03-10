import os


def get_version_from_pyproject():
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the path to pyproject.toml
    pyproject_path = os.path.join(script_dir, "pyproject.toml")
    with open(pyproject_path, "r") as f:
        # Read all lines from the file
        lines = f.readlines()
        # Filter the line that begins with "version"
        version_line = next((line.strip() for line in lines if line.strip().startswith("version")), None)
        # Extract the version string
        if version_line:
            version = version_line.split("=")[1].strip().strip('"')
            return version
        else:
            return None


VERSION = get_version_from_pyproject()

