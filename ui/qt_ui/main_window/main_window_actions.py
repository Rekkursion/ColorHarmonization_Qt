import os

import cv2
import numpy as np
from PIL import Image, ImageGrab
from PyQt5.QtWidgets import QFileDialog

from enums.colors import Colors
from enums.dialog_status import DialogStatus
from loaded_image_obj import LoadedImagesDict
from ui.qt_ui.url_input_dialog.url_input_dialog import URLInputDialog
from utils.general_utils import gut_get_ext, gut_load_image


# the triggered event for action-load-from-local
def action_action_open_settings_triggered(self):
    def open_settings_triggered():
        # TODO
        print('open_settings_triggered')
        pass
    return open_settings_triggered


# the triggered event for action-load-from-local
def action_load_from_local_triggered(self):
    def load_from_local_triggered():
        # open the file-dialog and get the image file(s)
        filename_list, _ = QFileDialog.getOpenFileNames(
            parent=self,
            caption='Open image(s)',
            filter='Image Files (*.jpg *.jpeg *.png *bmp)'
        )
        # iterate the filenames to do the processes
        for filename in filename_list:
            self.write_log(f'The image <i>{filename}</i> has been loaded from local.', Colors.LOG_LOAD_IMAGE)
            self.finish_image_loading(filename, gut_load_image(filename))
    return load_from_local_triggered


# the triggered event for action-load-from-url
def action_load_from_url_triggered(self):
    def load_from_url_triggered():
        # create a url-input-dialog to get the image-url
        dialog = URLInputDialog()
        # show and execute the created dialog
        dialog.show()
        dialog.exec()
        if dialog.get_status() == DialogStatus.ACCEPTED:
            win_name = dialog.get_url()
            self.write_log(f'The image <i>{win_name}</i> has been loaded from URL.', Colors.LOG_LOAD_IMAGE)
            self.finish_image_loading(win_name, dialog.get_loaded_image())
        elif dialog.get_status() == DialogStatus.ERROR:
            self.write_log(dialog.get_err_msg(), Colors.LOG_ERROR)
    return load_from_url_triggered


# the triggered event for action-load-from-clipboard
def action_load_from_clipboard_triggered(self):
    # start the process
    def start(win_name, img):
        self.clipboard_counter += 1
        self.write_log(f'The image <i>{win_name}</i> has been loaded from the clipboard.', Colors.LOG_LOAD_IMAGE)
        self.finish_image_loading(win_name, img)

    def load_from_clipboard_triggered():
        has_loaded = False
        try:
            # grab data from the clipboard
            data = ImageGrab.grabclipboard()
            # if the grabbed data is an image
            if isinstance(data, Image.Image):
                # convert the pil-img into a cv2-img
                img = np.array(data.convert('RGB'))[:, :, ::-1]
                has_loaded = True
                start(f'From clipboard {self.clipboard_counter}', img)
            # if the grabbed data is a string, it could possibly be a filename, give it a try
            elif isinstance(data, str):
                has_loaded = True
                start(f'From clipboard {self.clipboard_counter}', gut_load_image(data))
            # if the grabbed data is a list
            elif isinstance(data, list):
                # iterate the list to try getting the image(s)
                for item in data:
                    # if this item is an image
                    if isinstance(item, Image.Image):
                        # convert the pil-img into a cv2-img
                        img = np.array(item.convert('RGB'))[:, :, ::-1]
                        has_loaded = True
                        start(f'From clipboard {self.clipboard_counter}', img)
                    # if this item is a string, it could possibly be a filename, give it a try
                    elif isinstance(item, str):
                        has_loaded = True
                        start(f'From clipboard {self.clipboard_counter}', gut_load_image(item))
        except BaseException:
            self.write_log('Failed to load the image from clipboard. Please make sure the copied object is an image.', Colors.LOG_ERROR)
        # if there's nothing loaded
        if not has_loaded:
            self.write_log('No images detected in the clipboard.', Colors.LOG_WARNING)
    return load_from_clipboard_triggered


# the triggered event for saving all processed images to a directory
def action_save_all_triggered(self):
    def save_all_triggered():
        # open the dialog to let the user select an existing directory
        dir_name = QFileDialog.getExistingDirectory(parent=self, caption='Select a directory for saving')
        # iterate all loaded images
        if dir_name != '':
            cnt = 0
            for i in range(0, self.lis_imgs.count()):
                # get its window-name of a single image as the output filename
                win_name = self.lis_imgs.itemWidget(self.lis_imgs.item(i)).win_name
                # determine the extension of the output filename
                ext = gut_get_ext(win_name)
                if ext == '':
                    ext = '.jpg'
                # write it out
                img = LoadedImagesDict.get_processed_image(win_name)
                if img is not None:
                    cnt += 1
                    cv2.imwrite(os.path.join(dir_name, f'processed_{cnt}{ext}'), img)
            if cnt > 0:
                self.write_log('All processed images have been saved to the designated location.', Colors.LOG_IMAGE_SAVED)
            else:
                self.write_log('No any images which have been processed.', Colors.LOG_WARNING)
    return save_all_triggered


# the triggered-event for saving selected images to a directory
def action_save_selected_triggered(self):
    def save_selected_triggered():
        # open the dialog to let the user select an existing directory
        dir_name = QFileDialog.getExistingDirectory(parent=self, caption='Select a directory for saving')
        # iterate all loaded images
        if dir_name != '':
            cnt = 0
            for item in self.lis_imgs.selectedItems():
                # get its window-name of a single image as the output filename
                win_name = self.lis_imgs.itemWidget(item).win_name
                # determine the extension of the output filename
                ext = gut_get_ext(win_name)
                if ext == '':
                    ext = '.jpg'
                # write it out
                img = LoadedImagesDict.get_processed_image(win_name)
                if img is not None:
                    cnt += 1
                    cv2.imwrite(os.path.join(dir_name, f'processed_{cnt}{ext}'), img)
            if cnt > 0:
                self.write_log('All selected processed images have been saved to the designated location.', Colors.LOG_IMAGE_SAVED)
            else:
                self.write_log('No any images which have been processed in the selected set.', Colors.LOG_WARNING)
    return save_selected_triggered
