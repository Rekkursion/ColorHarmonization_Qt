from threading import Lock

import cv2

from enums.colors import Colors
from enums.process_status import ProcessStatus


_PROCESS_LOCK = Lock()


# start doing the color harmonization
def do_process(win_name, img, widget, log_writer, resize_ratio, template_type):
    if img is None:
        return
    # acquire the lock to avoid race-condition and release it after finishing the task (before the key-waiting)
    with _PROCESS_LOCK:
        try:
            # start

            print(f'| PROCESS | {win_name} | {img.shape} | {resize_ratio:.2f} | {template_type} |')
            widget.notify_status_change(ProcessStatus.PROCESSING)

            # harmonize

            # ...
            
            # done
            
            widget.notify_status_change(ProcessStatus.DONE)
            log_writer(f'The process of the loaded image <i>{win_name}</i> has been done.', Colors.LOG_PROCESS_DONE)
            # set the mouse callback to activate by-user events
            # cv2.setMouseCallback(win_name, mouse_callback, (win_name, widget,))
        except BaseException:
            widget.notify_status_change(ProcessStatus.ERROR)
            log_writer(f'Error happened when processing color harmonization on the image: <i>{win_name}</i>.', Colors.LOG_ERROR)
    # wait for user's action to keep the cv-window
    cv2.waitKey(0)