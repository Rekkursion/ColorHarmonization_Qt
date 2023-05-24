import socket
import urllib
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image, UnidentifiedImageError
from PIL.GifImagePlugin import GifImageFile
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from enums.dialog_status import DialogStatus
from utils.general_utils import gut_load_image


# the dialog for the user to input the image-URL
class URLInputDialog(QDialog):
    """
        txt_url:    the line-edit for entering the text of url
        btn_apply:  the push-button for applying the entered text of url
        btn_reset:  the push-button for resetting (clearing) the line-edit for entering the text of url
        btn_cancel: the push-button for cancelling
    """
    def __init__(self):
        super(URLInputDialog, self).__init__()
        # load the UI
        uic.loadUi('./ui/qt_ui/url_input_dialog/url_input_dialog.ui', self)
        # initialize the events
        self.init_events()
        # force this dialog being at the top
        self.setWindowModality(Qt.ApplicationModal)
        # the loaded image, if any
        self.loaded_img = None
        self.cache_fname = None
        # the error message, if needs
        self.err_msg = ''
        # the status of the dialog
        self.dialog_status = DialogStatus.DISPLAYING
        # set the window title
        self.setWindowTitle('URL Input Dialog')

    # initialize the events
    def init_events(self):
        # apply the entered url
        self.btn_apply.clicked.connect(lambda: {self.download_image_from_url(self.txt_url.text()), self.accept()})
        # reset the line-edit which is used to enter the url
        self.btn_reset.clicked.connect(lambda: {self.txt_url.setText(''), self.txt_url.setFocus()})
        # cancel the whole action
        self.btn_cancel.clicked.connect(lambda: self.cancel())

    # download the image from the designated url-text
    def download_image_from_url(self, url):
        try:
            # the pre-defined filename in the cache directory (minus 1 due to .gitkeep)
            num_downloaded_before = sum(1 for x in Path('./resource/dl_img').glob('*') if x.is_file()) - 1
            self.cache_fname = f'./resource/dl_img/url-loaded_{num_downloaded_before:03d}_{Path(url).name}'
            # download the file through the designated url
            urllib.request.urlretrieve(url, self.cache_fname)
            # open the file as an image
            img = gut_load_image(self.cache_fname)
            # if the loaded image is a gif, raise an error because the gif format is NOT supported
            if isinstance(Image.fromarray(img), GifImageFile):
                raise UnidentifiedImageError
            # set the image as the loaded one
            self.loaded_img = np.asarray(img)
            # change the dialog-status to accepted
            self.dialog_status = DialogStatus.ACCEPTED
        # some possible errors due to the network-related things (url, socket, http, etc.)
        except (AttributeError, socket.error, urllib.error.URLError, urllib.error.HTTPError, urllib.error.ContentTooShortError):
            self.err_msg = 'Image downloading failed.'
            # change the dialog-status to error
            self.dialog_status = DialogStatus.ERROR
        # some possible errors since the loaded image may be with an unknown or unsupported format/content
        except (ValueError, UnidentifiedImageError, OSError):
            self.err_msg = 'Unknown image file. Please aware that GIF files are NOT supported.'
            # change the dialog-status to error
            self.dialog_status = DialogStatus.ERROR

    # cancel this dialog
    def cancel(self):
        self.dialog_status = DialogStatus.CANCELED
        self.close()

    # get the user-entered url
    def get_url(self):
        return self.txt_url.text()

    # get the loaded image if any
    def get_loaded_image(self):
        return self.loaded_img

    # get the error message if some error happened, or it will return an empty string
    def get_err_msg(self):
        return self.err_msg

    # get the status of this dialog
    def get_status(self):
        return self.dialog_status
