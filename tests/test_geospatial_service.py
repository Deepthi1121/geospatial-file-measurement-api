import geopandas as gpd
from shapely.geometry import Polygon, LineString

from app.services.geospatial_service import GeospatialService


def test_polygon_area_is_calculated_in_square_meters():
    gdf = gpd.GeoDataFrame(
        {"name": ["square"]},
        geometry=[Polygon([(77.0, 12.0), (77.001, 12.0), (77.001, 12.001), (77.0, 12.001)])],
        crs="EPSG:4326",
    )

    features = GeospatialService.extract_features(gdf)

    assert features[0]["geometry_type"] == "Polygon"
    assert features[0]["measurement"]["type"] == "area"
    assert features[0]["measurement"]["value"] > 0


def test_linestring_length_is_calculated_in_meters():
    gdf = gpd.GeoDataFrame(
        {"name": ["line"]},
        geometry=[LineString([(77.0, 12.0), (77.001, 12.0)])],
        crs="EPSG:4326",
    )

    features = GeospatialService.extract_features(gdf)

    assert features[0]["measurement"]["type"] == "length"
    assert features[0]["measurement"]["value"] > 0
