from pathlib import Path
from src.edurag_x.storage.storage_manager import StorageManager

storage = StorageManager()

test_file = Path("supabase_test.txt")
test_file.write_text("EduRAG-X persistent storage test", encoding="utf-8")

try:
    storage.upload_file(test_file, "test/supabase_test.txt")
    print("Upload Successful!")

    downloaded_file = Path("supabase_download_test.txt")
    storage.download_file("test/supabase_test.txt", downloaded_file)

    print("Download Successful!")
    print(downloaded_file.read_text(encoding="utf-8"))

except Exception as error:
    print("Storage Test Failed:")
    print(error)