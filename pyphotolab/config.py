import json

from numpy.distutils import read_config

KEY_PHOTO_IMPORT_PATH = "photo-import-path"
KEY_CLUSTER_MIN_SAMPLES = "cluster-min-samples"
KEY_CLUSTER_EPS = "cluster-eps"

RADIUS_EARTH_KM = 6371.0


def read_config_file():
    with open('config.json') as f:
        data = json.load(f)
        print("Config: {}".format(str(data)))
        return data


config = read_config_file()


def get_photo_import_path(data=config):
    return data.get(KEY_PHOTO_IMPORT_PATH, "./photos")


def get_cluster_min_samples(data=config):
    return data.get(KEY_CLUSTER_MIN_SAMPLES, 5)


def get_cluster_eps(data=config):
    return data.get(KEY_CLUSTER_EPS, 2.0) / RADIUS_EARTH_KM
