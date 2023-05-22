from PyQt5.QtWidgets import QAbstractItemView, QListWidget, QListWidgetItem

from ui.qt_ui.loaded_images_list.loaded_images_widget import LoadedImagesWidget


class LoadedImagesListWidget(QListWidget):
    def __init__(self, log_writer=None):
        super(LoadedImagesListWidget, self).__init__()
        self.log_writer = log_writer
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

    # push an item into this list
    def push_back(self, win_name, img):
        if img is not None:
            widget = LoadedImagesWidget(win_name, img, self.count() + 1, self.log_writer)
            item = QListWidgetItem(self)
            item.setSizeHint(widget.sizeHint())
            self.addItem(item)
            self.setItemWidget(item, widget)
            return widget

    # get all of the widgets in the list
    def get_all_widgets(self):
        return [self.itemWidget(self.item(i)) for i in range(0, self.count())]

    # get the designated widget by the corresponding window name
    def get_widget_by_win_name(self, win_name):
        # iterate all widgets in the list
        for i in range(0, self.count()):
            # get a single widget
            widget = self.itemWidget(self.item(i))
            # check whether there's a widget which has a same name or not
            if widget.win_name == win_name:
                return widget
        # not found
        return None

    # deduplicate the window-name by adding a number before the original name
    def deduplicate_win_name(self, win_name):
        new_win_name = win_name
        counter = 1
        while self.get_widget_by_win_name(new_win_name) is not None:
            counter += 1
            new_win_name = f'({counter}) {win_name}'
        return new_win_name
