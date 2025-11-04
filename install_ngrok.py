"""
Download and install ngrok for Windows
"""
import os
import zipfile
import urllib.request
import sys

def download_ngrok():
    """Download ngrok for Windows"""
    print("Downloading ngrok...")

    # Ngrok download URL for Windows
    url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
    zip_path = "ngrok.zip"

    try:
        # Download the file
        urllib.request.urlretrieve(url, zip_path)
        print(f"Downloaded ngrok to {zip_path}")

        # Extract the zip file
        print("Extracting ngrok...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(".")

        print("ngrok extracted successfully!")

        # Clean up zip file
        os.remove(zip_path)
        print("Cleaned up zip file")

        # Check if ngrok.exe exists
        if os.path.exists("ngrok.exe"):
            print("\n✓ ngrok.exe is ready!")
            print("\nNext steps:")
            print("1. Get your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken")
            print("2. Run: ./ngrok.exe config add-authtoken YOUR_TOKEN")
            print("3. Run: ./ngrok.exe http 5000")
            return True
        else:
            print("Error: ngrok.exe not found after extraction")
            return False

    except Exception as e:
        print(f"Error downloading ngrok: {e}")
        return False

if __name__ == "__main__":
    download_ngrok()
