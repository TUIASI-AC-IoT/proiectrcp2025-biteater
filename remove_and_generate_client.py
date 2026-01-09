import os
import random
import string
import shutil

# Configuration
BASE_DIR = "./"
CLIENT_ROOT = os.path.join(BASE_DIR, "FileExplorerClient")

    # 2. CLIENT SIDE SETUP
# -----------------------------------------------------
def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created folder: {path}")

def create_text_file(path, content_str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content_str)
    print(f"Created text file: {path}")

def create_dummy_binary_file(path, size_in_mb):
    """Creates a file with random binary data to simulate specific sizes."""
    size_bytes = int(size_in_mb * 1024 * 1024)
    with open(path, "wb") as f:
        # We generate random bytes. For speed on large files, we repeat a smaller chunk.
        chunk = os.urandom(1024) 
        for _ in range(size_bytes // 1024):
            f.write(chunk)
    print(f"📦 Created binary file ({size_in_mb} MB): {path}")

def generate_environment():
    print(f"--- SETTING UP ENVIRONMENT IN: {os.path.abspath(BASE_DIR)} ---\n")
 
    # A. Standard Uploads
    upload_path = os.path.join(CLIENT_ROOT, "upload_queue")
    create_folder(upload_path)
    create_text_file(os.path.join(upload_path, "new_contract.txt"), "%PDF-1.5\nSigned contract content...")
    create_dummy_binary_file(os.path.join(upload_path, "vacation_photo.txt"), 2.0)

    # B. Bulk Uploads
    bulk_path = os.path.join(CLIENT_ROOT, "bulk_upload_test")
    create_folder(bulk_path)
    for i in range(1, 51):
        filename = f"item_{i:03d}.dat"
        create_text_file(os.path.join(bulk_path, filename), f"Data content for item {i}")


    print("\n--- GENERATION COMPLETE ---")
    print(f"Test files created in: {os.path.abspath(BASE_DIR)}")

if __name__ == "__main__":
    if os.path.exists(CLIENT_ROOT):
        shutil.rmtree(CLIENT_ROOT)
    generate_environment()
