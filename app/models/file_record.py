from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class FileRecord:
    id: str
    filename: str
    feature_count: int
    crs: str | None
    status: str
    features: list[dict[str, Any]] = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_file_response(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "filename": self.filename,
            "feature_count": self.feature_count,
            "crs": self.crs,
            "status": self.status,
            "created_at": self.created_at,
        }

    def to_measurements_response(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "filename": self.filename,
            "crs": self.crs,
            "status": self.status,
            "features": self.features,
        }
