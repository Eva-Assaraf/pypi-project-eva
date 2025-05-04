import tarfile
import zipfile
import re

def extract_dependencies(archive_path):
    dependencies = []
    metadata = {
        "package_name": None,
        "version": None,
        "author": None,
        "description": None
    }

    try:
        # Handle .tar.gz files (usually source distributions)
        if archive_path.endswith(".tar.gz"):
            with tarfile.open(archive_path, "r:gz") as tar:
                for m in tar.getmembers():
                    if "requirements.txt" in m.name:
                        # Parse dependencies from requirements.txt
                        f = tar.extractfile(m)
                        content = f.read().decode()
                        dependencies += parse_requirements_txt(content)
                    elif "setup.py" in m.name:
                        # Parse dependencies from setup.py
                        f = tar.extractfile(m)
                        content = f.read().decode()
                        dependencies += parse_setup_py(content)
                    elif "PKG-INFO" in m.name:
                        # Extract metadata (name, version, etc.) from PKG-INFO
                        f = tar.extractfile(m)
                        content = f.read().decode()
                        metadata.update(parse_metadata_info(content))

        # Handle .whl files (wheel format is a zip archive)
        elif archive_path.endswith(".whl"):
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                for file in zip_ref.namelist():
                    if file.endswith("METADATA"):
                        # Extract dependencies and metadata from METADATA file
                        with zip_ref.open(file) as f:
                            content = f.read().decode()
                            dependencies += parse_wheel_metadata(content)
                            metadata.update(parse_metadata_info(content))

    except Exception as e:
        print(f"Extraction error: {e}")

    # Remove duplicates and assign to metadata
    metadata["dependencies"] = list(set(dependencies))
    return metadata

def parse_requirements_txt(content):
    # Return all non-comment, non-empty lines
    return [line.strip() for line in content.splitlines() if line.strip() and not line.startswith("#")]

def parse_setup_py(content):
    found = re.findall(r"install_requires\s*=\s*\[(.*?)\]", content, re.DOTALL)
    if found:
        raw = found[0]
        return [line.strip().strip("\"'") for line in raw.split(",") if line.strip()]
    return []

def parse_wheel_metadata(content):
    # Extract lines starting with "Requires-Dist:" (used in wheel METADATA)
    return [line.split(": ", 1)[1] for line in content.splitlines() if line.startswith("Requires-Dist:")]

def parse_metadata_info(content):
    """Extrait proprement Name, Version, Author ou Maintainer, Summary."""
    info = {}
    for line in content.splitlines():
        if line.startswith("Name: "):
            info["package_name"] = line.split(": ", 1)[1].strip()
        elif line.startswith("Version: "):
            info["version"] = line.split(": ", 1)[1].strip()
        elif line.startswith("Author: "):
            author = line.split(": ", 1)[1].strip()
            if author and author.upper() != "UNKNOWN":
                info["author"] = author
        elif line.startswith("Maintainer: ") and "author" not in info:
            maintainer = line.split(": ", 1)[1].strip()
            if maintainer and maintainer.upper() != "UNKNOWN":
                info["author"] = maintainer
        elif line.startswith("Summary: "):
            info["description"] = line.split(": ", 1)[1].strip()
    # Fallback if no author was found
    if "author" not in info:
        info["author"] = "Not specified"
    return info
