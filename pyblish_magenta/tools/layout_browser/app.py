import os
import sys
import contextlib

from PySide import QtGui, QtCore

self = sys.modules[__name__]
self._window = None


class Window(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("Layout Browser")
        self.setFixedSize(250, 300)

        body = QtGui.QWidget()
        footer = QtGui.QWidget()

        list1 = QtGui.QListWidget()
        layout = QtGui.QVBoxLayout(body)
        layout.addWidget(list1)
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(body)
        layout.addWidget(footer)

    def refresh(self, topic, root):
        pass


def show(topic, root):
    if self._window:
        self._window.close()
        del(self._window)

    root = os.path.realpath(root)

    window = Window()
    window.show()
    window.refresh(topic, root)

    self._window = window


@contextlib.contextmanager
def application():
    app = QtGui.QApplication(sys.argv)
    yield
    app.exec_()


if __name__ == '__main__':
    os.environ["PROJECTROOT"] = "C:/Users/marcus/Dropbox/projects/thedeal/"
    root = ("C:/Users/marcus/Dropbox/projects/thedeal/film"
            "/seq01/1000/work/marcus/maya")

    with application():
        show("thedeal seq01 1000", root)
