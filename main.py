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
    # Ask the user for the name of the package to analyze
    package_name = input("Enter the PyPI package name: \n").strip()

    save_dir = "./downloaded_packages"
    os.makedirs(save_dir, exist_ok=True)

    # Get the latest version of the package from PyPI
    version = get_latest_version(package_name)
    if not version:
        logger.error("Error: Package not found on PyPI.")
        return
    logger.info(f"Latest version found: {version}")

    # Download the package archive
    archive_path = download_package(package_name, version, save_dir)
    if not archive_path:
        logger.error("Error during package download.")
        return

    # Extract metadata and dependencies
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

    # Run static analysis to detect potentially malicious code
    logger.info("--- Malicious Code Analysis ---")
    analysis = analyze_package(archive_path)
    if analysis:
        logger.info(f"Security Risk Score: {analysis['score']}")
        if analysis['suspicious_files']:
            logger.warning("Suspicious files and keywords found:")
            for item in analysis['suspicious_files']:
                logger.warning(f"File: {item['file']}")
                for kw in item['keywords_found']:
                    logger.warning(f"  → {kw}")
        else:
            logger.info("No suspicious code found.")
    else:
        logger.error("Analysis could not be completed.")

if __name__ == "__main__":
    main()
