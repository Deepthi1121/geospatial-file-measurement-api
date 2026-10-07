from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Geospatial File Measurement API",
    version="1.0.0",
    description="Upload Shapefile ZIP/KML files and retrieve feature measurements.",
)

app.include_router(router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok"}
