import sys
import contextlib

from PySide import QtGui, QtCore

from pyblish_magenta.vendor import inflection
import lib

# import pyblish_magenta.tools
# print(pyblish_magenta.tools)


self = sys.modules[__name__]
self._window = None


class Window(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("Instance Creator")

        header = QtGui.QWidget()
        body = QtGui.QWidget()
        lists = QtGui.QWidget()

        name_fld = QtGui.QLineEdit()
        create_btn = QtGui.QPushButton("Create")

        layout = QtGui.QHBoxLayout(header)
        layout.addWidget(name_fld)
        layout.addWidget(create_btn)
        layout.setContentsMargins(0, 0, 0, 0)

        list1Container = QtGui.QWidget()
        list2Container = QtGui.QWidget()

        list1 = QtGui.QListWidget()
        list2 = QtGui.QListWidget()

        list1Header = QtGui.QLabel("Family")
        list2Header = QtGui.QLabel("Subset")
        subset_fld = QtGui.QLineEdit()

        layout = QtGui.QVBoxLayout(list1Container)
        layout.addWidget(list1Header)
        layout.addWidget(list1)
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtGui.QVBoxLayout(list2Container)
        layout.addWidget(list2Header)
        layout.addWidget(subset_fld)
        layout.addWidget(list2)
        layout.setContentsMargins(0, 0, 0, 0)

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

        layout = QtGui.QHBoxLayout(lists)
        layout.addWidget(list1Container)
        layout.addWidget(list2Container)
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtGui.QVBoxLayout(body)
        layout.addWidget(options, 0, QtCore.Qt.AlignLeft)
        layout.addWidget(lists)
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(header)
        layout.addWidget(body)

        self.create_btn = create_btn
        self.name_fld = name_fld
        self.subset_fld = subset_fld
        self.list1 = list1
        self.list2 = list2
        self.useselection_chk = useselection_chk
        self.autoclose_chk = autoclose_chk

        create_btn.clicked.connect(self.on_create)
        name_fld.textChanged.connect(self.on_namechanged)
        name_fld.returnPressed.connect(self.on_create)
        list1.currentItemChanged.connect(self.on_list1changed)
        list2.currentItemChanged.connect(self.on_list2changed)

        self.resize(350, 250)

    def refresh(self):
        for family in sorted(lib.families, key=lambda i: i["name"]):
            item = QtGui.QListWidgetItem(family["name"])
            item.setData(QtCore.Qt.UserRole + 1, family["subsets"])
            item.setData(QtCore.Qt.UserRole + 2, family.get("help"))
            self.list1.addItem(item)

        self.name_fld.setText("myInstance")
        self.list1.setCurrentItem(self.list1.item(0))
        self.list2.setCurrentItem(self.list2.item(0))

    def on_list1changed(self, current, previous):
        self.list2.clear()

        subsets = current.data(QtCore.Qt.UserRole + 1)
        for subset in subsets:
            item = QtGui.QListWidgetItem(subset)
            self.list2.addItem(item)

        self.list2.setCurrentItem(self.list2.item(0))

    def on_list2changed(self, current, previous):
        if not current:
            return

        self.subset_fld.setText(current.text())

    def on_create(self):
        name = self.name_fld.text()
        name = inflection.transliterate(name)
        family = self.list1.currentItem().text()
        subset = self.subset_fld.text()
        use_selection = self.useselection_chk.checkState()
        lib.create(name, family, subset, use_selection)

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
