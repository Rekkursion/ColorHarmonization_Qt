from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QTextBrowser


class LogArea(QTextBrowser):
    def __init__(self):
        super(LogArea, self).__init__()
        self.setFont(QFont('Consolas', 10))
        self.setFixedHeight(160)

    def append(self, p_str):
        super(LogArea, self).append(p_str)
        # to keep the text-browser always at the bottom
        self.moveCursor(self.textCursor().End)
