from extractor import extract_dependencies
from analyzer import analyze_package

archive_path =  "pypi-test.tar.gz"
print(f"Analyzing local package archive: {archive_path}")

# Task 1 (partielle) – Extraction de dépendances et métadonnées
data = extract_dependencies(archive_path)
if data:
    print("\n--- Metadata ---")
    print(f"Name: {data['package_name']}")
    print(f"Version: {data['version']}")
    print(f"Author: {data['author']}")
    print(f"Description: {data['description']}")
    print("\nDependencies:")
    for dep in data["dependencies"]:
        print(f"- {dep}")
else:
    print("Unable to extract metadata or dependencies.")

# Task 2 – Analyse malicieuse
print("\n--- Malicious Code Analysis ---")
report = analyze_package(archive_path)
if report:
    print(f"Security Risk Score: {report['score']}")
    if report["suspicious_files"]:
        print("Suspicious files and keywords found:")
        for entry in report["suspicious_files"]:
            print(f"\nFile: {entry['file']}")
            for kw in entry["keywords_found"]:
                print(f"  → {kw}")
    else:
        print("No suspicious code found.")
else:
    print("Analysis failed.")
