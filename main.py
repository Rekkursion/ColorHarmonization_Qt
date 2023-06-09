import sys

from PyQt5.QtWidgets import QApplication

from ui.qt_ui.main_window.main_window import MainWindow


# start the application
def start_app():
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    try:
        # start the application
        start_app()
    except BaseException as e:
        print(e)
