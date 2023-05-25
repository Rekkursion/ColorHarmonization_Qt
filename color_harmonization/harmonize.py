import copy
from pathlib import Path

import cv2
import networkx as nx
import numpy as np
import scipy

from color_harmonization.harmonic_template import HarmonicTemplate_Base
from utils.general_utils import gut_resize_by_ratio
from utils.harmonization_utils import (
    hut_add_opaque_channel,
    hut_calc_arc_len,
    hut_canonicalize_deg,
    hut_draw_ring_shaped_histogram,
    hut_visualize_histogram,
)


# calculate the histogram of hues from an image in the hsv space
def _calc_hue_histogram(hsv_im):
    # take out hues only from the hsv space
    hues = hsv_im[:, :, 0].reshape(-1)
    # get the histogram on hues (the range of hues is 0 to 180)
    hist, _ = np.histogram(hues, bins=np.arange(181, dtype=np.int32))
    if len(hist) < 180:
        hist = np.concatenate((hist, np.zeros((180 - len(hist),), dtype=np.int32)), axis=0)
    return hist


# do an optimization for finding an alpha value that could minimize the distance
def _search_alpha_value(hsv, templ: HarmonicTemplate_Base):
    print('| Searching for ALPHA... |')
    flattened_hsv = hsv.reshape(-1, 3)
    H = flattened_hsv[:, 0]
    S = flattened_hsv[:, 1]

    F = lambda alpha: np.mean(np.array([templ.get_min_dis(h, alpha)[0] for h in H]) * S)
    x_root = scipy.optimize.brent(F, brack=(0., 180.,))
    x_root = hut_canonicalize_deg(x_root)
    # x_root = scipy.optimize.brentq(F, a=-180., b=180.)
    print(f'| ALPHA = {x_root} (in the range of [0, 180]) |')
    return x_root


# naively find the closest borders of sectors (without the help of the graph-cut method)
def _find_closest_borders_of_sectors_naively(hsv, templ: HarmonicTemplate_Base, alpha):
    # V: the pre-labelled map
    V = np.full(hsv.shape[: 2], .5, dtype=np.float32)
    # D: the minimal distances corresponding to the labels
    D = np.full(hsv.shape[: 2], 0., dtype=np.float32)
    for (y, x,), hue in np.ndenumerate(hsv[:, :, 0]):
        if not templ.is_in(hue, alpha)[0]:
            min_dis, move_dir = templ.get_min_dis(hue, alpha)
            D[y, x] = min_dis
            V[y, x] = 0 if move_dir == -1 else 1
    return V, D


def _apply_graph_cut(hsv, templ: HarmonicTemplate_Base, alpha, _lambda, V, D):

    ''' step 1. build a graph '''
    
    # construct a graph
    g = nx.DiGraph()
    # build all n-links
    for ((y, x,), hue,), ((_, _,), sat,) in zip(np.ndenumerate(hsv[:, :, 0]), np.ndenumerate(hsv[:, :, 1])):
        id = y * hsv.shape[1] + x
        g.add_node(id)
        if y > 0:
            neighbour_id = (y - 1) * hsv.shape[1] + x
            # B (E2) function
            edge_weight = (1 if V[y, x] != V[y - 1, x] else 0) * max(sat, hsv[y - 1, x, 1]) / \
                            (hut_calc_arc_len(hue, hsv[y - 1, x, 0]) + 1e-6)
            g.add_edge(id, neighbour_id, capacity=edge_weight)
            g.add_edge(neighbour_id, id, capacity=edge_weight)
        if x > 0:
            neighbour_id = y * hsv.shape[1] + (x - 1)
            # B (E2) function
            edge_weight = (1 if V[y, x] != V[y, x - 1] else 0) * max(sat, hsv[y, x - 1, 1]) / \
                            (hut_calc_arc_len(hue, hsv[y, x - 1, 0]) + 1e-6)
            g.add_edge(id, neighbour_id, capacity=edge_weight)
            g.add_edge(neighbour_id, id, capacity=edge_weight)
    # calculate the K-value
    capacities = nx.get_edge_attributes(g, 'capacity')
    K = 0.
    for (y, x,), hue in np.ndenumerate(hsv[:, :, 0]):
        id = y * hsv.shape[1] + x
        edges = g.edges(id)
        k = sum([capacities[e] for e in edges])
        if k > K:
            K = k
    K += 1.
    # build all links to S and T
    g.add_node('S')
    g.add_node('T')
    for (y, x,), hue in np.ndenumerate(hsv[:, :, 0]):
        id = y * hsv.shape[1] + x
        # move clockwisely
        if V[y, x] == 1:
            edge_weight_S = K
            edge_weight_T = 0.
        # move counterclockwisely
        elif V[y, x] == 0:
            edge_weight_S = 0.
            edge_weight_T = K
        # not moving (V[y, x] == .5)
        else:
            # R (E1) function
            edge_weight_S = _lambda * D[y, x] * hsv[y, x, 1]
            edge_weight_T = edge_weight_S
        g.add_edge('S', id, capacity=edge_weight_S)
        g.add_edge(id, 'T', capacity=edge_weight_T)
    
    ''' Step 2. exert min-cut algorithm '''
    
    print(f'| Start MIN-CUT... |')
    cut_value, partition = nx.minimum_cut(g, 'S', 'T')
    # S is in reachable (clockwise-moving); T is in non-reachable (counterclockwise-moving)
    reachable, non_reachable = partition
    # cutset = set()
    # for u, nbrs in ((n, g[n]) for n in reachable):
    #     cutset.update((u, v) for v in nbrs if v in non_reachable)
    print(f'Reachable     -> {len(reachable)}')
    print(f'Non-reachable -> {len(non_reachable)}')

    ''' Step 3. do color-shifting '''
    gaussian_fn = lambda x, mu, sigma: 1. / (np.sqrt(2. * np.pi) * sigma) * np.exp(-np.power((x - mu) / sigma, 2.) / 2.)
    ret_hsv = copy.deepcopy(hsv)
    for (y, x,), hue in np.ndenumerate(hsv[:, :, 0]):
        id = y * hsv.shape[1] + x
        assert (id in reachable) ^ (id in non_reachable)
        if id in reachable:
            _, sect = templ.find_nearest_sector_by_certain_dir(hue, alpha, move_dir=1)
        if id in non_reachable:
            _, sect = templ.find_nearest_sector_by_certain_dir(hue, alpha, move_dir=0)
        
        c = sect.centre_of_arc + alpha
        w = sect.arc_len
        g = gaussian_fn(hut_calc_arc_len(hue, c), mu=0., sigma=.1)

        new_hue = int(c + (w / 2.) * (1. - g))
        ret_hsv[y, x, 0] = new_hue
    
    return ret_hsv


