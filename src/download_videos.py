import os
import subprocess
import glob

# Configuration
R2_ENDPOINT = "https://[YOUR_ACCOUNT_ID].r2.cloudflarestorage.com"
R2_BUCKET = "s3://video-renders"
LOCAL_DOWNLOAD_DIR = "downloaded_videos"

# You must set these as environment variables or replace them here (not recommended for git)
# Better to export them in your terminal: export R2_ACCOUNT_ID="xyz..."

def download_new_videos():
    print("Checking R2 for new videos...")

    # Ensure download directory exists
    os.makedirs(LOCAL_DOWNLOAD_DIR, exist_ok=True)

    # List files in the bucket
    # We use the AWS CLI because it's already installed and configured
    try:
        # List files
        cmd_list = [
            "aws", "s3", "ls", R2_BUCKET,
            "--endpoint-url", os.environ.get("R2_ENDPOINT_URL")
        ]
        result = subprocess.run(cmd_list, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Error listing bucket: {result.stderr}")
            return

        files = result.stdout.splitlines()
        if not files:
            print("No videos found in R2.")
            return

        print(f"Found {len(files)} files. Downloading...")

        # Download everything recursively to the local folder
        cmd_download = [
            "aws", "s3", "cp", R2_BUCKET, LOCAL_DOWNLOAD_DIR,
            "--recursive",
            "--endpoint-url", os.environ.get("R2_ENDPOINT_URL")
        ]

        subprocess.run(cmd_download, check=True)
        print(f"Success! Videos saved to: {os.path.abspath(LOCAL_DOWNLOAD_DIR)}")

        # Optional: Clean up R2 after download to save space? 
        # Uncomment the next line if you want to delete files from cloud after downloading
        # subprocess.run(["aws", "s3", "rm", R2_BUCKET, "--recursive", "--endpoint-url", os.environ.get("R2_ENDPOINT_URL")])

    except Exception as e:
        print(f"Download failed: {e}")

if __name__ == "__main__":
    # Check if Endpoint is set
    if not os.environ.get("R2_ENDPOINT_URL"):
        print("Error: R2_ENDPOINT_URL environment variable not set.")
        print("Run: export R2_ENDPOINT_URL=https://<your-account-id>.r2.cloudflarestorage.com")
    else:
        download_new_videos()
