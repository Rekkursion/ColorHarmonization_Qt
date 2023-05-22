from threading import Thread

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow

from color_harmonization.main_process import do_process as do_color_harmonization_process
from enums.process_status import ProcessStatus
from loaded_image_obj import LoadedImagesDict
from ui.qt_ui.loaded_images_list.loaded_images_list_widget import LoadedImagesListWidget
from ui.qt_ui.log_area.log_area import LogArea
from ui.qt_ui.main_window.main_window_actions import *


class MainWindow(QMainWindow):
    """
        action_load_from_local:         the action for loading the image from local
        action_load_from_url:           the action for loading the image from a particular url
        action_load_from_clipboard:     the action for loading the image from the clipboard
        action_save_all:                the action for saving all the processed images to a directory
        action_save_selected:           the action for saving the selected images to a directory
        lis_imgs:                       the list-widget for showing all opened images
    """
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

    # initialize events
    def init_events(self):
        self.action_load_from_local.triggered.connect(action_load_from_local_triggered(self))
        self.action_load_from_url.triggered.connect(action_load_from_url_triggered(self))
        self.action_load_from_clipboard.triggered.connect(action_load_from_clipboard_triggered(self))
        self.action_save_all.triggered.connect(action_save_all_triggered(self))
        self.action_save_selected.triggered.connect(action_save_selected_triggered(self))
        self.action_open_settings.triggered.connect(action_action_open_settings_triggered(self))
    
    # a callback when image loading is done
    def finish_image_loading(self, win_name, img):
        win_name = self.lis_imgs.deduplicate_win_name(win_name)
        widget = self.lis_imgs.push_back(win_name, img)
        widget.notify_status_change(ProcessStatus.LOADED)
        LoadedImagesDict.add_processed_image(win_name, img, img)
        return True

    # start the process a particular image
    # def start_process(self, win_name, img):
    #     Thread(
    #         target=do_color_harmonization_process,
    #         name=win_name,
    #         daemon=True,
    #         args=(win_name, img, widget, self.write_log,),
    #     ).start()
    #     return True

    # write a single log and the text-color at the log-area (text-browser)
    def write_log(self, text, color):
        log = '<span style="color: rgb{};"> &gt; {}</span>'.format(str(color), f'<strong>{text}</strong>')
        self.log_area.append(log)
