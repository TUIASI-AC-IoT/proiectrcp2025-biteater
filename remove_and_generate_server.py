import os
import random
import string
import shutil

# Configuration
BASE_DIR = "./"
SERVER_ROOT = os.path.join(BASE_DIR, "FileExplorerServer")

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

    path = os.path.join(SERVER_ROOT, "downloads_test")
    create_folder(path)
    
    # 2KB Config JSON
    json_content = '{\n  "app_name": "StorageTest",\n  "version": 1.0,\n  "settings": {\n    "retry_count": 5,\n    "timeout": 300\n  }\n}'
    create_text_file(os.path.join(path, "config.json"), json_content)
    
    
    # B. Operations Test (Move/Rename)
    inbox_path = os.path.join(SERVER_ROOT, "operations_test", "inbox")
    archive_path = os.path.join(SERVER_ROOT, "operations_test", "archive")
    create_folder(inbox_path)
    create_folder(archive_path)
    
    # PDF Report
    pdf_dummy_content = "%PDF-1.4\n" + ("This is a dummy PDF line. " + "\n") * 100
    create_text_file(os.path.join(inbox_path, "report_2023.txt"), pdf_dummy_content)
    
    # Notes Text
    create_text_file(os.path.join(inbox_path, "notes.txt"), "Meeting notes:\n- Review storage capacity.\n- Check latency.\n")

    # C. Cleanup Zone (Delete)
    cleanup_path = os.path.join(SERVER_ROOT, "cleanup_zone")
    temp_folder = os.path.join(cleanup_path, "old_temp_folder")
    create_folder(temp_folder)
    
    create_text_file(os.path.join(cleanup_path, "obsolete_log.log"), "Error: Connection timeout at 00:00:00\n" * 500)
    create_text_file(os.path.join(temp_folder, "junk_1.tmp"), "Temp data 111111")
    create_text_file(os.path.join(temp_folder, "junk_2.tmp"), "Temp data 222222")

    # D. Edge Cases (Nesting & Special Chars)
    deep_path = os.path.join(SERVER_ROOT, "edge_cases", "deep_nest_A", "deep_nest_B", "deep_nest_C")
    create_folder(deep_path)
    create_text_file(os.path.join(deep_path, "hidden_treasure.txt"), "You found me! This tests recursive path parsing.")
    
    special_path = os.path.join(SERVER_ROOT, "edge_cases", "special_!@#_chars")
    create_folder(special_path)
    create_text_file(os.path.join(special_path, "file with spaces.txt"), "This filename tests URL encoding.")

    print("\n--- GENERATION COMPLETE ---")
    print(f"Test files created in: {os.path.abspath(BASE_DIR)}")


if __name__ == '__main__':
    if os.path.exists(SERVER_ROOT):
        shutil.rmtree(SERVER_ROOT)
    generate_environment()

