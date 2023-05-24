import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout,
)

from enums.dialog_status import DialogStatus


DEFAULT_SAVE_RES_DIR = './outputs/results/'
DEFAULT_SAVE_VIS_DIR = './outputs/visualizations/'


# the panel (dialog) for the global configurations
class GlobalConfigPanel(QDialog):
    save_res_dir = DEFAULT_SAVE_RES_DIR
    save_vis_dir = DEFAULT_SAVE_VIS_DIR

    def __init__(self):
        super(GlobalConfigPanel, self).__init__()

        self.dialog_status = DialogStatus.DISPLAYING
        self.setFont(QFont('Consolas', 12))
        self.setBaseSize(1500, 500)

        # the save directory for results
        self.lbl_save_res_dir = QLabel('       Save directory for results  ./')
        self.txt_save_res_dir = QLineEdit(self._remove_cur_dir(GlobalConfigPanel.save_res_dir))
        self.hbox_save_res = QHBoxLayout()
        self.hbox_save_res.addWidget(self.lbl_save_res_dir, 0)
        self.hbox_save_res.addWidget(self.txt_save_res_dir, 1)

        # the save directory for visualizations
        self.lbl_save_vis_dir = QLabel('Save directory for visualizations  ./')
        self.txt_save_vis_dir = QLineEdit(self._remove_cur_dir(GlobalConfigPanel.save_vis_dir))
        self.hbox_save_vis = QHBoxLayout()
        self.hbox_save_vis.addWidget(self.lbl_save_vis_dir, 0)
        self.hbox_save_vis.addWidget(self.txt_save_vis_dir, 1)

        # buttons
        self.btn_apply = QPushButton('Apply')
        self.btn_cancel = QPushButton('Cancel')
        self.hbox_buttons = QHBoxLayout()
        self.hbox_buttons.addWidget(self.btn_apply, 1)
        self.hbox_buttons.addWidget(self.btn_cancel, 1)
        
        # display all widgets
        self.vbox_all = QVBoxLayout()
        self.vbox_all.addWidget(QLabel('For security issue, the following directories could only be set inside the project.'), 0)
        self.vbox_all.addWidget(QLabel('==================================================================================='), 0)
        self.vbox_all.addLayout(self.hbox_save_res, 0)
        self.vbox_all.addLayout(self.hbox_save_vis, 0)
        self.vbox_all.addLayout(self.hbox_buttons, 0)
        self.setLayout(self.vbox_all)

        # initialize the events
        self.init_events()
        # force this dialog being at the top
        self.setWindowModality(Qt.ApplicationModal)
        # set the window title
        self.setWindowTitle('Global settings')

    # initialize the events
    def init_events(self):
        self.btn_apply.clicked.connect(self.action_apply)
        self.btn_cancel.clicked.connect(self.action_cancel)
    
    def action_apply(self):
        GlobalConfigPanel.save_res_dir = os.path.join('./', self.txt_save_res_dir.text())
        GlobalConfigPanel.save_vis_dir = os.path.join('./', self.txt_save_vis_dir.text())
        self.dialog_status = DialogStatus.ACCEPTED
        self.accept()
    
    def action_cancel(self):
        self.dialog_status = DialogStatus.CANCELED
        self.close()
    
    def _remove_cur_dir(self, path):
        path = str(path)
        if path.startswith('./'):
            return path[2: ]
        return path
