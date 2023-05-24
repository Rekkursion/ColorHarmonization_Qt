import cv2
import numpy as np

from utils.general_utils import gut_resize_by_ratio


TEMPL_TYPES_MAPPING = ('i', 'V', 'L', 'I', 'T', 'Y', 'X',)


# map the template type as an integer into the respective character
def hut_map_template_type(templ_type):
    if isinstance(templ_type, int):
        return TEMPL_TYPES_MAPPING[templ_type]
    return templ_type


# convert an image into the hsv color space
def hut_convert_image_into_hsv_w_resizing(im, ratio=1):
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


# draw the ring-shaped histogram
def hut_draw_ring_shaped_histogram(hist, templ=None, alpha=0., shape_of_hist='sector'):
    assert shape_of_hist in ('sector', 'line',)

    # some controlling parameters for the visualization
    W, H = 512, 512
    RADIUS = 233
    INNER_CIRCLE_RADIUS = 115
    HIST_COLOR = (127, 127, 127, 255,)

    # print(np.where(hist == np.max(hist)))
    # print(hist)
    
    # the canvas for visualizing
    vis = np.full((H, W, 4,), 255, dtype=np.uint8)

    # draw the color-gradient circle
    for hue_idx, _ in enumerate(hist):
        b, g, r = cv2.cvtColor(np.array((((hue_idx, 255, 255,),),), dtype=np.uint8), cv2.COLOR_HSV2BGR).reshape(-1)
        # color = (int(r), int(g), int(b), 255,)
        color = (int(b), int(g), int(r), 255,)
        rad = np.deg2rad(hue_idx * 2.)
        x2, y2 = int(RADIUS * np.cos(rad) + W / 2.), int(RADIUS * np.sin(rad) + H / 2.)
        cv2.line(vis, (W // 2, H // 2,), (x2, y2,), color=color, thickness=7)
    # overdraw a pure white circle to make the color-gradient a ring
    cv2.circle(vis, (W // 2, H // 2,), INNER_CIRCLE_RADIUS, color=(255,) * 4, thickness=-1)
    cv2.circle(vis, (W // 2, H // 2,), RADIUS, color=(255,) * 4, thickness=10)
    # draw the histogram inside the ring (needed a second for-loop because we have to overdraw a white circle in prior)
    pillar_max_height = INNER_CIRCLE_RADIUS - 10
    normalized_hist = (hist - np.min(hist)) / np.ptp(hist) * pillar_max_height
    for hue_idx, normalized_count_of_hue in enumerate(normalized_hist):
        if normalized_count_of_hue > 0.:
            rad = np.deg2rad(hue_idx * 2.)
            x2, y2 = int(INNER_CIRCLE_RADIUS * np.cos(rad) + W / 2.), int(INNER_CIRCLE_RADIUS * np.sin(rad) + H / 2.)
            x1 = int((INNER_CIRCLE_RADIUS - normalized_count_of_hue) * np.cos(rad) + W / 2.)
            y1 = int((INNER_CIRCLE_RADIUS - normalized_count_of_hue) * np.sin(rad) + H / 2.)
            if shape_of_hist == 'line':
                cv2.line(vis, (x1, y1,), (x2, y2,), color=HIST_COLOR, thickness=2)
            else: # elif shape_of_hist == 'sector':
                cv2.ellipse(
                    vis,
                    (x1, y1,),
                    (int(normalized_count_of_hue), int(normalized_count_of_hue),),
                    0,
                    hue_idx * 2. - 4.,
                    hue_idx * 2. + 4.,
                    color=HIST_COLOR,
                    thickness=-1,
                )
    # draw some texts
    for deg in range(0, 360, 90):
        rad = np.deg2rad(deg)
        x, y = int(RADIUS * np.cos(rad) + W / 2.), int(RADIUS * np.sin(rad) + H / 2.)
        if deg == 180:
            x -= 20
        if deg == 90:
            x -= 12; y += 10
        if deg == 270:
            x -= 15
        cv2.putText(vis, f'{deg // 2}', org=(x, y,), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=.5, color=(0,) * 4, thickness=2)
    # draw the sectors' areas if which type of the template is provided
    if templ is not None:
        # sectors_vis = np.full((H, W, 4,), 255, dtype=np.uint8)
        sectors_vis = hut_add_opaque_channel(np.zeros((H, W, 3,), dtype=np.uint8))
        for sector in templ.sectors:
            cv2.ellipse(
                sectors_vis,
                (W // 2, H // 2,),
                (RADIUS, RADIUS,),
                0,
                sector.get_start_deg(offset=alpha) * 2.,
                (sector.get_start_deg(offset=alpha) + sector.range_deg) * 2.,
                color=(200, 200, 200, 255,),
                thickness=-1,
            )
        vis_w_sectors = cv2.addWeighted(vis, .6, sectors_vis, .4, gamma=.0)
        vis = np.hstack((vis, vis_w_sectors,))
    return vis


# visualize the histograms on a color-gradient ring
def hut_visualize_histogram(hist, templ=None, alpha=0., raw_im=None, show=False, save_path=None):
    # create the ring-shaped histogram visualization
    vis = hut_draw_ring_shaped_histogram(hist, templ, alpha)

    # stack the raw image, if provided
    if raw_im is not None:
        resize_ratio = vis.shape[0] / raw_im.shape[0]
        stacked_im = cv2.resize(raw_im, (int(raw_im.shape[1] * resize_ratio), vis.shape[0],))
        stacked_im = hut_add_opaque_channel(stacked_im)
        vis = np.hstack((vis, stacked_im,))

    # show the histogram visualization
    if save_path is not None:
        cv2.imwrite(str(save_path), vis)
    if show:
        cv2.imshow('histogram', vis)
        cv2.waitKey(0)


# calculate the arc-length
def hut_calc_arc_len(deg1, deg2=None, r=10.):
    deg1 = hut_canonicalize_deg(deg1)
    if deg2 is None:
        return 2. * np.pi * r * ((abs(deg1) % 180) / 180.)
    deg2 = hut_canonicalize_deg(deg2)
    return 2. * np.pi * r * ((abs(deg1 - deg2) % 180) / 180.)


# canonicalize an angle in degree into a certain range
def hut_canonicalize_deg(deg, max_range=180.):
    return float(deg) % max_range
    # if deg >= 0:
    #     ret = deg % max_range
    # else:
    #     gang = (abs(deg) - 1) // max_range + 1
    #     ret = (deg + (max_range * gang)) % max_range
    # return ret


# add the opaque channel to a 3-channel image (and it becomes 4-channel)
def hut_add_opaque_channel(im):
    if im.ndim == 3 and im.shape[-1] == 3:
        return np.concatenate((im, np.full((*im.shape[: 2], 1), 255, dtype=np.uint8),), axis=-1)
    return im
