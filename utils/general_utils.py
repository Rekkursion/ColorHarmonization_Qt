import os
from pathlib import Path
import platform
import subprocess

import cv2
import numpy as np


# resize an image by the given ratio
def gut_resize_by_ratio(im, ratio):
    if ratio == 1:
        return im
    new_h = int(im.shape[0] * ratio)
    new_w = int(im.shape[1] * ratio)
    return cv2.resize(im, (new_w, new_h,))


# load an image with in-path unicode supported
def gut_load_image(fpath, flags=-1):
    return cv2.imdecode(np.fromfile(str(fpath), dtype=np.uint8), flags)


# get the extension (suffix) of an image by its filename/path
def gut_get_ext(fpath):
    return Path(fpath).suffix


# replace the extension of a filename/path
def gut_replace_ext(fpath, ext):
    return str(Path(fpath).with_suffix(ext))


# https://stackoverflow.com/questions/6631299/python-opening-a-folder-in-explorer-nautilus-finder
def gut_open_directory_in_explorer(path):
    if os.path.exists(path):
        if platform.system() == 'Windows':
            os.startfile(os.path.abspath(path))
        elif platform.system() == 'Darwin':
            subprocess.Popen(['open', path,])
        else:
            subprocess.Popen(['xdg-open', path,])
        return True
    return False
