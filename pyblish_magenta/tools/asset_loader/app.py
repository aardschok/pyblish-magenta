import os
import sys
import contextlib

from PySide import QtGui, QtCore

import lib

self = sys.modules[__name__]
self._window = None


class Window(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("Asset Loader")

        self._root = None
        self._topic = ""
        self._representation = None

        body = QtGui.QWidget()
        footer = QtGui.QWidget()

        list1 = QtGui.QListWidget()  # Category
        list2 = QtGui.QListWidget()  # Asset
        list3 = QtGui.QListWidget()  # Subset
        list4 = QtGui.QListWidget()  # Version

        layout = QtGui.QHBoxLayout(body)
        layout.addWidget(list1)
        layout.addWidget(list2)
        layout.addWidget(list3)
        layout.addWidget(list4)
        layout.setContentsMargins(0, 0, 0, 0)

        options = QtGui.QWidget()

        closeonload_chk = QtGui.QCheckBox()
        closeonload_lbl = QtGui.QLabel("Close on load")
        closeonload_chk.setCheckState(QtCore.Qt.Checked)
        layout = QtGui.QGridLayout(options)
        layout.addWidget(closeonload_chk, 0, 0)
        layout.addWidget(closeonload_lbl, 0, 1)
        layout.setContentsMargins(0, 0, 0, 0)

        path = QtGui.QLineEdit()
        path.setReadOnly(True)
        btn_load = QtGui.QPushButton("Load")
        btn_load.setFixedWidth(80)
        btn_refresh = QtGui.QPushButton("Refresh")
        btn_refresh.setFixedWidth(80)

        layout = QtGui.QHBoxLayout(footer)
        layout.addWidget(path)
        layout.addWidget(btn_refresh)
        layout.addWidget(btn_load)
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(body)
        layout.addWidget(options, 0, QtCore.Qt.AlignRight)
        layout.addWidget(footer)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.list1 = list1
        self.list2 = list2
        self.list3 = list3
        self.list4 = list4
        self.path = path
        self.btn_load = btn_load
        self.btn_refresh = btn_refresh
        self.closeonload_chk = closeonload_chk

        btn_load.clicked.connect(self.on_load)
        btn_refresh.clicked.connect(self.on_refresh)

        list1.currentItemChanged.connect(self.on_list1changed)
        list2.currentItemChanged.connect(self.on_list2changed)
        list3.currentItemChanged.connect(self.on_list3changed)
        list4.currentItemChanged.connect(self.on_list4changed)

        self.resize(600, 250)

    def on_load(self):
        """Import asset into Maya"""
        item = self.list4.currentItem()
        root = item.data(QtCore.Qt.UserRole + 1)
        lib.load(root)

        if self.closeonload_chk.checkState():
            self.close()

    def refresh(self, root, representation):
        # Reset state
        self.list1.clear()
        self.list2.clear()
        self.list3.clear()
        self.list4.clear()
        self.path.setText("")
        self.btn_load.setEnabled(False)

        self._root = root
        self._representation = representation

        for i in list(os.path.join(self._root, p)
                      for p in os.listdir(self._root)):
            item = QtGui.QListWidgetItem(os.path.basename(i))
            item.setData(QtCore.Qt.UserRole + 1, i)
            self.list1.addItem(item)

        self.list1.setCurrentItem(self.list1.item(0))

    def on_refresh(self):
        self.refresh(self._topic, self._root, self._representation)

    def on_list1changed(self, current, previous):
        """List items of asset"""
        self.btn_load.setEnabled(False)
        self.path.setText("")
        self.list2.clear()

        if not self.list1.currentItem():
            return

        if self.list1.currentItem().text() == "No items":
            return

        root = current.data(QtCore.Qt.UserRole + 1)

        no_items = True
        for i in walk(root):
            item = QtGui.QListWidgetItem(os.path.basename(i))
            item.setData(QtCore.Qt.UserRole + 1, i)
            self.list2.addItem(item)
            no_items = False

        if no_items:
            item = QtGui.QListWidgetItem("No items")
            self.list2.addItem(item)

    def on_list2changed(self, current, previous):
        """List items of asset"""
        self.btn_load.setEnabled(False)
        self.path.setText("")
        self.list3.clear()

        if not self.list2.currentItem():
            return

        if self.list2.currentItem().text() == "No items":
            return

        root = current.data(QtCore.Qt.UserRole + 1)
        root = os.path.join(root, "publish")

        no_items = True
        for i in walk(root):
            item = QtGui.QListWidgetItem(os.path.basename(i))
            item.setData(QtCore.Qt.UserRole + 1, i)
            self.list3.addItem(item)
            no_items = False

        if no_items:
            item = QtGui.QListWidgetItem("No items")
            self.list3.addItem(item)

    def on_list3changed(self, current, previous):
        self.btn_load.setEnabled(False)
        self.path.setText("")
        self.list4.clear()

        if not self.list3.currentItem():
            return

        if self.list3.currentItem().text() == "No items":
            return

        root = current.data(QtCore.Qt.UserRole + 1)

        no_items = True
        for i in walk(root):
            item = QtGui.QListWidgetItem(os.path.basename(i))
            item.setData(QtCore.Qt.UserRole + 1, i)
            self.list4.addItem(item)
            no_items = False

        if no_items:
            item = QtGui.QListWidgetItem("No items")
            self.list4.addItem(item)

    def on_list4changed(self, current, previous):
        if not self.list4.currentItem():
            return

        if self.list4.currentItem().text() == "No items":
            return

        root = current.data(QtCore.Qt.UserRole + 1)
        if self._representation in lib.representations(root):
            self.btn_load.setEnabled(True)

        self.path.setText(root)


def show(root, representation):
    if self._window:
        self._window.close()
        del(self._window)

    root = os.path.realpath(root)

    try:
        widgets = QtGui.QApplication.topLevelWidgets()
        widgets = dict((w.objectName(), w) for w in widgets)
        parent = widgets['MayaWindow']
    except KeyError:
        parent = None

    window = Window(parent)
    window.show()
    window.refresh(root, representation)

    self._window = window


def walk(root):
    try:
        dirs = os.listdir(root)
    except:
        return

    for path in dirs:
        if path.startswith("."):
            continue

        yield os.path.join(root, path)


@contextlib.contextmanager
def application():
    app = QtGui.QApplication(sys.argv)
    yield
    app.exec_()


if __name__ == '__main__':

    # TODO: Make this more dynamic instead of hardcoded
    from pyblish_magenta.vendor import cquery
    root = "path/to/project"
    root = cquery.first_match(root,
                              selector=".Project",
                              direction=cquery.UP)
    root = os.path.join(root, "production", "assets")

    with application():
        show(root, representation=".ma")
