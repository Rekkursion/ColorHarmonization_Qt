import os

import cv2
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtWidgets import (
    QButtonGroup, QDialog, QGridLayout, QHBoxLayout, QLabel, QPushButton, QRadioButton, QSlider, QVBoxLayout,
)

from enums.dialog_status import DialogStatus
from utils.general_utils import gut_load_image
from utils.harmonization_utils import hut_map_template_type


# the panel (dialog) for the configuration of a harmonization process
class HarmonizationConfigPanel(QDialog):
    """
        txt_url:    the line-edit for entering the text of url
        btn_apply:  the push-button for applying the entered text of url
        btn_reset:  the push-button for resetting (clearing) the line-edit for entering the text of url
        btn_cancel: the push-button for cancelling
    """
    def __init__(self, win_name, **kwargs):
        super(HarmonizationConfigPanel, self).__init__()
        
        self.resize_ratio = kwargs.get('resize_ratio', 1.)
        self.templ_type = kwargs.get('template_type', 0)

        self.dialog_status = DialogStatus.DISPLAYING
        self.setFont(QFont('Consolas', 12))
        self.setBaseSize(1600, 800)

        # the template types (radio buttons)
        templ_icons = gut_load_image('./resource/template_types.png')
        h, w = templ_icons.shape[: 2]
        self.grid_icons = QGridLayout()
        self.grp_icons = QButtonGroup()
        for k in range(7):
            icon_fpath = f'./resource/template_type_{k}_{hut_map_template_type(k)}.png'
            if not os.path.exists(icon_fpath):
                y = (k // 4) * (h // 2)
                x = (k % 4) * (w // 4)
                icon = templ_icons[y: y + h // 2, x: x + w // 4, ...]
                cv2.imwrite(icon_fpath, icon)
            rdb_template_type = QRadioButton()
            rdb_template_type.setIcon(QIcon(QPixmap(icon_fpath).scaled(155, 160, Qt.KeepAspectRatio)))
            rdb_template_type.setIconSize(QSize(w // 4 // 2, h // 2 // 2,))
            if k == self.templ_type:
                rdb_template_type.setChecked(True)
            self.grp_icons.addButton(rdb_template_type, k)
            self.grid_icons.addWidget(rdb_template_type, k // 4, k % 4)

        # the slider for resize ratio
        self.lbl_slider = QLabel('Resize ratio ')
        self.sld_resize_ratio = QSlider(self)
        self.sld_resize_ratio.setOrientation(1)
        self.sld_resize_ratio.setTickPosition(QSlider.TicksBelow)
        self.sld_resize_ratio.setRange(1, 20)
        self.sld_resize_ratio.setSingleStep(1)
        self.sld_resize_ratio.setTickInterval(20)
        self.sld_resize_ratio.setValue(int(self.resize_ratio * 20.))
        self.lbl_show_slider_value = QLabel(f' {self.resize_ratio:.2f}')
        self.hbox_slider = QHBoxLayout()
        self.hbox_slider.addWidget(self.lbl_slider, 0)
        self.hbox_slider.addWidget(self.sld_resize_ratio, 1)
        self.hbox_slider.addWidget(self.lbl_show_slider_value, 0)

        # buttons
        self.btn_apply = QPushButton('Apply')
        self.btn_cancel = QPushButton('Cancel')
        self.hbox_buttons = QHBoxLayout()
        self.hbox_buttons.addWidget(self.btn_apply, 1)
        self.hbox_buttons.addWidget(self.btn_cancel, 1)

        # the pixmap for displaying the loaded image
        self.lbl_display_im = QLabel()
        pixm_im = QPixmap(win_name)
        pixm_im = pixm_im.scaled(300, 300, Qt.KeepAspectRatio)
        self.lbl_display_im.setPixmap(pixm_im)
        
        # display all widgets
        self.vbox_all = QVBoxLayout()
        self.vbox_all.addWidget(QLabel(win_name), 1)
        self.vbox_all.addWidget(self.lbl_display_im, 0)
        self.vbox_all.addLayout(self.grid_icons, 1)
        self.vbox_all.addLayout(self.hbox_slider, 1)
        self.vbox_all.addLayout(self.hbox_buttons, 1)
        self.setLayout(self.vbox_all)

        # initialize the events
        self.init_events()
        # force this dialog being at the top
        self.setWindowModality(Qt.ApplicationModal)
        # set the window title
        self.setWindowTitle('Harmonization configuration')

    # initialize the events
    def init_events(self):
        self.sld_resize_ratio.valueChanged.connect(self.action_set_resize_ratio)
        self.btn_apply.clicked.connect(self.action_apply)
        self.btn_cancel.clicked.connect(self.action_cancel)
    
    def action_set_resize_ratio(self):
        ratio = self.sld_resize_ratio.value() / 20.
        self.resize_ratio = ratio
        self.lbl_show_slider_value.setText(f' {ratio:.2f}')
    
    def action_apply(self):
        self.resize_ratio = self.sld_resize_ratio.value() / 20.
        self.templ_type = self.grp_icons.checkedId()
        self.dialog_status = DialogStatus.ACCEPTED
        self.accept()
    
    def action_cancel(self):
        self.dialog_status = DialogStatus.CANCELED
        self.close()
