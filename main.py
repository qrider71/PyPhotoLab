import analyse_photo as ap
import pprint as pp

from datetime import datetime


def main():
    ap.import_photos_into_db("/Users/qrider/Kamera-Uploads")
    ap.cluster()


def test():
    conn = ap.cluster()


""""
    print("Start analysis {}".format(str(datetime.now())))
    files = ap.get_files("/Users/qrider/Kamera-Uploads")
    total_count = len(files)
    count = 0
    for f in files:
        if count % 100 == 0:
            print("Processed {} of {} files".format(count, total_count))
        count = count + 1
        if f.endswith(".jpg") or f.endswith(".JPG"):
            # pp.pprint(f)
            info = ap.analyse_photo(f)
            # pp.pprint(info.to_map())
    print("Finished analysis {}".format(str(datetime.now())))
"""

if __name__ == "__main__":
    main()
