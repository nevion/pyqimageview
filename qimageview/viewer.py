#The MIT License (MIT)
#
#Copyright (c) 2014 Jason Newton <nevion@gmail.com>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QDesktopWidget, QLineEdit, QSlider
from PyQt5.QtGui import QImage
from PyQt5.QtCore import QPoint, QPointF, QRect, QRectF, QSize, QSizeF, pyqtSignal
from PyQt5.Qt import Qt
from enum import Enum
import os, sys

def sigint_handler(*args):
    """Handler for the SIGINT signal."""
    sys.stderr.write('\r')
    QApplication.quit()

from .widget import ImageView

main_loop_type = 'qt'

class AppImageView(ImageView):
    def __init__(self, *args, **kwargs):
        ImageView.__init__(self, *args, **kwargs)
        scene = self.scene()
        self.main_widget = None

    def mousePressEvent(self, event):
        ImageView.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        ImageView.mouseMoveEvent(self, event)
        pos = event.pos()
        scene_pos = self.mapToScene(pos)
        msg = 'ui: %d, %d  image: %d, %d'%(pos.y(), pos.x(), round(scene_pos.y()), round(scene_pos.x()))
        self.main_widget.statusBar().showMessage(msg)


class ImageViewerWindow(QMainWindow):
    def __init__(self, image, input_path):
        QMainWindow.__init__(self)
        self.image = image
        self.input_path = input_path
        self.image_view = AppImageView(self)
        self.image_view.main_widget = self
        self.statusBar().showMessage("")

        #self.resize(image.size())
        padding = self.frameGeometry().size() - self.geometry().size()
        self.resize(image.size() + padding)
        #self.resize(797, 615)

        central = QWidget(self)
        central.setObjectName("MainWindow")

        self.verticalLayout = QtWidgets.QVBoxLayout(central)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        #self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.verticalLayout.setObjectName("verticalLayout")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.image_view.sizePolicy().hasHeightForWidth())
        self.image_view.setSizePolicy(sizePolicy)
        self.image_view.setMouseTracking(True)
        self.image_view.setFocusPolicy(QtCore.Qt.NoFocus)
        self.image_view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.image_view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.image_view.setObjectName("image_view")
        self.verticalLayout.addWidget(self.image_view)

        self.setCentralWidget(central)
        self.layout().setContentsMargins(0, 0, 0, 0)

        screen = QDesktopWidget().screenGeometry(self)
        size = self.geometry()
        self.move((screen.width()-size.width())/4, (screen.height()-size.height())/4)

        self.update_view()
        self.image_view.reset()

    def hideEvent(self, event):
        QMainWindow.hide(self)

    def update_view(self):
        self.image_view.image = self.image
        self.setWindowTitle(self.make_window_title())

    def make_window_title(self):
        return os.path.basename(self.input_path)

    def keyPressEvent(self, event):
        key = event.key()
        modifier = event.modifiers()
        global main_loop_type
        if key == Qt.Key_Escape:
            if main_loop_type == 'qt':
                QApplication.quit()
            elif main_loop_type == 'ipython':
                self.hide()
                #import IPython
                #IPython.get_ipython().ask_exit()

def main():
    import argparse, errno, sys
    parser = argparse.ArgumentParser(description='image viewer')
    parser.add_argument('inputs', type=str, nargs=1, help='path to the image')
    parser.add_argument('--interactive', '-i', action='store_true', help='launch in interactive shell')
    opts = parser.parse_args()

    input_image = opts.inputs[0]
    image = QImage()
    image.load(input_image)

    app = QApplication(sys.argv)
    try:
        import signal
        signal.signal(signal.SIGINT, sigint_handler)
    except ImportError:
        pass
    window = ImageViewerWindow(image, input_image)
    window.show()

    if opts.interactive:
        global main_loop_type
        main_loop_type = 'ipython'
        from IPython import start_ipython
        start_ipython(user_ns=dict(globals(), **locals()), argv=[])
    else:
        app.exec_()

if __name__ == '__main__':
    main()
