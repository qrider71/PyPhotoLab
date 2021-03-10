from os.path import normpath, getsize
from hashlib import sha512
from GPSPhoto import gpsphoto
from PIL import Image
from scipy.spatial import ConvexHull

from sklearn.cluster import OPTICS, cluster_optics_dbscan

import arrow

from pyphotolab.files import get_jpg_files
from pyphotolab.photodb import *

RADIUS_EARTH_KM = 6371.0

BLOCK_SIZE = 65536

KEY_FILE_PATH = "file-path"
KEY_FILE_SIZE = "file-size"
KEY_HASH_VALUE = "hash-value"
KEY_COORDS_DEG = "coords-deg"
KEY_TIMESTAMP = "timestamp"
KEY_DATE_TIME = "date-time"

EXIF_DATETIME_ORIGINAL = 36867


class PhotoInfo:

    def __init__(self, file_path, file_size, hash_value, coords_deg, date_time):
        self.file_path = file_path
        self.file_size = file_size
        self.hash_value = hash_value
        self.coords_deg = coords_deg

        if date_time is not None:
            self.timestamp = date_time.timestamp
            self.date_time = date_time.format('YYYY-MM-DDTHH:mm:ss')
        else:
            self.timestamp = None
            self.date_time = None

    # creates hashmap representation for JSON export
    def to_map(self):
        return {
            KEY_FILE_PATH: self.file_path,
            KEY_FILE_SIZE: self.file_size,
            KEY_HASH_VALUE: self.hash_value,
            KEY_COORDS_DEG: self.coords_deg,
            KEY_TIMESTAMP: self.timestamp,
            KEY_DATE_TIME: self.date_time,
        }


# Traverses path recursively and import all photo information into the sqlite db for further analysis.
# This might be time consuming for huge amount of photos
def import_photos_into_db(path):
    conn = db_connect()
    map_hash_photoid = db_select_photos_hash_id(conn)
    map_path_photoid = db_select_paths_path_photoid(conn)

    all_photos = list(get_jpg_files(path))
    new_photos = list(filter(lambda p: p not in map_path_photoid, all_photos))

    count_all = len(all_photos)
    count_new = len(new_photos)

    print("Found {} new photos out of {} in path {}".format(count_new, count_all, path))

    count = 0
    for path in new_photos:
        if count % 100 == 0:
            print("Processed {} of {} files".format(count, count_new))

        count = count + 1
        info = analyse_photo(path)
        hash_value = info.hash_value

        if hash_value in map_hash_photoid:
            # photo already exists under different path
            photo_id_existing = map_hash_photoid[hash_value]
            db_insert_path(conn, photo_id_existing, path)
        else:
            # new photo
            photo_id_new = db_insert_photo(conn, info)
            map_hash_photoid[hash_value] = photo_id_new

    conn.close()


# performs geographic clustering on photo information in the sqlite db
# cluster_min_samples: minimum samples per cluster
# cluster_eps: max distance for a point to become member of a cluster
def cluster(cluster_min_samples=5, cluster_eps=2.0 / RADIUS_EARTH_KM):
    print("Start clustering")
    conn = db_connect()
    coords_map = db_select_photos_coords(conn)
    coords_rad = list(coords_map.keys())
    clustering = OPTICS(min_samples=cluster_min_samples, metric='haversine').fit(coords_rad)

    labels_dbscan = cluster_optics_dbscan(reachability=clustering.reachability_,
                                          core_distances=clustering.core_distances_,
                                          ordering=clustering.ordering_, eps=cluster_eps)

    # coords_rad_labels = zip(coords_rad, clustering.labels_)
    coords_rad_labels = zip(coords_rad, labels_dbscan)
    map_coords_deg_cluster = {coords_map[coord_rad]: label for (coord_rad, label) in coords_rad_labels}

    map_hull_points_idx = compute_hull_curves(map_coords_deg_cluster)

    db_create_clusters(conn, map_coords_deg_cluster, map_hull_points_idx)
    conn.close()
    print("Finished clustering")


# returns map with points on the hull curves with their curve position index for all clusters
def compute_hull_curves(map_coords_deg_cluster):
    print("Computing hull curves")
    map_hull_point_idx = {}
    labels = {label for label in map_coords_deg_cluster.values()}
    print("Found {} cluster labels".format(len(labels)))
    for label in labels:
        points = [[lat, lon] for (lat, lon) in map_coords_deg_cluster.keys() if
                  map_coords_deg_cluster[(lat, lon)] == label]

        hull_curve = ConvexHull(points)
        vertices = hull_curve.vertices
        n_vertices = len(vertices)
        print("Found {} points for cluster label {} with {} vertices".format(len(points), label, n_vertices))
        for i in range(n_vertices):
            idx = vertices[i]
            (lat, lon) = points[idx]
            map_hull_point_idx[(lat, lon)] = i

    return map_hull_point_idx


# analyses photo referenced by path and extracts properties (hash value, size, gps coordinates, timestamp, etc.)
# for further analysis
def analyse_photo(path):
    norm_path = normpath(path)
    info = PhotoInfo(
        norm_path,
        getsize(norm_path),
        hash_value_for_file(norm_path),
        coords(norm_path),
        date_time_original(norm_path)
    )
    return info


# computes hash value from the specified photo file
def hash_value_for_file(path):
    hash_function = sha512()
    with open(path, 'rb') as f:
        buf = f.read(BLOCK_SIZE)
        while len(buf) > 0:
            hash_function.update(buf)
            buf = f.read(BLOCK_SIZE)
    return hash_function.hexdigest()


# extracts gps coordinates from the specified photo file
def coords(path):
    try:
        gps_data = gpsphoto.getGPSData(path)
        if "Latitude" in gps_data and "Longitude" in gps_data:
            return gps_data.get("Latitude", 0.0), gps_data.get("Longitude", 0.0)
        else:
            return None
    except:
        print("Error getting GPS data from file {}".format(path))
        return None


# extracts EXIF timestamp from the specified photo file
def date_time_original(path):
    try:
        exif = Image.open(path).getexif()
        if EXIF_DATETIME_ORIGINAL in exif:
            ts_string = exif[EXIF_DATETIME_ORIGINAL]
            ts = arrow.get(ts_string, 'YYYY:MM:DD HH:mm:ss')
            return ts
        else:
            return None
    except:
        print("Error getting date_time_original from file {}".format(path))
        return None
