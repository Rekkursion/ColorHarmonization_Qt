from pathlib import Path
from threading import Lock

import cv2
from PyQt5 import QtCore

import color_harmonization.harmonic_template as harmonic_template
import color_harmonization.harmonize as harmonize
from enums.colors import Colors
from enums.process_status import ProcessStatus
from loaded_image_obj import LoadedImagesDict
from ui.qt_ui.global_config_panel.global_config_panel import GlobalConfigPanel
from utils.general_utils import gut_load_image
from utils.harmonization_utils import hut_convert_image_into_hsv_w_resizing, hut_map_template_type, TEMPL_TYPES_MAPPING


_PROCESS_LOCK = Lock()


class ProcessThread(QtCore.QThread):
    signal_process_done = QtCore.pyqtSignal(ProcessStatus, str, tuple)

    def __init__(self, parent, target, args, kwargs):
        super().__init__(parent)
        self.target = target
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        self.target(
            self,
            *self.args,
            **self.kwargs,
        )


# start doing the color harmonization
def do_process(curr_thread, win_name, img, widget, resize_ratio, template_type, ref_im_fpath=None):
    if img is None:
        return
    if widget.process_status in (ProcessStatus.ERROR, ProcessStatus.LOADING, ProcessStatus.PROCESSING,):
        return
    # acquire the lock and release it after finishing the task (before the key-waiting)
    if _PROCESS_LOCK.locked():
        curr_thread.signal_process_done.emit(
            ProcessStatus.WAITING,
            f'Waiting for another harmonization done for the selected one <i>{win_name}</i>.',
            Colors.LOG_WARNING,
        )
    with _PROCESS_LOCK:
        try:
            ''' start '''

            print(f'| PROCESS | {win_name} | {img.shape} | {resize_ratio:.2f} | {template_type} |')
            widget.notify_status_change(ProcessStatus.PROCESSING)

            ''' harmonize '''
            
            # convert the image into hsv color space also apply resizing
            resized_im, hsv = hut_convert_image_into_hsv_w_resizing(img, ratio=resize_ratio)
            if ref_im_fpath is not None:
                ref_im = gut_load_image(ref_im_fpath)
                ref_im = cv2.resize(ref_im, (resized_im.shape[1], resized_im.shape[0],))
                ref_im, ref_hsv = hut_convert_image_into_hsv_w_resizing(ref_im)
                print(f'| REF = {ref_im_fpath} | ', end='')
            else:
                ref_im, ref_hsv = None, None
                print(f'| REF = NONE | ', end='')

            # choose a harmonic template
            types_list = tuple(range(7)) if template_type == 7 else (template_type,)
            templ_list = []
            for _t in types_list:
                t_type = hut_map_template_type(_t)
                try:
                    templ_list.append(getattr(harmonic_template, f'Template_{t_type}')())
                except AttributeError:
                    print(f'No such template (type-{t_type}) existed.', end='')
            
            print(f'| SHAPE (AFT RSZ) = {hsv.shape} | '
                  f'# PIXELS = {hsv.shape[0] * hsv.shape[1]} | TEMPLATE-TYPE = {"AUTO" if template_type == 7 else t_type} |')
            
            # tackle w/ paths
            fname = f'{Path(win_name).stem}_ratio={resize_ratio:.2f}_type={template_type}{Path(win_name).suffix}'
            save_res_path = Path(GlobalConfigPanel.save_res_dir, fname)
            save_vis_path = Path(GlobalConfigPanel.save_vis_dir, fname)
            save_res_path.parent.mkdir(parents=True, exist_ok=True)
            save_vis_path.parent.mkdir(parents=True, exist_ok=True)
            LoadedImagesDict.update_save_path(win_name, str(save_res_path))

            # do color harmonization
            harmonized = harmonize.harmonize(
                resized_im, hsv, templ_list,
                vis_save_path=save_vis_path,
                result_save_path=save_res_path,
                ref_im=ref_im,
                ref_hsv=ref_hsv,
            )
            # update the processed image
            LoadedImagesDict.update_processed_image(win_name, harmonized)
            print()
            print('=====================================================')
            print()
            
            ''' done '''

            curr_thread.signal_process_done.emit(
                ProcessStatus.DONE,
                f'The process of the loaded image <i>{win_name}</i> has been done.',
                Colors.LOG_PROCESS_DONE,
            )

            # set the mouse callback to activate some user events
            # cv2.setMouseCallback(win_name, mouse_callback, (win_name, widget,))
        except BaseException as e:
            curr_thread.signal_process_done.emit(
                ProcessStatus.ERROR,
                f'Error happened when processing color harmonization on the image <i>{win_name}</i>: {e}',
                Colors.LOG_ERROR,
            )
    # wait for user's action to keep the cv-window
    cv2.waitKey(0)