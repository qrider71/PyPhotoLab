import sqlite3
from os.path import exists

from numpy import deg2rad


# establish sqlite db connection, create new db if db does not exist
def db_connect(db_path='photos.db'):
    db_exists = exists(db_path)
    conn = sqlite3.connect(db_path)
    if not db_exists:
        db_create(conn)
    return conn


# create new sqlite database
def db_create(conn):
    with open('db_setup.sql', 'r') as sql_file:
        sql_script = sql_file.read()

    c = conn.cursor()
    c.executescript(sql_script)
    conn.commit()
    c.close()


# execute select query and return entire result set as a list
def db_select(conn, query):
    c = conn.cursor()
    c.execute(query)
    res = c.fetchall()
    c.close()
    return res


# return map with hash value/photo id pairs
def db_select_photos_hash_id(conn):
    res = db_select(conn, '''SELECT hash_value, id from photos''')
    return {h: i for (h, i) in res}


# return map with photo path/photo id pairs
def db_select_paths_path_photoid(conn):
    res = db_select(conn, '''SELECT path, photo_id from paths''')
    return {p: i for (p, i) in res}


# return map with mapping of all coordinates from radian to degree
def db_select_photos_coords(conn):
    res = db_select(conn, '''SELECT lat_deg, lon_deg from all_coords_view ''')
    return {tuple(deg2rad((lat_deg, lon_deg))): (lat_deg, lon_deg) for (lat_deg, lon_deg) in res}


# insert a new path for a photo
def db_insert_path(conn, photo_id_existing, file_path):
    c = conn.cursor()
    c.execute("INSERT INTO paths (photo_id, path) VALUES (?, ?)", (photo_id_existing, file_path))
    conn.commit()
    c.close()


# insert a new photo with its path
def db_insert_photo(conn, info):
    coords_deg = info.coords_deg
    if coords_deg is not None:
        (lat_deg, lon_deg) = coords_deg
    else:
        lat_deg = None
        lon_deg = None

    c = conn.cursor()
    c.execute('''INSERT INTO photos (
                    file_size, 
                    timestamp, 
                    date_time, 
                    lat_deg,
                    lon_deg,
                    hash_value) VALUES (?, ?, ?, ?, ?, ?)''',
              (info.file_size,
               info.timestamp,
               info.date_time,
               lat_deg,
               lon_deg,
               info.hash_value))
    conn.commit()

    c.execute('''SELECT id from photos where hash_value=:hash''', {"hash": info.hash_value})
    res = c.fetchone()
    photo_id = res[0]
    c.close()

    db_insert_path(conn, photo_id, info.file_path)
    return photo_id


# insert all coordinates with cluster labels into clusters table, coordinates are in degree
def db_create_clusters(conn, map_coords_deg_cluster):
    c = conn.cursor()
    c.execute("DELETE FROM clusters")
    for key in map_coords_deg_cluster.keys():
        label = map_coords_deg_cluster[key].item()
        (lat_deg, lon_deg) = key
        c.execute("INSERT INTO clusters (label, lat_deg, lon_deg) VALUES (?, ?, ?)", (label, lat_deg, lon_deg))
        conn.commit()
    c.close()
