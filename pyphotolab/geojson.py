from geojson import Point, MultiPoint, Polygon, Feature, FeatureCollection, dump
from pyphotolab.photodb import db_connect, db_get_cluster_centers, db_get_hull_curve, db_get_no_cluster_points
from pyphotolab.util import swap_lat_lon
from pyphotolab.geo_reverse import get_geo_description


# NOTE: geojson uses (longitude/latitude) notion instead of (lat/lon)
# so swap_lat_lon() needs to be calling before calling a geojson function

def create_geo_features():
    features = []
    conn = db_connect()
    cluster_centers = db_get_cluster_centers(conn)
    for c in cluster_centers:
        (label, count_photos, lat_deg, lon_deg) = c
        point = Point((lon_deg, lat_deg))
        get_geo_description(lat_deg, lon_deg)
        feature = Feature(geometry=point, properties={
            "photos-cluster-label": label,
            "photos-cluster-count": count_photos,
            "marker-color": "#c81e1e",
            "marker-size": "large",
            "marker-symbol": "camera"})

        features.append(feature)

        polygon_coords = swap_lat_lon(db_get_hull_curve(conn, label))
        polygon = Polygon([polygon_coords])
        feature = Feature(geometry=polygon, properties={})

        features.append(feature)

    no_cluster_points = swap_lat_lon(db_get_no_cluster_points(conn))
    points = MultiPoint(no_cluster_points)
    feature = Feature(geometry=points, properties={
        "marker-color": "#f6ae13",
        "marker-size": "small",
        "marker-symbol": "camera"})

    features.append(feature)

    conn.close()
    return features


def create_geojson_file(file_name='photo_locations.json'):
    features = create_geo_features()
    feature_collection = FeatureCollection(features)
    with open(file_name, 'w') as f:
        dump(feature_collection, f)
