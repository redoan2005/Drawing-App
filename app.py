
import sys

from PySide6 import QtWidgets as qtw
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import (
    QPainter,
    QPen,
    QColor,
    QImage,
)


class DrawingCanvas(qtw.QWidget):

    def __init__(self):
        super().__init__()

        self.setMinimumSize(600, 400)
        self.setAttribute(
            Qt.WidgetAttribute.WA_StaticContents
        )

        self.image = QImage(
            self.size(),
            QImage.Format.Format_ARGB32
        )
        self.image.fill(QColor("white"))

        self.last_point = QPoint()
        self.drawing = False

        self.pen_color = QColor("black")
        self.pen_width = 4

        self.history = []

    def save_history(self):
        self.history.append(self.image.copy())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.image)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.save_history()
            self.last_point = event.position().toPoint()
            self.drawing = True

    def mouseMoveEvent(self, event):
        if (
            self.drawing
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            current_point = event.position().toPoint()

            painter = QPainter(self.image)

            painter.setPen(
                QPen(
                    self.pen_color,
                    self.pen_width,
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                    Qt.PenJoinStyle.RoundJoin,
                )
            )

            painter.drawLine(
                self.last_point,
                current_point
            )

            painter.end()

            self.last_point = current_point
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False

    def set_color(self, color):
        if color.isValid():
            self.pen_color = color

    def set_width(self, width):
        self.pen_width = width

    def clear_canvas(self):
        self.save_history()
        self.image.fill(QColor("white"))
        self.update()

    def undo(self):
        if self.history:
            self.image = self.history.pop()
            self.update()

    def save_image(self):
        path, _ = qtw.QFileDialog.getSaveFileName(
            self,
            "Save Drawing",
            "my_drawing.png",
            "PNG Image (*.png)"
        )

        if path:
            if not path.lower().endswith(".png"):
                path += ".png"

            if self.image.save(path, "PNG"):
                qtw.QMessageBox.information(
                    self,
                    "Saved",
                    "Drawing saved successfully!"
                )
            else:
                qtw.QMessageBox.warning(
                    self,
                    "Error",
                    "Could not save the image."
                )


class DrawingApp(qtw.QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("My Drawing App")
        self.resize(850, 600)

        self.canvas = DrawingCanvas()
        self.setCentralWidget(self.canvas)

        toolbar = self.addToolBar("Drawing Tools")

        color_action = toolbar.addAction("Choose Color")
        color_action.triggered.connect(self.choose_color)

        toolbar.addSeparator()

        toolbar.addWidget(qtw.QLabel(" Brush size: "))

        self.size_box = qtw.QSpinBox()
        self.size_box.setRange(1, 40)
        self.size_box.setValue(4)
        self.size_box.valueChanged.connect(
            self.canvas.set_width
        )
        toolbar.addWidget(self.size_box)

        undo_action = toolbar.addAction("Undo")
        undo_action.triggered.connect(self.canvas.undo)

        clear_action = toolbar.addAction("Clear")
        clear_action.triggered.connect(
            self.canvas.clear_canvas
        )

        save_action = toolbar.addAction("Save")
        save_action.triggered.connect(
            self.canvas.save_image
        )

        erase_action = toolbar.addAction("Eraser")
        erase_action.triggered.connect(self.use_eraser)

    def choose_color(self):
        color = qtw.QColorDialog.getColor(
            self.canvas.pen_color,
            self,
            "Choose Drawing Color"
        )

        if color.isValid():
            self.canvas.set_color(color)

    def use_eraser(self):
        self.canvas.set_color(QColor("white"))
        self.size_box.setValue(20)


app = qtw.QApplication(sys.argv)

window = DrawingApp()
window.show()

sys.exit(app.exec())
