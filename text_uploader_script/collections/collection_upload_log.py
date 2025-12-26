import csv
from pathlib import Path

from uploader_app.config import COLLECTION_UPLOAD_LOG_FILE


LOG_PATH = Path(COLLECTION_UPLOAD_LOG_FILE)

# Header for collection upload log: id (destination), pecha_collection_id (source), title (English)
LOG_HEADER = [
    "id",
    "pecha_collection_id",
    "title",
]


def _ensure_log_file() -> None:
    """Ensure the log file exists with the proper header."""
    if not LOG_PATH.exists():
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(LOG_HEADER)
        return

    # If the file exists, ensure its header matches the current LOG_HEADER.
    with LOG_PATH.open("r", newline="", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        # Empty file – just write the new header.
        with LOG_PATH.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(LOG_HEADER)
        return

    # Parse the existing header row via csv to handle commas/quoting correctly.
    existing_header = next(csv.reader([lines[0].strip()]))

    if existing_header == LOG_HEADER:
        # Already up-to-date.
        return

    # If the header is different, we leave it alone to avoid data loss
    return


def get_parent_id_by_pecha_collection_id(pecha_collection_id: str) -> str | None:
    """
    Look up the destination collection ID (id) by matching the pecha_collection_id.
    Returns None if not found.
    """
    if not LOG_PATH.exists():
        return None

    with LOG_PATH.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("pecha_collection_id") == pecha_collection_id:
                return row.get("id")

    return None


def log_uploaded_collection(
    id: str,
    pecha_collection_id: str,
    title: str | None = None,
) -> None:
    """
    Log an uploaded collection with its destination ID, source pecha_collection_id, and title.
    """
    _ensure_log_file()

    with LOG_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                id,
                pecha_collection_id,
                title or "",
            ]
        )