# do color harmonization on an image in the hsv space with a specific harmonic template
def harmonize(
        raw_im,
        hsv,
        templ: HarmonicTemplate_Base,
        vis_save_path,
        result_save_path,
        _lambda=.5,
        mode='graph_cut',
        **_,
):
    assert mode in ('naive', 'graph_cut',), 'The processing mode must be either "naive" or "graph_cut".'

    vis_save_path = Path(vis_save_path)
    vis_parent, vis_stem, vis_ext = vis_save_path.parent, vis_save_path.stem, vis_save_path.suffix

    # get the histogram on hues (hue: 0 - 180, sat: 0 - 255, val: 0 - 255,)
    hue_hist = _calc_hue_histogram(hsv)
    # visualize the histogram
    hut_visualize_histogram(hue_hist, templ, 0., raw_im, save_path=str(vis_parent / f'{vis_stem}_1-raw{vis_ext}'), show=False)

    # search for the best alpha
    alpha = _search_alpha_value(hsv, templ)
    # templ.rotate_sectors(alpha)
    hut_visualize_histogram(hue_hist, templ, alpha, raw_im, save_path=str(vis_parent / f'{vis_stem}_2-sectors-rotated{vis_ext}'), show=False)

    # pre-select the nearest borders of sectors
    V, D = _find_closest_borders_of_sectors_naively(hsv, templ, alpha)
    print('0.5', np.where(V == .5)[0].__len__())
    print('  0', np.where(V == 0)[0].__len__())
    print('  1', np.where(V == 1)[0].__len__())
    print('all', np.prod(V.shape))

    # optimize the color-shifting with the help of the graph-cut image segmentation method
    new_hsv = _apply_graph_cut(hsv, templ, alpha, _lambda, V, D)

    # re-construct the color-harmonized image
    new_im = cv2.cvtColor(new_hsv, cv2.COLOR_HSV2BGR)
    ret_im = copy.deepcopy(new_im)
    new_hsv = cv2.cvtColor(new_im, cv2.COLOR_BGR2HSV)
    new_hue_hist = _calc_hue_histogram(new_hsv)
    hut_visualize_histogram(new_hue_hist, templ, alpha, new_im, save_path=str(vis_parent / f'{vis_stem}_3-harmonized{vis_ext}'), show=False)

    # do visualization
    raw_hist_vis = hut_draw_ring_shaped_histogram(hue_hist, templ, alpha)
    new_hist_vis = hut_draw_ring_shaped_histogram(new_hue_hist, templ, alpha)
    vis_h = max(raw_im.shape[0], 400)
    ratio = vis_h / raw_hist_vis.shape[0]
    raw_hist_vis = gut_resize_by_ratio(raw_hist_vis, ratio=ratio)
    new_hist_vis = gut_resize_by_ratio(new_hist_vis, ratio=ratio)
    if vis_h != raw_im.shape[0]:
        raw_im = cv2.resize(raw_im, (int(raw_hist_vis.shape[0] / raw_im.shape[0] * raw_im.shape[1]), raw_hist_vis.shape[0],))
        new_im = cv2.resize(new_im, (int(raw_hist_vis.shape[0] / new_im.shape[0] * new_im.shape[1]), raw_hist_vis.shape[0],))
    raw_im = hut_add_opaque_channel(raw_im)
    new_im = hut_add_opaque_channel(new_im)
    final_vis = np.vstack((
        np.hstack((raw_hist_vis, raw_im,)),
        hut_add_opaque_channel(np.zeros((10, raw_hist_vis.shape[1] + raw_im.shape[1], 3,), dtype=np.uint8)),
        np.hstack((new_hist_vis, new_im,)),
    ))
    cv2.imwrite(str(vis_parent / f'{vis_stem}_4-final{vis_ext}'), final_vis)
    cv2.imshow('Result', final_vis)
    cv2.waitKey(0)
    
    # save the result
    cv2.imwrite(str(result_save_path), ret_im)

    return ret_im
