import os
import sys
import json
import contextlib

from PySide import QtGui

import lib


class Window(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("Package Loader")

        self._root = None
        self._topic = ""
        self._packages = {}
        self._representation = None

        header = QtGui.QWidget()
        body = QtGui.QWidget()
        footer = QtGui.QWidget()

        label1 = QtGui.QLabel("Package Loader")

        layout = QtGui.QHBoxLayout(header)
        layout.addWidget(label1)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        list1 = QtGui.QListWidget()
        list2 = QtGui.QListWidget()
        list3 = QtGui.QListWidget()

        list3.setEnabled(False)

        layout = QtGui.QHBoxLayout(body)
        layout.addWidget(list1)
        layout.addWidget(list2)
        layout.addWidget(list3)
        layout.setContentsMargins(0, 0, 0, 0)

        btn_load = QtGui.QPushButton("Load")
        btn_load.setFixedWidth(80)
        btn_refresh = QtGui.QPushButton("Refresh")
        btn_refresh.setFixedWidth(80)

        layout = QtGui.QHBoxLayout(footer)
        layout.addWidget(QtGui.QWidget())  # Right-aligned
        layout.addWidget(btn_refresh)
        layout.addWidget(btn_load)
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtGui.QVBoxLayout(self)
        # layout.addWidget(header)
        layout.addWidget(body)
        layout.addWidget(footer)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.list1 = list1
        self.list2 = list2
        self.list3 = list3
        self.label1 = label1
        self.btn_load = btn_load
        self.btn_refresh = btn_refresh

        btn_load.clicked.connect(self.on_load)
        btn_refresh.clicked.connect(self.on_refresh)

        list1.currentItemChanged.connect(self.on_packagechanged)
        list2.currentItemChanged.connect(self.on_versionchanged)

        self.resize(400, 250)

    def refresh(self, root, representation):
        self.list1.clear()
        self.list2.clear()
        self.list3.clear()

        packages = lib.list_packages(root)

        self._root = root
        self._packages = packages
        self._representation = representation

        for p in packages:
            item = QtGui.QListWidgetItem(p)
            self.list1.addItem(item)

        self.list1.setCurrentItem(self.list1.item(0))

        self.btn_load.setEnabled(False)

    def on_load(self):
        """Import package into Maya"""
        package = self._packages[self.list1.currentItem().text()]
        version = package["versions"][self.list2.currentItem().text()]
        lib.load_package(version, self._representation)
        self.close()

    def on_refresh(self):
        self.refresh(self._root)

    def on_packagechanged(self, current, previous):
        """List versions of package"""
        try:
            package = self._packages[current.text()]
        except AttributeError:
            # No current item
            return

        self.list2.clear()

        for v in sorted(package["versions"]):
            item = QtGui.QListWidgetItem(v)
            self.list2.addItem(item)

    def on_versionchanged(self, current, previous):
        """List contents of package"""
        self.list3.clear()

        try:
            package = self._packages[self.list1.currentItem().text()]
        except AttributeError:
            # No current item
            return

        version = package["versions"][self.list2.currentItem().text()]
        pkg = next(f for f in os.listdir(version)
                   if f.endswith(".pkg"))

        with open(os.path.join(version, pkg)) as f:
            pkg = json.load(f)

        for subset, version in pkg.iteritems():
            item = QtGui.QListWidgetItem("%s (%s)" % (subset, version))
            self.list3.addItem(item)

        self.btn_load.setEnabled(True)


def show(root, representation):
    self = sys.modules[__name__]

    try:
        widgets = QtGui.QApplication.topLevelWidgets()
        widgets = dict((w.objectName(), w) for w in widgets)
        parent = widgets['MayaWindow']
    except KeyError:
        parent = None

    self.window = Window(parent)
    self.window.refresh(root, representation)
    self.window.show()


@contextlib.contextmanager
def application():
    app = QtGui.QApplication(sys.argv)
    yield
    app.exec_()


if __name__ == '__main__':
    root = ("C:/Users/marcus/Dropbox/projects/thedeal/film/"
            "seq01/1000/work/marcus/maya")

    with application():
        show(root, ".abc")
