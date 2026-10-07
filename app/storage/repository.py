from app.models.file_record import FileRecord


class FileRepository:
    """
    Simple in-memory repository for the assignment.

    A production deployment could replace this class with PostgreSQL/PostGIS
    without changing the API/service layer.
    """

    def __init__(self):
        self._items: dict[str, FileRecord] = {}

    def save(self, record: FileRecord) -> None:
        self._items[record.id] = record

    def get(self, file_id: str) -> FileRecord | None:
        return self._items.get(file_id)
