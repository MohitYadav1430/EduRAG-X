from pathlib import Path

from src.edurag_x.storage.supabase_client import get_supabase_client


class StorageManager:

    def __init__(self, bucket_name="eduragx-storage"):
        self.client = get_supabase_client()
        self.bucket_name = bucket_name
        self.bucket = self.client.storage.from_(bucket_name)

    def upload_file(self, local_path, remote_path):

        local_path = Path(local_path)

        with open(local_path, "rb") as file:
            self.bucket.upload(
                path=remote_path,
                file=file,
                file_options={
                    "upsert": "true"
                }
            )

        return True

    def download_file(self, remote_path, local_path):

        local_path = Path(local_path)
        local_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        response = self.bucket.download(remote_path)

        with open(local_path, "wb") as file:
            file.write(response)

        return True

    def file_exists(self, remote_path):

        try:
            self.bucket.download(remote_path)
            return True
        except Exception:
            return False

    def delete_file(self, remote_path):

        self.bucket.remove([remote_path])
        return True