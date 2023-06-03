import os

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow

from enums.process_status import ProcessStatus
from loaded_image_obj import LoadedImagesDict
from ui.qt_ui.loaded_images_list.loaded_images_list_widget import LoadedImagesListWidget
from ui.qt_ui.log_area.log_area import LogArea
from ui.qt_ui.main_window.main_window_actions import *


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # load the UI
        uic.loadUi('./ui/qt_ui/main_window/main_window.ui', self)
        # the list-widget for showing all loaded images
        self.lis_imgs = LoadedImagesListWidget(self.write_log)
        self.main_layout.addWidget(self.lis_imgs)
        # the text-browser for logs
        self.log_area = LogArea()
        self.main_layout.addWidget(self.log_area)
        # initialize the events
        self.init_events()
        # the counter for counting the number of opened images via clipboard
        self.clipboard_counter = 0
        # accept drag-n-drop files
        self.setAcceptDrops(True)

    # initialize events
    def init_events(self):
        self.action_load_from_local.triggered.connect(action_load_from_local_triggered(self))
        self.action_load_from_url.triggered.connect(action_load_from_url_triggered(self))
        self.action_load_from_clipboard.triggered.connect(action_load_from_clipboard_triggered(self))
        self.action_save_all.triggered.connect(action_save_all_triggered(self))
        self.action_save_selected.triggered.connect(action_save_selected_triggered(self))
        self.action_open_settings.triggered.connect(action_action_open_settings_triggered(self))
        self.action_open_res_dir.triggered.connect(action_open_res_dir_triggered(self))
        self.action_open_vis_dir.triggered.connect(action_open_vis_dir_triggered(self))
    
    # a callback when image loading is done
    def finish_image_loading(self, win_name, img):
        # win_name = self.lis_imgs.deduplicate_win_name(win_name)
        widget = self.lis_imgs.push_back(win_name, img)
        widget.notify_status_change(ProcessStatus.LOADED)
        LoadedImagesDict.add_processed_image(win_name, img)
        return True

    # write a single log and the text-color at the log-area (text-browser)
    def write_log(self, text, color=Colors.LOG_GENERAL):
        log = '<span style="color: rgb{};"> &gt; {}</span>'.format(str(color), f'<strong>{text}</strong>')
        self.log_area.append(log)

    # https://gist.github.com/peace098beat/db8ef7161508e6500ebe
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        file_paths = [u.toLocalFile() for u in event.mimeData().urls()]
        for fpath in file_paths:
            if os.path.isfile(fpath):
                im = gut_load_image(fpath)
                if im is not None:
                    self.write_log(f'The image <i>{fpath}</i> has been loaded from local by drag-and-drop.', Colors.LOG_LOAD_IMAGE)
                    self.finish_image_loading(fpath, im)
                else:
                    self.write_log(f'The file <i>{fpath}</i> is not a legal image.', Colors.LOG_ERROR)
            else:
                self.write_log(f'The path <i>{fpath}</i> is not a legal image file path.', Colors.LOG_ERROR)
