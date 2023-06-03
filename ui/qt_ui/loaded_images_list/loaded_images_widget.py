import os
from pathlib import Path

import cv2
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QAction, QFileDialog, QHBoxLayout, QLabel, QMenu, QPushButton, QVBoxLayout, QWidget,
)

from color_harmonization.main_process import ProcessThread
from color_harmonization.main_process import do_process as do_color_harmonization_process
from enums.colors import Colors
from enums.dialog_status import DialogStatus
from enums.process_status import ProcessStatus
from loaded_image_obj import LoadedImagesDict
from ui.qt_ui.harmonization_config_panel.harmonization_config_panel import HarmonizationConfigPanel
from utils.general_utils import gut_get_ext, gut_load_image, gut_replace_ext
from utils.harmonization_utils import hut_add_opaque_channel, hut_map_template_type


class LoadedImagesWidget(QWidget):
    def __init__(self, win_name, img, order, log_writer=None, parent=None):
        super(LoadedImagesWidget, self).__init__(parent)
        # the configuration for harmonization
        self.process_cfg = {
            'resize_ratio': 1.,
            'template_type': 0,
            'ref_im_fpath': None,
        }
        # the window name and the image
        self.win_name = win_name
        self.im_wh = (img.shape[1], img.shape[0],)
        # the log writer
        self.log_writer = log_writer

        # the first row (order, win-name, image-size)
        self.lbl_order = QLabel(f'[{order}] |')
        self.lbl_win_name = QLabel(self.win_name)
        self.hbox_fir = QHBoxLayout()
        self.hbox_fir.addWidget(self.lbl_order, 0)
        self.hbox_fir.addWidget(self.lbl_win_name, 1)

        # the second row (status, configurations)
        self.lbl_status_title = QLabel('Status:')
        self.lbl_status = QLabel('Loading or waiting')
        self.btn_configurate = QPushButton('Configurate')
        self.lbl_show_config = QLabel(self.config_display_text)
        self.lbl_show_config.setTextFormat(Qt.RichText)
        self.lbl_size = QLabel(self.im_size_display_text)
        self.lbl_size.setTextFormat(Qt.RichText)
        self.hbox_sec = QHBoxLayout()
        self.hbox_sec.addWidget(self.lbl_status_title, 0)
        self.hbox_sec.addWidget(self.lbl_status, 0)
        self.hbox_sec.addWidget(self.btn_configurate, 1)
        self.hbox_sec.addWidget(self.lbl_show_config, 0)
        self.hbox_sec.addWidget(self.lbl_size, 0)

        # the third row (buttons for showing images, start process, and save the results)
        self.btn_show_img = QPushButton(QIcon(QPixmap('./resource/img_search.png')), '')
        self.btn_show_img.setStyleSheet("""
            QPushButton {background-color: transparent;}
            QPushButton:pressed {background-color: rgb(226, 230, 234);}
            QPushButton:hover:!pressed {background-color: rgb(226, 230, 234);}
        """)
        self.btn_start_process = QPushButton('Start process')
        self.btn_save_processed = QPushButton('Save the processed image to...')
        self.btn_super_resolution = QPushButton('Super resolution')
        self.btn_save_processed_sr = QPushButton('Save the SR\'d image to...')
        self.hbox_thr = QHBoxLayout()
        self.hbox_thr.addWidget(self.btn_show_img, 0)
        self.hbox_thr.addWidget(self.btn_start_process, 1)
        self.hbox_thr.addWidget(self.btn_save_processed, 1)
        self.hbox_thr.addWidget(QLabel(' | '), 0)
        self.hbox_thr.addWidget(self.btn_super_resolution, 1)
        self.hbox_thr.addWidget(self.btn_save_processed_sr, 1)

        # for containing all widgets
        self.vbox_all = QVBoxLayout()
        self.vbox_all.addLayout(self.hbox_fir, 0)
        self.vbox_all.addLayout(self.hbox_sec, 0)
        self.vbox_all.addLayout(self.hbox_thr, 0)
        self.setLayout(self.vbox_all)

        # set actions of the image-showing menu-button
        menu = QMenu()
        self.action_show_orig = QAction('Show the original image', self)
        self.action_show_proc = QAction('Show the processed image', self)
        self.action_show_proc_sr = QAction('Show the processed image (after super resolution)', self)
        self.action_show_comparison_btn = QAction('Show the comparison', self)
        menu.addAction(self.action_show_orig)
        menu.addAction(self.action_show_proc)
        menu.addAction(self.action_show_proc_sr)
        menu.addAction(self.action_show_comparison_btn)
        self.btn_show_img.setMenu(menu)

        # disable all buttons from the beginning (they will be enabled until its process is done)
        self.btn_configurate.setDisabled(True)
        self.btn_show_img.setDisabled(True)
        self.btn_start_process.setDisabled(True)
        self.btn_save_processed.setDisabled(True)
        self.btn_super_resolution.setDisabled(True)
        self.btn_save_processed_sr.setDisabled(True)
        self.action_show_proc.setDisabled(True)
        self.action_show_proc_sr.setDisabled(True)
        self.action_show_comparison_btn.setDisabled(True)

        # initially change the text-color of the lbl-status
        self.process_status = ProcessStatus.LOADING
        self.lbl_status.setStyleSheet(f'color: rgb{ProcessStatus.LOADING.get_text_color()[::-1]};')
        # initialize events
        self.init_events()

    # initialize events
    def init_events(self):
        # show the original image
        self.action_show_orig.triggered.connect(lambda: cv2.imshow(f'|{self.win_name}|', LoadedImagesDict.get_original_image(self.win_name)))
        # show the processed image
        self.action_show_proc.triggered.connect(lambda: cv2.imshow(self.win_name, LoadedImagesDict.get_processed_image(self.win_name)))
        self.action_show_proc_sr.triggered.connect(lambda: cv2.imshow(self.win_name, gut_load_image(LoadedImagesDict.get_sr_out_path(self.win_name))))
        self.action_show_comparison_btn.triggered.connect(self.action_show_comparison)
        # open the configuration panel
        self.btn_configurate.clicked.connect(self.action_pop_up_configuration_panel)
        # start process (color harmonization)
        self.btn_start_process.clicked.connect(self.action_start_process)
        # apply super-resolution on the processed image
        self.btn_super_resolution.clicked.connect(self.action_super_resolution)
        # save the processed image
        self.btn_save_processed.clicked.connect(self.action_save_processed_image)
        self.btn_save_processed_sr.clicked.connect(self.action_save_processed_image_sr)

    # notify the status when the image-process is changed
    def notify_status_change(self, status):
        # update the status of the process
        self.process_status = status
        # change the text-color according to the status
        self.lbl_status.setStyleSheet(f'color: rgb{status.get_text_color()[::-1]};')
        self.lbl_status.setText(status.value)
        # enable/disable the buttons, if necessary
        self.btn_show_img.setEnabled(status == ProcessStatus.DONE or status == ProcessStatus.LOADED)
        self.btn_save_processed.setEnabled(status == ProcessStatus.DONE)
        # if the image is just loaded
        if status == ProcessStatus.LOADED:
            self.btn_configurate.setEnabled(True)
            self.btn_start_process.setEnabled(True)
            self.btn_save_processed.setEnabled(False)
            self.btn_configurate.click()
        elif status in (ProcessStatus.WAITING, ProcessStatus.PROCESSING,):
            self.btn_configurate.setEnabled(False)
            self.btn_start_process.setEnabled(False)
            self.btn_super_resolution.setEnabled(False)
            self.btn_save_processed.setEnabled(False)
            self.action_show_proc.setEnabled(False)
            self.action_show_comparison_btn.setEnabled(False)
        # if the process is done
        elif status == ProcessStatus.DONE:
            self.btn_configurate.setEnabled(True)
            self.btn_start_process.setEnabled(True)
            self.btn_super_resolution.setEnabled(True)
            self.btn_save_processed.setEnabled(True)
            self.action_show_proc.setEnabled(True)
            self.action_show_comparison_btn.setEnabled(True)
            # initially show the size of the processed image (although it's still the same as the original one)
            self.notify_size_change()

    # notify the size of the processed image is changed
    def notify_size_change(self):
        # get the new size of the processed image
        new_size = LoadedImagesDict.get_size_of_processed_image(self.win_name)
        self.btn_save_processed.setText(f'Save the processed image [{new_size[0]} x {new_size[1]}] to...')

    # pop up a panel for harmonization configuration
    def action_pop_up_configuration_panel(self):
        # show and execute the dialog
        cfg_panel = HarmonizationConfigPanel(self.win_name, **self.process_cfg)
        cfg_panel.show()
        cfg_panel.exec()
        if cfg_panel.dialog_status == DialogStatus.ACCEPTED:
            self.process_cfg['resize_ratio'] = cfg_panel.resize_ratio
            self.process_cfg['template_type'] = cfg_panel.templ_type
            self.process_cfg['ref_im_fpath'] = cfg_panel.ref_im_fpath
            self.lbl_show_config.setText(self.config_display_text)
            self.lbl_size.setText(self.im_size_display_text)
            self.log_writer(f'Configuration for <i>{self.win_name}</i> is updated.')
        elif cfg_panel.dialog_status == DialogStatus.CANCELED:
            pass

    # start the harmonization process
    def action_start_process(self):
        thread = ProcessThread(
            self,
            target=do_color_harmonization_process,
            args=(
                self.win_name,
                LoadedImagesDict.get_original_image(self.win_name),
                self,
            ),
            kwargs=self.process_cfg,
        )
        thread.signal_process_done.connect(self.singal_process_done_emitted)
        thread.start()
        return True
    
    def singal_process_done_emitted(self, process_status, msg, msg_color):
        self.log_writer(msg, msg_color)
        self.notify_status_change(process_status)
    
    # https://github.com/xinntao/Real-ESRGAN
    def action_super_resolution(self):
        self.notify_status_change(ProcessStatus.PROCESSING)
        # deal w/ paths
        saved_path = Path(LoadedImagesDict.get_save_path(self.win_name))
        sr_out_dir = str(saved_path.parent)
        sr_out_path = os.path.join(sr_out_dir, f'{saved_path.stem}_sr{saved_path.suffix}')
        # update the save-path of the sr'd image
        LoadedImagesDict.update_sr_out_path(self.win_name, sr_out_path)
        # determine the outscale
        outscale = int(1. / self.process_cfg['resize_ratio']) + 1
        # apply super resolution
        return_code = os.system(f'python ./Real-ESRGAN/inference_realesrgan.py -n RealESRGAN_x4plus -i \"{str(saved_path)}\" -o \"{sr_out_dir}\" -s {outscale} --suffix sr --fp32 ')
        if return_code == 0:
            # make sure the sr'd image has the same size as the raw one
            sr, raw = gut_load_image(sr_out_path), LoadedImagesDict.get_original_image(self.win_name)
            if sr.shape != raw.shape:
                sr = cv2.resize(sr, (raw.shape[1], raw.shape[0],))
                cv2.imwrite(sr_out_path, sr)
            sr, raw = gut_load_image(sr_out_path), LoadedImagesDict.get_original_image(self.win_name)
            self.action_show_proc_sr.setEnabled(True)
            self.log_writer(f'The SR\'d (scale={outscale}) image has been saved to <i>{sr_out_path}</i>.', Colors.LOG_PROCESS_DONE)
            self.notify_status_change(ProcessStatus.DONE)
            self.btn_super_resolution.setEnabled(False)
            self.btn_save_processed_sr.setEnabled(True)
            self.action_show_comparison_btn.setEnabled(True)
    
    # the action of saving the processed image
    def action_save_processed_image(self):
        # activate the save-file-dialog and get the filename and the file type selected by the user
        filename, file_type = QFileDialog.getSaveFileName(
            parent=self,
            caption='Save the processed image',
            filter='All (*);;JPG (*.jpg *.jpeg);;PNG (*.png);;BMP (*.bmp)'
        )
        # make sure the filename is NOT empty (the user clicked the 'save' button in the file-dialog)
        if filename != '':
            # if the type is ALL, automatically determines the extension w/ the original one
            if file_type == 'All (*)' and gut_get_ext(filename) == '':
                filename = gut_replace_ext(filename, gut_get_ext(self.win_name))
            # write the image into the file w/ the designated filename
            cv2.imwrite(filename, LoadedImagesDict.get_processed_image(self.win_name))
            # write a log
            if self.log_writer is not None:
                self.log_writer(f'The processed image <i>{self.win_name}</i> has been saved to the designated location.', Colors.LOG_IMAGE_SAVED)
    
    def action_save_processed_image_sr(self):
        # activate the save-file-dialog and get the filename and the file type selected by the user
        filename, file_type = QFileDialog.getSaveFileName(
            parent=self,
            caption='Save the SR\'d image',
            filter='All (*);;JPG (*.jpg *.jpeg);;PNG (*.png);;BMP (*.bmp)'
        )
        # make sure the filename is NOT empty (the user clicked the 'save' button in the file-dialog)
        if filename != '':
            # if the type is ALL, automatically determines the extension w/ the original one
            if file_type == 'All (*)' and gut_get_ext(filename) == '':
                filename = gut_replace_ext(filename, gut_get_ext(self.win_name))
            # write the image into the file w/ the designated filename
            cv2.imwrite(filename, gut_load_image(LoadedImagesDict.get_sr_out_path(self.win_name)))
            # write a log
            if self.log_writer is not None:
                self.log_writer(f'The SR\'d image <i>{self.win_name}</i> has been saved to the designated location.', Colors.LOG_IMAGE_SAVED)
    
    def action_show_comparison(self):
        raw = LoadedImagesDict.get_original_image(self.win_name)
        aft = LoadedImagesDict.get_sr_out_path(self.win_name)
        if aft is None:
            aft = LoadedImagesDict.get_processed_image(self.win_name)
            if aft.shape[-1] == 4:
                aft = cv2.cvtColor(aft, cv2.COLOR_BGRA2BGR)
            if aft.shape[0] < raw.shape[0]:
                d = raw.shape[0] - aft.shape[0]
                aft = np.concatenate((aft, np.zeros((d, aft.shape[1], 3,), dtype=np.uint8),), axis=0)
        else:
            aft = gut_load_image(aft)
            if aft.shape[-1] == 4:
                aft = cv2.cvtColor(aft, cv2.COLOR_BGRA2BGR)
        line = np.zeros((aft.shape[0], 2, 3,), dtype=np.uint8)
        if raw.shape[-1] == 4:
            raw = cv2.cvtColor(raw, cv2.COLOR_BGRA2BGR)
        cv2.imshow(self.win_name, np.hstack((raw, line, aft,)))


    @property
    def config_display_text(self):
        r = self.process_cfg['resize_ratio']
        t = hut_map_template_type(self.process_cfg['template_type'])
        ref = self.process_cfg['ref_im_fpath']
        return f' {"{"} ' + \
               f'Resize-ratio: <span style="color: red;"><strong>{r:.2f}</strong></span>, ' + \
               f'Template: <span style="color: red;"><strong>{t}</strong></span>{"" if t == "AUTO" else "-type"}, ' + \
               'Ref.: {}'.format('NONE' if ref is None else f'<span style="color: red;"><strong>{ref}</strong></span>') + \
               f' {"}"}'
    
    @property
    def im_size_display_text(self):
        r = self.process_cfg['resize_ratio']
        new_w = int(self.im_wh[0] * r)
        new_h = int(self.im_wh[1] * r)
        return f'| Raw: [{self.im_wh[0]:,} x {self.im_wh[1]:,}] -> ' + \
               f'Resized: [{new_w:,} x {new_h:,}] ' + \
               f'(# pixels = <span style="color: red;"><strong>{new_w * new_h:,}</strong></span>)'
