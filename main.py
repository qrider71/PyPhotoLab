from pyphotolab import analyse_photo as ap
from pyphotolab.geojson import *
from pyphotolab.config import *


def main():
    conf_photo_import_path = get_photo_import_path()
    conf_cluster_min_samples = get_cluster_min_samples()
    conf_cluster_eps = get_cluster_eps()

    # ap.import_photos_into_db(conf_photo_import_path)
    ap.cluster(cluster_min_samples=conf_cluster_min_samples, cluster_eps=conf_cluster_eps)
    create_geojson_file()


if __name__ == "__main__":
    main()
