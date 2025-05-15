from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter

# class to define the shot in progress, made, and miss overlay
class ColorOverlay(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.Widget | Qt.FramelessWindowHint)

        self._color = QColor(0,0,0,0)


    def set_overlay_color(self, color: QColor):
        self._color = color
        self.update()

    def clear_overlay(self):
        print("Clearing overlay")
        self.set_overlay_color(QColor(0, 0, 0, 0))

    def paintEvent(self, event):
        print(f"Painting overlay with color: {self._color.getRgb()}")
        painter = QPainter(self)
        painter.fillRect(self.rect(), self._color)