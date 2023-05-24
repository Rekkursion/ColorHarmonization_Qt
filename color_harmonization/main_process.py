from threading import Lock

import cv2

import color_harmonization.harmonic_template as harmonic_template
import color_harmonization.harmonize as harmonize
from enums.colors import Colors
from enums.process_status import ProcessStatus
from utils.harmonization_utils import hut_convert_image_into_hsv_w_resizing, hut_map_template_type


_PROCESS_LOCK = Lock()


# start doing the color harmonization
def do_process(win_name, img, widget, log_writer, resize_ratio, template_type):
    if img is None:
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
            
            # do color harmonization
            # harmonize.harmonize(resized_im, hsv, templ, **cfg)
            print()
            print('=====================================================')
            print()
            
            ''' done '''
            
            widget.notify_status_change(ProcessStatus.DONE)
            log_writer(f'The process of the loaded image <i>{win_name}</i> has been done.', Colors.LOG_PROCESS_DONE)

            # set the mouse callback to activate some user events
            # cv2.setMouseCallback(win_name, mouse_callback, (win_name, widget,))
        except BaseException:
            widget.notify_status_change(ProcessStatus.ERROR)
            log_writer(f'Error happened when processing color harmonization on the image: <i>{win_name}</i>.', Colors.LOG_ERROR)
    # wait for user's action to keep the cv-window
    cv2.waitKey(0)