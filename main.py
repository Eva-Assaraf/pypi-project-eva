from downloader import get_latest_version, download_package
from extractor import extract_dependencies
from analyzer import analyze_package

import os
import logging

# Set up logging to show messages in the console and save them to a file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("package_downloader.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    user_input = input("Enter a PyPI package name OR path to a .tar.gz/.whl/directory:\n").strip()

    # If it's a path to a local file or directory, skip download
    if os.path.exists(user_input):
        archive_path = user_input
        logger.info(f"Analyzing local package: {archive_path}")
    else:
        # Assume it's a PyPI package name
        package_name = user_input
        save_dir = "./downloaded_packages"
        os.makedirs(save_dir, exist_ok=True)

        version = get_latest_version(package_name)
        if not version:
            logger.error("Error: Package not found on PyPI.")
            return
        logger.info(f"Latest version found: {version}")

        archive_path = download_package(package_name, version, save_dir)
        if not archive_path:
            logger.error("Error during package download.")
            return

    # Task 1 (extract metadata) — only if archive
    if archive_path.endswith(".tar.gz") or archive_path.endswith(".whl"):
        dependencies = extract_dependencies(archive_path)
        if dependencies:
            logger.info(f"Name: {dependencies['package_name']}\n"
                        f"Version: {dependencies['version']}\n"
                        f"Author: {dependencies['author']}\n"
                        f"Description: {dependencies['description']}")
            logger.info("Dependencies found:")
            for dep in dependencies['dependencies']:
                logger.info(f"- {dep}")
        else:
            logger.warning("No dependencies found or unable to extract.")
    else:
        logger.info("Skipping dependency extraction (not a .tar.gz or .whl file)")

    # Task 2 – Analyze code statically
    logger.info("--- Malicious Code Analysis ---")
    analysis = analyze_package(archive_path)
    if analysis:
        logger.info(f"Security Risk Score: {analysis['score']}")
        if analysis['suspicious_files']:
            logger.warning("Suspicious files and keywords found:")
            for item in analysis['suspicious_files']:
                logger.warning(f"File: {item['file']} ({item['type']})")
                for kw in item["lines"]:
                    logger.warning(f"  → Line {kw['line']}: {kw['keyword']}")
                    logger.warning(f"    Context: {kw['context']}")
        else:
            logger.info("No suspicious code found.")
    else:
        logger.error("Analysis could not be completed.")

if __name__ == "__main__":
    main()
