from pyphotolab import analyse_photo as ap
from pyphotolab.util import *
from pyphotolab.geojson import *


def main():
    # ap.import_photos_into_db("/Users/qrider/Kamera-Uploads")
    # ap.cluster()
    test()


def test():
    ap.cluster()
    create_geojson_file()


if __name__ == "__main__":
    main()
