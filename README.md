# Geospatial File Measurement API

A FastAPI backend that accepts geospatial files, extracts their features, handles CRS correctly, and calculates measurements.

## Features

- FastAPI REST API
- Upload `.kml` files
- Upload `.zip` archives containing a Shapefile
- Extract feature ID/index, geometry type, geometry, CRS and properties
- Polygon/MultiPolygon area calculation in square meters
- LineString/MultiLineString length calculation in meters
- Point/MultiPoint supported with no measurement
- Unsupported geometry types are handled without crashing
- Geographic CRS such as EPSG:4326 is projected before measurements
- Automated tests with Pytest
- Interactive API documentation through Swagger UI

## Project structure

```text
geospatial-file-measurement-api/
├── app/
│   ├── api/routes.py
│   ├── models/file_record.py
│   ├── services/file_service.py
│   ├── services/geospatial_service.py
│   ├── storage/repository.py
│   └── main.py
├── tests/
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

### 1. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

The Swagger UI can be used to upload files and test every endpoint.

## API

### Health

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

### Upload

```http
POST /api/files/
Content-Type: multipart/form-data
```

Form field:

```text
file=<KML file or ZIP Shapefile>
```

Example response:

```json
{
  "id": "abc123",
  "filename": "survey.kml",
  "feature_count": 2,
  "crs": "EPSG:4326",
  "status": "COMPLETED",
  "created_at": "2026-10-07T00:00:00+00:00",
  "measurements_url": "/api/files/abc123/measurements/"
}
```

### File information

```http
GET /api/files/{id}/
```

Returns metadata about the uploaded file.

### Measurements

```http
GET /api/files/{id}/measurements/
```

Returns feature-level geometry and measurements.

Example:

```json
{
  "id": "abc123",
  "filename": "survey.kml",
  "crs": "EPSG:4326",
  "status": "COMPLETED",
  "features": [
    {
      "feature_id": 0,
      "source_index": "0",
      "geometry_type": "Polygon",
      "geometry": {},
      "crs": "EPSG:4326",
      "properties": {
        "name": "Area 1"
      },
      "measurement": {
        "type": "area",
        "value": 12345.67,
        "unit": "square_meters"
      }
    }
  ]
}
```

## CRS handling

The API never calculates area or distance directly from latitude/longitude degrees.

For geographic input such as EPSG:4326, GeoPandas is used to estimate a local UTM projected CRS. The geometry is transformed into that projected CRS and the measurement is then calculated.

If the input is already projected, that CRS is used directly.

This makes the resulting area and length measurements meaningful in metric units.

## File processing flow

```text
Upload
  ↓
Validate extension
  ↓
Save temporarily
  ↓
Extract ZIP if required
  ↓
Read with GeoPandas
  ↓
Extract features
  ↓
Choose projected CRS
  ↓
Calculate measurements
  ↓
Store result
  ↓
Return API response
```

## Testing

Run:

```bash
pytest -q
```

The tests cover:

- Health endpoint
- Polygon area calculation
- LineString length calculation

## Design decisions

### FastAPI

FastAPI was selected because it provides a clean REST API, request validation, automatic OpenAPI documentation and good support for asynchronous file uploads.

### GeoPandas

GeoPandas provides a high-level interface for reading geospatial formats, handling CRS transformations and working with feature geometries.

### Temporary file processing

Uploaded files are written to a temporary directory and removed after processing. This prevents temporary upload data from accumulating.

### Repository abstraction

The current assignment uses an in-memory repository to keep the project simple. The repository is isolated behind a small interface so it can later be replaced with PostgreSQL/PostGIS.

### Bulk feature processing

All features are processed in a single upload rather than requiring one request per feature.

## Learning and future scope

Possible production improvements:

- PostgreSQL + PostGIS persistence
- Object storage such as S3/Azure Blob
- Background processing with Celery/RQ
- Authentication and authorization
- Upload-size limits
- Virus/malware scanning
- More geospatial formats
- Better CRS selection for very large geographic extents
- Pagination for very large feature collections
- Docker deployment
- Structured logging and monitoring

## Interview explanation

A short explanation:

> "I built a FastAPI backend that accepts KML files and ZIP archives containing Shapefiles. GeoPandas reads the uploaded geospatial data and extracts each feature's geometry, properties and CRS. For measurements, I avoid calculating directly in latitude/longitude degrees. I transform geographic data such as EPSG:4326 into an appropriate projected CRS, usually a local UTM CRS, and then calculate polygon area or line length. The API exposes endpoints for uploading files, retrieving file information and retrieving feature measurements. I also added validation, graceful handling of unsupported geometries, automated tests and documentation."
