import shutil
import tempfile
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.models.file_record import FileRecord
from app.services.geospatial_service import GeospatialService
from app.storage.repository import FileRepository


class FileService:
    ALLOWED_EXTENSIONS = {".kml", ".zip"}

    def __init__(self, repository: FileRepository):
        self.repository = repository

    async def process_upload(self, upload: UploadFile) -> dict:
        filename = upload.filename or ""
        suffix = Path(filename).suffix.lower()

        if suffix not in self.ALLOWED_EXTENSIONS:
            raise ValueError("Only .kml files or .zip files containing a Shapefile are supported.")

        file_id = uuid.uuid4().hex
        work_dir = Path(tempfile.mkdtemp(prefix=f"geo_{file_id}_"))

        try:
            uploaded_path = work_dir / Path(filename).name
            with uploaded_path.open("wb") as output:
                shutil.copyfileobj(upload.file, output)

            source_path = self._prepare_source(uploaded_path, work_dir)
            gdf = GeospatialService.read_file(str(source_path))
            features = GeospatialService.extract_features(gdf)

            record = FileRecord(
                id=file_id,
                filename=filename,
                feature_count=len(gdf),
                crs=gdf.crs.to_string() if gdf.crs else None,
                status="COMPLETED",
                features=features,
            )
            self.repository.save(record)

            return {
                **record.to_file_response(),
                "measurements_url": f"/api/files/{file_id}/measurements/",
            }
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)

    @staticmethod
    def _prepare_source(uploaded_path: Path, work_dir: Path) -> Path:
        if uploaded_path.suffix.lower() == ".kml":
            return uploaded_path

        import zipfile

        extract_dir = work_dir / "extracted"
        extract_dir.mkdir()

        try:
            with zipfile.ZipFile(uploaded_path, "r") as zf:
                names = zf.namelist()
                if any(Path(name).is_absolute() or ".." in Path(name).parts for name in names):
                    raise ValueError("Invalid ZIP archive.")

                zf.extractall(extract_dir)
        except zipfile.BadZipFile as exc:
            raise ValueError("The uploaded ZIP file is invalid.") from exc

        shp_files = list(extract_dir.rglob("*.shp"))
        if not shp_files:
            raise ValueError("ZIP archive must contain a Shapefile (.shp).")
        return shp_files[0]
