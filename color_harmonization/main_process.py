from pathlib import Path
from threading import Lock

import cv2

import color_harmonization.harmonic_template as harmonic_template
import color_harmonization.harmonize as harmonize
from enums.colors import Colors
from enums.process_status import ProcessStatus
from ui.qt_ui.global_config_panel.global_config_panel import GlobalConfigPanel
from utils.harmonization_utils import hut_convert_image_into_hsv_w_resizing, hut_map_template_type
from loaded_image_obj import LoadedImagesDict


_PROCESS_LOCK = Lock()


# start doing the color harmonization
def do_process(win_name, img, widget, log_writer, resize_ratio, template_type):
    if img is None:
        return
    if widget.process_status in (ProcessStatus.ERROR, ProcessStatus.LOADING, ProcessStatus.PROCESSING,):
        return
    # acquire the lock and release it after finishing the task (before the key-waiting)
    with _PROCESS_LOCK:
        try:
            ''' start '''

            print(f'| PROCESS | {win_name} | {img.shape} | {resize_ratio:.2f} | {template_type} |')
            widget.notify_status_change(ProcessStatus.PROCESSING)

            ''' harmonize '''
            
            # convert the image into hsv color space also apply resizing
            resized_im, hsv = hut_convert_image_into_hsv_w_resizing(img, ratio=resize_ratio)
            # choose a harmonic template
            t_type = hut_map_template_type(template_type)
            try:
                templ = getattr(harmonic_template, f'Template_{t_type}')()
            except AttributeError:
                print(f'No such template (type-{t_type}) existed.')
            
            print(f'| SHAPE (AFT RSZ) = {hsv.shape} | '
                  f'# PIXELS = {hsv.shape[0] * hsv.shape[1]} | TEMPLATE-TYPE = {t_type} |')
            
            # tackle w/ paths
            fname = f'{Path(win_name).stem}_ratio={resize_ratio:.2f}_type={template_type}{Path(win_name).suffix}'
            save_res_path = Path(GlobalConfigPanel.save_res_dir, fname)
            save_vis_path = Path(GlobalConfigPanel.save_vis_dir, fname)
            save_res_path.parent.mkdir(parents=True, exist_ok=True)
            save_vis_path.parent.mkdir(parents=True, exist_ok=True)

            # do color harmonization
            harmonized = harmonize.harmonize(
                resized_im, hsv, templ,
                vis_save_path=save_vis_path,
                result_save_path=save_res_path,
            )
            # update the processed image
            LoadedImagesDict.update_processed_image(win_name, harmonized)
            print()
            print('=====================================================')
            print()
            
            ''' done '''
            
            widget.notify_status_change(ProcessStatus.DONE)
            log_writer(f'The process of the loaded image <i>{win_name}</i> has been done.', Colors.LOG_PROCESS_DONE)

            # set the mouse callback to activate some user events
            # cv2.setMouseCallback(win_name, mouse_callback, (win_name, widget,))
        except BaseException as e:
            widget.notify_status_change(ProcessStatus.ERROR)
            log_writer(f'Error happened when processing color harmonization on the image <i>{win_name}</i>: {e}', Colors.LOG_ERROR)
    # wait for user's action to keep the cv-window
    cv2.waitKey(0)