import sys
import contextlib

from PySide import QtGui, QtCore

from pyblish_magenta.vendor import inflection

import lib

self = sys.modules[__name__]
self._window = None


class Window(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("Instance Creator")
        self.setFixedSize(250, 250)

        header = QtGui.QWidget()
        body = QtGui.QWidget()

        name_fld = QtGui.QLineEdit()
        create_btn = QtGui.QPushButton("Create")

        layout = QtGui.QHBoxLayout(header)
        layout.addWidget(name_fld)
        layout.addWidget(create_btn)
        layout.setContentsMargins(0, 0, 0, 0)

        list1 = QtGui.QListWidget()

        options = QtGui.QWidget()
        layout = QtGui.QGridLayout(options)
        layout.setContentsMargins(0, 0, 0, 0)

        useselection_chk = QtGui.QCheckBox()
        useselection_lbl = QtGui.QLabel("Use selection")
        useselection_chk.setCheckState(QtCore.Qt.Checked)
        layout.addWidget(useselection_chk, 0, 0)
        layout.addWidget(useselection_lbl, 0, 1)

        autoclose_chk = QtGui.QCheckBox()
        autoclose_lbl = QtGui.QLabel("Close after creation")
        autoclose_chk.setCheckState(QtCore.Qt.Checked)
        layout.addWidget(autoclose_chk, 1, 0)
        layout.addWidget(autoclose_lbl, 1, 1)

        layout = QtGui.QVBoxLayout(body)
        layout.addWidget(options, 0, QtCore.Qt.AlignLeft)
        layout.addWidget(list1)
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(header)
        layout.addWidget(body)

        self.create_btn = create_btn
        self.name_fld = name_fld
        self.list1 = list1
        self.useselection_chk = useselection_chk
        self.autoclose_chk = autoclose_chk

        create_btn.clicked.connect(self.on_create)
        name_fld.textChanged.connect(self.on_namechanged)
        name_fld.returnPressed.connect(self.on_create)

    def refresh(self):
        for family, defaults in sorted(lib.families.iteritems()):
            item = QtGui.QListWidgetItem(family)
            self.list1.addItem(item)

        self.list1.setCurrentItem(self.list1.item(0))
        self.name_fld.setText("myInstance")
        # self.name_fld.selectAll()
        # self.name_fld.setFocus()

    def on_create(self):
        name = self.name_fld.text()
        name = inflection.transliterate(name)
        family = self.list1.currentItem().text()
        use_selection = self.useselection_chk.checkState()
        lib.create(name, family, use_selection)

        if self.autoclose_chk.checkState():
            self.close()

    def on_namechanged(self, name):
        if name:
            self.create_btn.setEnabled(True)
        else:
            self.create_btn.setEnabled(False)


def show():
    if self._window:
        self._window.close()
        del(self._window)

    try:
        widgets = QtGui.QApplication.topLevelWidgets()
        widgets = dict((w.objectName(), w) for w in widgets)
        parent = widgets['MayaWindow']
    except KeyError:
        parent = None

    window = Window(parent)
    window.show()
    window.refresh()

    self._window = window


@contextlib.contextmanager
def application():
    app = QtGui.QApplication(sys.argv)
    yield
    app.exec_()


if __name__ == '__main__':
    with application():
        show()
