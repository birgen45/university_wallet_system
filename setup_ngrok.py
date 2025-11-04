"""
Setup ngrok - Extract and configure with authtoken
"""
import zipfile
import os
import subprocess

def setup_ngrok():
    """Extract ngrok and add authtoken"""

    # Check if zip exists
    if not os.path.exists("ngrok.zip"):
        print("Error: ngrok.zip not found!")
        return False

    # Extract ngrok
    print("Extracting ngrok.zip...")
    try:
        with zipfile.ZipFile("ngrok.zip", 'r') as zip_ref:
            zip_ref.extractall(".")
        print("✓ Extracted successfully!")
    except Exception as e:
        print(f"Error extracting: {e}")
        print("\nPlease extract ngrok.zip manually:")
        print("1. Right-click ngrok.zip")
        print("2. Select 'Extract All...'")
        print("3. Extract to this folder")
        print("4. Run this script again")
        return False

    # Check if ngrok.exe exists
    if not os.path.exists("ngrok.exe"):
        print("Error: ngrok.exe not found after extraction!")
        return False

    print("✓ ngrok.exe is ready!")

    # Add authtoken
    authtoken = "34dzKFseI6oCfuJEgOpS3RcHiE2_TQnyUFtmWCBhesJ1E9sL"
    print("\nAdding authentication token...")

    try:
        result = subprocess.run(
            ["./ngrok.exe", "config", "add-authtoken", authtoken],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.returncode == 0:
            print("✓ Authtoken added successfully!")
        else:
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error adding authtoken: {e}")
        return False

    print("\n" + "="*60)
    print("✓ Setup Complete!")
    print("="*60)
    print("\nTo start ngrok tunnel, run:")
    print("  ./ngrok.exe http 5000")
    print("\nOr double-click: start_ngrok.bat")
    print("="*60)

    return True

if __name__ == "__main__":
    setup_ngrok()
