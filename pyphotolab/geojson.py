from geojson import Point, MultiPoint, Polygon, Feature, FeatureCollection, dump
from pyphotolab.photodb import db_connect, db_get_cluster_centers, db_get_hull_curve, db_get_unclustered_points
from pyphotolab.util import swap_lat_lon


def create_geo_features():
    features = []
    conn = db_connect()
    cluster_centers = db_get_cluster_centers(conn)
    for c in cluster_centers:
        (label, count_photos, lat_deg, lon_deg) = c
        point = Point((lon_deg, lat_deg))
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

    unclustered_points = swap_lat_lon(db_get_unclustered_points(conn))
    points = MultiPoint(unclustered_points)
    feature = Feature(geometry=points, properties={
            "marker-color": "#f6ae13",
            "marker-size": "small",
            "marker-symbol": "camera"})

    features.append(feature)

    conn.close()
    return features


def create_geojson_file(file_name='photo_locations.geojson'):
    features = create_geo_features()
    feature_collection = FeatureCollection(features)
    with open(file_name, 'w') as f:
        dump(feature_collection, f)
