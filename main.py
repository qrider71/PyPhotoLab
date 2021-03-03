from pyphotolab import analyse_photo as ap


def main():
    ap.import_photos_into_db("/Users/qrider/Kamera-Uploads")
    ap.cluster()


def test():
    conn = ap.cluster()


if __name__ == "__main__":
    main()
