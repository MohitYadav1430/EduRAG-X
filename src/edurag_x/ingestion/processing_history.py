import json
from pathlib import Path
from datetime import datetime, timezone

from src.edurag_x.storage.storage_manager import StorageManager


class ProcessingHistory:

    def __init__(
        self,
        history_file="data/history/processing_history.json",
        storage_manager=None
    ):

        self.history_file = Path(history_file)
        self.storage_manager = storage_manager

        self.history_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # Restore history from Supabase
        if self.storage_manager is not None:
            try:
                self.storage_manager.download_file(
                    "history/processing_history.json",
                    self.history_file
                )
            except Exception:
                pass

        if not self.history_file.exists():
            self.history_file.write_text(
                "[]",
                encoding="utf-8"
            )

    def _sync_cloud(self):

        if self.storage_manager is None:
            return

        self.storage_manager.upload_file(
            self.history_file,
            "history/processing_history.json"
        )

    def get_history(self):

        try:
            with open(
                self.history_file,
                "r",
                encoding="utf-8"
            ) as file:

                history = json.load(file)

                if isinstance(history, list):
                    return history

                return []

        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def add_record(
        self,
        filename,
        status,
        pages=0,
        chunks=0,
        vectors=0,
        error=None
    ):

        history = self.get_history()

        record = {
            "filename": filename,
            "status": status,
            "pages": pages,
            "chunks": chunks,
            "vectors": vectors,
            "error": error,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat()
        }

        history.append(record)

        with open(
            self.history_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                history,
                file,
                indent=4,
                ensure_ascii=False
            )

        self._sync_cloud()

        return record

    def clear_history(self):

        with open(
            self.history_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump([], file, indent=4)

        self._sync_cloud()