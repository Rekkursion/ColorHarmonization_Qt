import json
from pathlib import Path

import cv2
import numpy as np


# resize an image by the given ratio
def gut_resize_by_ratio(im, ratio):
    if ratio == 1:
        return im
    new_h = int(im.shape[0] * ratio)
    new_w = int(im.shape[1] * ratio)
    return cv2.resize(im, (new_w, new_h,))


# load an image with in-path unicode supported and convert it into the hsv color space
def gut_load_image_into_hsv(fpath, flags=-1, ratio=1):
    try:
        # load the image
        im = gut_load_image(fpath, flags)
        # do resizing first, if intended
        im = gut_resize_by_ratio(im, ratio)

        # ensure the image is in the shape of [H, W, 3]
        if im.ndim == 2:
            im = np.tile(np.expand_dims(im, axis=2), reps=(1, 1, 3,))
        if im.shape[-1] == 1:
            im = np.tile(im, reps=(1, 1, 3,))
        if im.shape[-1] == 4:
            im = im[:, :, : -1]
        assert im.ndim == 3 and im.shape[-1] == 3, 'Unsupported image format.'

        # convert the image from bgr space to hsv space
        hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
        return im, hsv
    except FileNotFoundError:
        print(f'File {str(fpath)} not found.')


# load an image with in-path unicode supported
def gut_load_image(fpath, flags=-1):
    return cv2.imdecode(np.fromfile(str(fpath), dtype=np.uint8), flags)


# get the extension (suffix) of an image by its filename/path
def gut_get_ext(fpath):
    return Path(fpath).suffix


# replace the extension of a filename/path
def gut_replace_ext(fpath, ext):
    return str(Path(fpath).with_suffix(ext))
