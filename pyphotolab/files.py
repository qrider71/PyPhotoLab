from os import listdir
from os.path import normpath, isfile, isdir, join


def get_jpg_files(path):
    return filter(lambda f: is_jpeg(f), get_files(path))


def is_jpeg(f):
    f_lower = f.lower()
    return f_lower.endswith("jpg") or f_lower.endswith("jpeg")


def get_files(path):
    npath = normpath(path)
    if isfile(npath):
        return [npath]
    elif isdir(npath):
        return get_files_rec([], npath)


def get_files_rec(files, path):
    if isfile(path):
        files.append(path)
    elif isdir(path):
        contents = listdir(path)
        for f in contents:
            files = get_files_rec(files, join(path, f))
    return files
