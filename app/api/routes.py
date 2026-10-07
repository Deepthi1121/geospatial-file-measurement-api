from fastapi import APIRouter, File, HTTPException, UploadFile, status
from app.services.file_service import FileService
from app.storage.repository import FileRepository

router = APIRouter()
repository = FileRepository()
service = FileService(repository)


@router.post("/files/", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...)):
    try:
        return await service.process_upload(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Processing failed: {exc}")


@router.get("/files/{file_id}/")
def get_file(file_id: str):
    result = repository.get(file_id)
    if result is None:
        raise HTTPException(status_code=404, detail="File not found")
    return result.to_file_response()


@router.get("/files/{file_id}/measurements/")
def get_measurements(file_id: str):
    result = repository.get(file_id)
    if result is None:
        raise HTTPException(status_code=404, detail="File not found")
    return result.to_measurements_response()
