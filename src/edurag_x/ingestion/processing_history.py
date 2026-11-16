import json
from pathlib import Path
from datetime import datetime, timezone


class ProcessingHistory:

    def __init__(self, history_file="data/history/processing_history.json"):
        self.history_file = Path(history_file)

        # Create history directory if it does not exist
        self.history_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # Create empty JSON file if it does not exist
        if not self.history_file.exists():
            self.history_file.write_text(
                "[]",
                encoding="utf-8"
            )

    def get_history(self):
        """Return all saved processing records."""

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

        except json.JSONDecodeError:
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
        """Save a new document processing record."""

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

        return record

    def clear_history(self):
        """Remove all processing history."""

        with open(
            self.history_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump([], file, indent=4)