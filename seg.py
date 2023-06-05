# https://opencv-python-tutorials.readthedocs.io/zh/latest/4.%20OpenCV%E4%B8%AD%E7%9A%84%E5%9B%BE%E5%83%8F%E5%A4%84%E7%90%86/4.16.%20%E5%9F%BA%E4%BA%8EGrabCut%E7%AE%97%E6%B3%95%E7%9A%84%E4%BA%A4%E4%BA%92%E5%BC%8F%E5%89%8D%E6%99%AF%E6%8F%90%E5%8F%96/
# https://hackmd.io/@cws0701/SJit0xQhc

import cv2
import numpy as np
from matplotlib import pyplot as plt


def apply_interactive_segmentation(fpath_or_im, mode, win_name='', plotout=False):
    # img = cv2.imread('./resource/test_img/fig7a.png', -1)
    if isinstance(fpath_or_im, str):
        img = cv2.imread(fpath_or_im, -1)
    else:
        img = fpath_or_im
    
    if img.shape[-1] == 4:
        img = img[:, :, : 3]
    mask = np.zeros(img.shape[: 2], np.uint8)
    
    # let user select the roi
    # rect = (0, 0, img.shape[1] - 1, img.shape[0] - 1,)
    rect = cv2.selectROI('Select the bounding box of the foreground', img)
    cv2.destroyWindow('Select the bounding box of the foreground')

    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)

    cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 8, cv2.GC_INIT_WITH_RECT)
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype(np.uint8)

    if plotout:
        vis = np.tile(np.expand_dims(mask2, axis=2), reps=(1, 1, 3,)) * 255
        vis = np.hstack([vis, img, (img & (vis if mode == 'background' else 255 - vis)),], dtype=np.uint8)
        cv2.imshow(f'Segmentation: mode={mode} name={win_name}', vis)
    
    return mask2


if __name__ == '__main__':
    apply_interactive_segmentation(
        './resource/test_img/fig7a.png',
        'background',
        plotout=True,
    )
