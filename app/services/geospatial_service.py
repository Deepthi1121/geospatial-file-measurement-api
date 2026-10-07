from typing import Any

import geopandas as gpd
from pyproj import CRS


class GeospatialService:
    """
    Reads geospatial files and calculates measurements.

    Measurements are deliberately calculated after projecting geographic
    coordinates into a suitable metric CRS rather than calculating directly
    from latitude/longitude degrees.
    """

    @staticmethod
    def read_file(path: str) -> gpd.GeoDataFrame:
        gdf = gpd.read_file(path)
        if gdf.empty:
            raise ValueError("The uploaded geospatial file contains no features.")
        return gdf

    @staticmethod
    def choose_projected_crs(gdf: gpd.GeoDataFrame) -> CRS:
        if gdf.crs is None:
            raise ValueError("The input file has no CRS. A CRS is required for measurement.")

        # GeoPandas estimates a local UTM CRS from the dataset extent.
        # This is appropriate for most local/regional datasets.
        if gdf.crs.is_projected:
            return CRS.from_user_input(gdf.crs)

        estimated = gdf.estimate_utm_crs()
        if estimated is not None:
            return CRS.from_user_input(estimated)

        # Fallback to Web Mercator only when a local UTM CRS cannot be estimated.
        return CRS.from_epsg(3857)

    @classmethod
    def extract_features(cls, gdf: gpd.GeoDataFrame) -> list[dict[str, Any]]:
        source_crs = gdf.crs.to_string() if gdf.crs else None
        projected_crs = cls.choose_projected_crs(gdf)
        projected = gdf.to_crs(projected_crs)

        results: list[dict[str, Any]] = []

        for index, (row, projected_row) in enumerate(zip(gdf.iterrows(), projected.iterrows())):
            original_idx, original_feature = row
            _, projected_feature = projected_row
            geometry = original_feature.geometry
            projected_geometry = projected_feature.geometry

            geometry_type = geometry.geom_type if geometry is not None else "Unknown"

            item: dict[str, Any] = {
                "feature_id": index,
                "source_index": str(original_idx),
                "geometry_type": geometry_type,
                "geometry": geometry.__geo_interface__ if geometry is not None else None,
                "crs": source_crs,
                "properties": {
                    str(k): cls._json_safe(v)
                    for k, v in original_feature.drop(labels="geometry").to_dict().items()
                },
            }

            if geometry_type in {"Polygon", "MultiPolygon"}:
                item["measurement"] = {
                    "type": "area",
                    "value": float(projected_geometry.area),
                    "unit": "square_meters",
                }
            elif geometry_type in {"LineString", "MultiLineString"}:
                item["measurement"] = {
                    "type": "length",
                    "value": float(projected_geometry.length),
                    "unit": "meters",
                }
            elif geometry_type in {"Point", "MultiPoint"}:
                item["measurement"] = None
            else:
                # Gracefully handle unsupported geometry types.
                item["measurement"] = None
                item["measurement_status"] = "UNSUPPORTED_GEOMETRY"

            results.append(item)

        return results

    @staticmethod
    def _json_safe(value: Any) -> Any:
        if value is None:
            return None
        if hasattr(value, "item"):
            try:
                return value.item()
            except Exception:
                pass
        return value
