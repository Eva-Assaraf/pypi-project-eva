import requests
import os

def get_latest_version(package_name):
    # Construct the URL to get the package metadata from PyPI
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # If request is successful, return the latest version
            data = response.json()
            return data["info"]["version"]
        else:
            return None
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

def download_package(package_name, version, save_path):
    # Construct the URL to get the specific version metadata
    url = f"https://pypi.org/pypi/{package_name}/{version}/json"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None

        urls = response.json()["urls"]
        if not urls:
            return None

        # Prefer to download a .whl file if available
        for file in urls:
            if file["filename"].endswith(".whl"):
                download_url = file["url"]
                break
        else:
            # If no .whl is available, download the first file listed
            download_url = urls[0]["url"]

        # Define the file path to save the downloaded file
        filename = download_url.split("/")[-1]
        full_path = os.path.join(save_path, filename)

        # Download and save the file content
        file_data = requests.get(download_url)
        with open(full_path, "wb") as f:
            f.write(file_data.content)

        return full_path
    except Exception as e:
        print(f"Download error: {e}")
        return None
