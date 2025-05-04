import tarfile
import zipfile
import tempfile
import os


# Extract the contents of a .tar.gz or .whl file into a temporary directory
def extract_to_temp_dir(archive_path):
    temp_dir = tempfile.mkdtemp()
    try:
        if archive_path.endswith(".tar.gz"):
            with tarfile.open(archive_path, "r:gz") as tar:
                tar.extractall(path=temp_dir)
        elif archive_path.endswith(".whl"):
            with zipfile.ZipFile(archive_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)
        return temp_dir
    except Exception as e:
        print(f"Error extracting files: {e}")
        return None

# Suspicious keywords often found in malicious or risky code
SUSPICIOUS_KEYWORDS = [
    "os.system", "subprocess", "eval", "exec", "socket", "ctypes", "base64", "open(",
    "wget", "requests.get", "input(", "pickle", "marshal", "compile", "globals",
    "locals", "__import__", "getattr(", "setattr("
]

# Scan a Python file line by line to detect suspicious keywords with context
def scan_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            found = []
            for i, line in enumerate(lines):
                for kw in SUSPICIOUS_KEYWORDS:
                    if kw in line:
                        context = "".join(lines[max(0, i-1):i+2]).strip()
                        found.append((kw, i + 1, context))
            # Remove duplicates while keeping the first occurrence and context
            unique = {}
            for kw, line_num, context in found:
                if kw not in unique:
                    unique[kw] = (line_num, context)
            return [(kw, line, ctx) for kw, (line, ctx) in unique.items()]

    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []


# Walk through all .py files in the extracted directory and analyze them
def analyze_extracted_dir(directory):
    report = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                keywords = scan_file(full_path)
                if keywords:
                    report.append({
                        "file": full_path,
                        "keywords_found": [kw[0] for kw in keywords],
                        "lines": [
                            {"keyword": kw[0], "line": kw[1], "context": kw[2]}
                            for kw in keywords
                        ]
                    })
    return report


# Generate a simple risk score based on the number and severity of findings
def generate_risk_score(report):
    critical = ["eval", "exec", "__import__", "os.system"]
    total = sum(len(entry["keywords_found"]) for entry in report)
    critical_count = sum(
        1 for entry in report for k in entry["keywords_found"] if k in critical
    )
    if critical_count > 0:
        return "High"
    elif total <= 2:
        return "Moderate"
    else:
        return "Safe"


# Full analysis function that extracts the package, scans for issues, and assigns a score
def analyze_package(archive_path):
    extracted_dir = extract_to_temp_dir(archive_path)
    if not extracted_dir:
        return None

    scan_report = analyze_extracted_dir(extracted_dir)
    score = generate_risk_score(scan_report)

    return {
        "suspicious_files": scan_report,
        "score": score
    }
